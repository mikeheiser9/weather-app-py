"""Health service: cheap, concurrent per-dependency probes.

Mongo (system of record) and the upstream provider are treated as critical;
Redis is a non-critical cache, so its absence degrades but does not fail health.
Probes run concurrently with short timeouts and never run heavy upstream calls.
"""

from __future__ import annotations

import asyncio

import structlog

from app.clients.open_meteo import OpenMeteoClient
from app.clients.resilience import Resilience
from app.db_types import MongoDatabase
from app.models.common import (
    DependencyHealth,
    DependencyStatus,
    HealthResponse,
)
from app.repositories.cache import WeatherCache

logger = structlog.get_logger(__name__)


class HealthService:
    def __init__(
        self,
        cache: WeatherCache,
        db: MongoDatabase,
        client: OpenMeteoClient,
        resilience: Resilience,
    ) -> None:
        self._cache = cache
        self._db = db
        self._client = client
        self._resilience = resilience

    async def _mongo_ok(self) -> bool:
        try:
            await self._db.command("ping")
        except Exception as exc:
            logger.warning("mongo_ping_failed", error=str(exc))
            return False
        return True

    async def check(self) -> HealthResponse:
        redis_ok, mongo_ok, upstream_ok = await asyncio.gather(
            self._cache.ping(),
            self._mongo_ok(),
            self._client.reachable(),
        )

        redis = DependencyHealth(
            status=DependencyStatus.OK if redis_ok else DependencyStatus.DEGRADED,
            detail=None if redis_ok else "cache unavailable, serving live",
        )
        mongo = DependencyHealth(
            status=DependencyStatus.OK if mongo_ok else DependencyStatus.DOWN,
        )
        upstream = DependencyHealth(
            status=DependencyStatus.OK if upstream_ok else DependencyStatus.DOWN,
        )

        if mongo.status is DependencyStatus.DOWN or upstream.status is DependencyStatus.DOWN:
            overall = DependencyStatus.DOWN
        elif redis.status is DependencyStatus.DEGRADED:
            overall = DependencyStatus.DEGRADED
        else:
            overall = DependencyStatus.OK

        return HealthResponse(
            status=overall,
            redis=redis,
            mongo=mongo,
            upstream=upstream,
            breakers=self._resilience.breaker_states(),
        )
