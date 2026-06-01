"""Redis-backed weather cache.

Redis is an ephemeral optimization, never the system of record. Every operation
degrades gracefully: if Redis is unavailable the cache reports a miss (reads) or
silently skips (writes) and logs a warning, so the API still serves live data.
"""

from __future__ import annotations

import structlog
from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.models.weather import WeatherResponse

logger = structlog.get_logger(__name__)


class WeatherCache:
    """Stores normalized weather responses keyed by coordinates and units."""

    def __init__(self, redis: Redis | None, ttl_seconds: int) -> None:
        self._redis = redis
        self._ttl = ttl_seconds

    async def get(self, key: str) -> WeatherResponse | None:
        """Return a cached response, or None on miss or any Redis failure."""
        if self._redis is None:
            return None
        try:
            raw = await self._redis.get(key)
        except (RedisError, OSError) as exc:
            logger.warning("cache_get_failed", error=str(exc))
            return None
        if raw is None:
            return None
        try:
            return WeatherResponse.model_validate_json(raw)
        except ValidationError as exc:
            logger.warning("cache_decode_failed", error=str(exc))
            return None

    async def set(self, key: str, value: WeatherResponse) -> None:
        """Store a response with the configured TTL. Never raises."""
        if self._redis is None:
            return
        try:
            await self._redis.set(key, value.model_dump_json(), ex=self._ttl)
        except (RedisError, OSError) as exc:
            logger.warning("cache_set_failed", error=str(exc))

    async def ping(self) -> bool:
        """Lightweight reachability check for /health."""
        if self._redis is None:
            return False
        try:
            return bool(await self._redis.ping())
        except (RedisError, OSError):
            return False
