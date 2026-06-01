"""FastAPI dependency injection.

Shared singletons (settings, http client, redis, mongo, resilience, upstream
client, cache) are created once in the app lifespan and stored on ``app.state``.
Lightweight repositories and services are assembled per request from those
singletons. Using Annotated aliases keeps router signatures clean and typed.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request

from app.clients.open_meteo import OpenMeteoClient
from app.clients.resilience import Resilience
from app.config import Settings
from app.db_types import MongoDatabase
from app.errors import MissingClientIdError
from app.repositories.cache import WeatherCache
from app.repositories.favorites_repo import FavoritesRepository
from app.repositories.history_repo import HistoryRepository
from app.services.favorites_service import FavoritesService
from app.services.health_service import HealthService
from app.services.history_service import HistoryService
from app.services.weather_service import WeatherService

_CLIENT_ID_HEADER = "X-Client-Id"


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_weather_cache(request: Request) -> WeatherCache:
    cache: WeatherCache = request.app.state.weather_cache
    return cache


def get_resilience(request: Request) -> Resilience:
    resilience: Resilience = request.app.state.resilience
    return resilience


def get_open_meteo(request: Request) -> OpenMeteoClient:
    client: OpenMeteoClient = request.app.state.open_meteo
    return client


def get_db(request: Request) -> MongoDatabase:
    db: MongoDatabase = request.app.state.db
    return db


SettingsDep = Annotated[Settings, Depends(get_settings)]
WeatherCacheDep = Annotated[WeatherCache, Depends(get_weather_cache)]
ResilienceDep = Annotated[Resilience, Depends(get_resilience)]
OpenMeteoDep = Annotated[OpenMeteoClient, Depends(get_open_meteo)]
DbDep = Annotated[MongoDatabase, Depends(get_db)]


def get_favorites_repo(db: DbDep) -> FavoritesRepository:
    return FavoritesRepository(db)


def get_history_repo(db: DbDep, settings: SettingsDep) -> HistoryRepository:
    return HistoryRepository(db, settings.history_max_items)


FavoritesRepoDep = Annotated[FavoritesRepository, Depends(get_favorites_repo)]
HistoryRepoDep = Annotated[HistoryRepository, Depends(get_history_repo)]


def get_weather_service(
    client: OpenMeteoDep,
    cache: WeatherCacheDep,
    history: HistoryRepoDep,
    settings: SettingsDep,
) -> WeatherService:
    return WeatherService(client, cache, history, settings)


def get_favorites_service(repo: FavoritesRepoDep) -> FavoritesService:
    return FavoritesService(repo)


def get_history_service(repo: HistoryRepoDep) -> HistoryService:
    return HistoryService(repo)


def get_health_service(
    cache: WeatherCacheDep,
    db: DbDep,
    client: OpenMeteoDep,
    resilience: ResilienceDep,
) -> HealthService:
    return HealthService(cache, db, client, resilience)


WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
FavoritesServiceDep = Annotated[FavoritesService, Depends(get_favorites_service)]
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]


def _validate_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def require_client_id(
    x_client_id: Annotated[str | None, Header(alias=_CLIENT_ID_HEADER)] = None,
) -> str:
    """Require a valid UUID client id for favorites/history endpoints."""
    if not x_client_id or not _validate_uuid(x_client_id):
        raise MissingClientIdError()
    return x_client_id


def optional_client_id(
    x_client_id: Annotated[str | None, Header(alias=_CLIENT_ID_HEADER)] = None,
) -> str | None:
    """Accept an optional valid client id (used by /weather for history)."""
    if x_client_id and _validate_uuid(x_client_id):
        return x_client_id
    return None


ClientIdDep = Annotated[str, Depends(require_client_id)]
OptionalClientIdDep = Annotated[str | None, Depends(optional_client_id)]
