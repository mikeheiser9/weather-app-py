"""Per-upstream resilience: tenacity retry wrapped by a pybreaker breaker.

Each logical upstream operation is executed as a single circuit-breaker call.
Inside that call, tenacity retries only transient failures (timeouts,
connection errors, 5xx) with exponential backoff and jitter. Non-transient
errors (4xx) are neither retried nor counted toward the breaker. When the
breaker is open the call fails fast with a structured 503.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeVar

import pybreaker
import structlog
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.config import Settings
from app.errors import UpstreamError, UpstreamUnavailableError
from app.models.common import BreakerState

logger = structlog.get_logger(__name__)

T = TypeVar("T")

UPSTREAMS: tuple[str, ...] = ("geocoding", "forecast", "air_quality")

_STATE_MAP: dict[str, BreakerState] = {
    pybreaker.STATE_CLOSED: BreakerState.CLOSED,
    pybreaker.STATE_OPEN: BreakerState.OPEN,
    pybreaker.STATE_HALF_OPEN: BreakerState.HALF_OPEN,
}


class TransientUpstreamError(Exception):
    """Retryable upstream failure (timeout, connection error, or 5xx)."""


class _LoggingListener(pybreaker.CircuitBreakerListener):
    """Logs circuit breaker state transitions."""

    def state_change(
        self,
        cb: pybreaker.CircuitBreaker,
        old_state: pybreaker.CircuitBreakerState | None,
        new_state: pybreaker.CircuitBreakerState | None,
    ) -> None:
        logger.warning(
            "circuit_breaker_state_change",
            breaker=cb.name,
            old_state=old_state.name if old_state else None,
            new_state=new_state.name if new_state else None,
        )


class Resilience:
    """Holds one circuit breaker per upstream and runs calls through retry."""

    def __init__(self, settings: Settings) -> None:
        self._max_attempts = settings.retry_max_attempts
        self._initial_backoff = settings.retry_initial_backoff
        self._max_backoff = settings.retry_max_backoff
        self._breakers: dict[str, pybreaker.CircuitBreaker] = {
            name: pybreaker.CircuitBreaker(
                fail_max=settings.breaker_fail_max,
                reset_timeout=settings.breaker_reset_timeout,
                exclude=[lambda exc: not isinstance(exc, TransientUpstreamError)],
                listeners=[_LoggingListener()],
                name=name,
            )
            for name in UPSTREAMS
        }

    def breaker_states(self) -> dict[str, BreakerState]:
        """Return the current state of every breaker for /health."""
        return {
            name: _STATE_MAP.get(breaker.current_state, BreakerState.CLOSED)
            for name, breaker in self._breakers.items()
        }

    def _before_sleep(self, upstream: str) -> Callable[[RetryCallState], None]:
        def _log(state: RetryCallState) -> None:
            logger.warning(
                "upstream_retry",
                upstream=upstream,
                attempt=state.attempt_number,
            )

        return _log

    async def _retry(self, upstream: str, func: Callable[[], Awaitable[T]]) -> T:
        retrying: AsyncRetrying = AsyncRetrying(
            retry=retry_if_exception_type(TransientUpstreamError),
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_random_exponential(multiplier=self._initial_backoff, max=self._max_backoff),
            before_sleep=self._before_sleep(upstream),
            reraise=True,
        )
        return await retrying(func)

    async def call(self, upstream: str, func: Callable[[], Awaitable[T]]) -> T:
        """Run ``func`` for ``upstream`` through the breaker and retry policy.

        The synchronous ``calling()`` context manager is used (pybreaker's
        ``call_async`` requires tornado): it checks the open state on enter and
        records success or failure on exit while the awaited body runs inside.
        """
        breaker = self._breakers[upstream]
        try:
            with breaker.calling():
                return await self._retry(upstream, func)
        except pybreaker.CircuitBreakerError as exc:
            logger.warning("circuit_open_fast_fail", upstream=upstream)
            raise UpstreamUnavailableError() from exc
        except TransientUpstreamError as exc:
            raise UpstreamError() from exc
