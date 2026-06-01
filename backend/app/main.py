"""FastAPI application factory and lifespan wiring.

Shared resources (httpx client, Redis, MongoDB, resilience, upstream client,
cache) are created once on startup and stored on ``app.state`` for dependency
injection, then cleanly closed on shutdown.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from app.clients.open_meteo import OpenMeteoClient
from app.clients.resilience import Resilience
from app.config import Settings, get_settings
from app.db_types import MongoClient
from app.errors import register_exception_handlers
from app.logging import configure_logging
from app.middleware import RequestContextMiddleware
from app.repositories.cache import WeatherCache
from app.repositories.favorites_repo import FavoritesRepository
from app.repositories.history_repo import HistoryRepository
from app.routers import favorites, health, history, weather

logger = structlog.get_logger(__name__)


def _build_http_client(settings: Settings) -> httpx.AsyncClient:
    timeout = httpx.Timeout(
        connect=settings.http_connect_timeout,
        read=settings.http_read_timeout,
        write=settings.http_read_timeout,
        pool=settings.http_connect_timeout,
    )
    return httpx.AsyncClient(timeout=timeout)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings)

    http_client = _build_http_client(settings)
    redis: Redis = Redis.from_url(settings.redis_url)
    mongo_client: MongoClient = AsyncIOMotorClient(
        settings.mongo_url,
        serverSelectionTimeoutMS=2000,
        uuidRepresentation="standard",
    )
    db = mongo_client[settings.mongo_db_name]
    resilience = Resilience(settings)

    app.state.http_client = http_client
    app.state.redis = redis
    app.state.mongo_client = mongo_client
    app.state.db = db
    app.state.resilience = resilience
    app.state.open_meteo = OpenMeteoClient(http_client, settings, resilience)
    app.state.weather_cache = WeatherCache(redis, settings.cache_ttl_seconds)

    try:
        await FavoritesRepository(db).ensure_indexes()
        await HistoryRepository(db, settings.history_max_items).ensure_indexes()
    except Exception as exc:
        logger.warning("index_creation_failed", error=str(exc))

    logger.info("app_started", env=settings.app_env)
    try:
        yield
    finally:
        await http_client.aclose()
        try:
            await redis.aclose()
        except Exception as exc:
            logger.warning("redis_close_failed", error=str(exc))
        mongo_client.close()
        logger.info("app_stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="Weather Proxy",
        version="0.1.0",
        summary="Production-grade weather proxy over Open-Meteo.",
        lifespan=lifespan,
    )
    app.state.settings = settings

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-Id"],
    )

    register_exception_handlers(app)

    app.include_router(weather.router)
    app.include_router(health.router)
    app.include_router(favorites.router)
    app.include_router(history.router)

    return app


app = create_app()
