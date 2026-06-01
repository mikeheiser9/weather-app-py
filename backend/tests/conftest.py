"""Shared test fixtures, fakes, and Open-Meteo sample payloads.

The FastAPI app is built and its shared singletons are injected directly onto
``app.state`` (the lifespan is not run under the ASGI test transport). Redis is
faked with fakeredis, MongoDB with mongomock-motor, and Open-Meteo is mocked
with respx. The real Open-Meteo API is never contacted.
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
import pytest_asyncio
from app.clients.open_meteo import OpenMeteoClient
from app.clients.resilience import Resilience
from app.config import Settings
from app.main import create_app
from app.repositories.cache import WeatherCache
from fakeredis import aioredis as fake_aioredis
from httpx import ASGITransport
from mongomock_motor import AsyncMongoMockClient

from tests.samples import (
    AQ_URL,
    FORECAST_URL,
    GEO_URL,
    aqi_payload,
    forecast_payload,
    geo_payload,
    make_settings,
)


@dataclass
class Harness:
    """Bundle of the app, an HTTP client, and the injected dependencies."""

    app: Any
    client: httpx.AsyncClient
    redis: Any
    db: Any
    settings: Settings
    open_meteo: OpenMeteoClient
    resilience: Resilience


@asynccontextmanager
async def harness_cm(
    *,
    redis: Any | None = None,
    **settings_overrides: Any,
) -> AsyncIterator[Harness]:
    settings = make_settings(**settings_overrides)
    redis = redis if redis is not None else fake_aioredis.FakeRedis()
    db: Any = AsyncMongoMockClient()[settings.mongo_db_name]
    http_client = httpx.AsyncClient()
    resilience = Resilience(settings)
    open_meteo = OpenMeteoClient(http_client, settings, resilience)

    app = create_app(settings)
    app.state.settings = settings
    app.state.redis = redis
    app.state.db = db
    app.state.resilience = resilience
    app.state.open_meteo = open_meteo
    app.state.weather_cache = WeatherCache(redis, settings.cache_ttl_seconds)

    transport = ASGITransport(app=app)
    test_client = httpx.AsyncClient(transport=transport, base_url="http://test")
    try:
        yield Harness(
            app=app,
            client=test_client,
            redis=redis,
            db=db,
            settings=settings,
            open_meteo=open_meteo,
            resilience=resilience,
        )
    finally:
        await test_client.aclose()
        await http_client.aclose()
        with contextlib.suppress(Exception):
            await redis.aclose()


@pytest_asyncio.fixture
async def harness() -> AsyncIterator[Harness]:
    async with harness_cm() as instance:
        yield instance


@pytest.fixture
def make_harness() -> Callable[..., Any]:
    """Return the harness context-manager factory for custom-settings tests."""
    return harness_cm


@pytest.fixture
def urls() -> SimpleNamespace:
    return SimpleNamespace(geo=GEO_URL, forecast=FORECAST_URL, aqi=AQ_URL)


@pytest.fixture
def samples() -> SimpleNamespace:
    return SimpleNamespace(
        geo=geo_payload,
        forecast=forecast_payload,
        aqi=aqi_payload,
    )
