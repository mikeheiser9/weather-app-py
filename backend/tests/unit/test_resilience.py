"""Unit tests for retry and circuit-breaker behavior."""

from __future__ import annotations

import pytest
from app.clients.resilience import Resilience, TransientUpstreamError
from app.errors import UpstreamError, UpstreamUnavailableError
from app.models.common import BreakerState

from tests.samples import make_settings


async def test_retries_transient_then_succeeds() -> None:
    resilience = Resilience(make_settings(retry_max_attempts=3))
    calls = {"n": 0}

    async def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise TransientUpstreamError("boom")
        return "ok"

    result = await resilience.call("forecast", flaky)
    assert result == "ok"
    assert calls["n"] == 3


async def test_does_not_retry_non_transient() -> None:
    resilience = Resilience(make_settings(retry_max_attempts=3))
    calls = {"n": 0}

    async def bad_request() -> str:
        calls["n"] += 1
        raise UpstreamError("4xx")

    with pytest.raises(UpstreamError):
        await resilience.call("forecast", bad_request)
    assert calls["n"] == 1
    assert resilience.breaker_states()["forecast"] == BreakerState.CLOSED


async def test_breaker_opens_and_fast_fails() -> None:
    resilience = Resilience(make_settings(retry_max_attempts=1, breaker_fail_max=2))
    calls = {"n": 0}

    async def always_fails() -> str:
        calls["n"] += 1
        raise TransientUpstreamError("down")

    # First transient failure surfaces as a 502; the second trips the breaker
    # and fast-fails as a 503.
    with pytest.raises(UpstreamError):
        await resilience.call("forecast", always_fails)
    with pytest.raises(UpstreamUnavailableError):
        await resilience.call("forecast", always_fails)

    assert resilience.breaker_states()["forecast"] == BreakerState.OPEN

    # With the breaker open, the next call fast-fails without invoking func.
    calls_before = calls["n"]
    with pytest.raises(UpstreamUnavailableError):
        await resilience.call("forecast", always_fails)
    assert calls["n"] == calls_before
