"""Weather orchestration: cache, geocode, forecast + air quality, normalize.

This is the only place the full request flow is assembled. Air quality is
treated as best-effort: a forecast failure fails the request, but an air-quality
failure degrades to a response without the AQI panel. History recording never
fails the weather response.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import structlog

from app.clients.open_meteo import OpenMeteoClient
from app.config import Settings
from app.domain.cache_key import build_weather_cache_key
from app.domain.normalize import normalize_weather
from app.errors import BadRequestError
from app.models.common import Units
from app.models.weather import ResolvedLocation, WeatherResponse
from app.repositories.cache import WeatherCache
from app.repositories.history_repo import HistoryRepository

logger = structlog.get_logger(__name__)


class WeatherService:
    """Resolve a city and return a normalized, optionally cached, weather payload."""

    def __init__(
        self,
        client: OpenMeteoClient,
        cache: WeatherCache,
        history: HistoryRepository,
        settings: Settings,
    ) -> None:
        self._client = client
        self._cache = cache
        self._history = history
        self._settings = settings

    async def search_locations(self, query: str, count: int) -> list[ResolvedLocation]:
        """Return candidate locations for search typeahead (never raises on empty)."""
        cleaned = query.strip()
        if not cleaned:
            return []
        return await self._client.geocode_search(cleaned, count)

    async def get_weather(
        self,
        units: Units,
        client_id: str | None,
        city: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        name: str | None = None,
    ) -> WeatherResponse:
        location = await self._resolve_location(city, latitude, longitude, name)
        query_label = city if city else location.name
        cache_key = build_weather_cache_key(
            location.latitude,
            location.longitude,
            units,
            self._settings.cache_coord_precision,
        )

        cached = await self._cache.get(cache_key)
        if cached is not None:
            logger.info("cache_lookup", cache="hit", key=cache_key)
            await self._record_history(client_id, query_label, location, units)
            return cached.model_copy(update={"cache": True})
        logger.info("cache_lookup", cache="miss", key=cache_key)

        forecast_data, air_quality_data = await self._fetch_upstreams(
            location.latitude, location.longitude, units
        )

        response = normalize_weather(
            location=location,
            forecast=forecast_data,
            air_quality=air_quality_data,
            units=units,
            fetched_at=datetime.now(UTC).isoformat(),
            cache=False,
        )

        await self._cache.set(cache_key, response)
        await self._record_history(client_id, query_label, location, units)
        return response

    async def _resolve_location(
        self,
        city: str | None,
        latitude: float | None,
        longitude: float | None,
        name: str | None = None,
    ) -> ResolvedLocation:
        if city:
            return await self._client.geocode(city)
        if latitude is not None and longitude is not None:
            return ResolvedLocation(
                name=name.strip() if name and name.strip() else "Current location",
                latitude=latitude,
                longitude=longitude,
            )
        raise BadRequestError("Provide either 'city' or both 'lat' and 'lon'.")

    async def _fetch_upstreams(
        self,
        latitude: float,
        longitude: float,
        units: Units,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        results = await asyncio.gather(
            self._client.forecast(latitude, longitude, units),
            self._client.air_quality(latitude, longitude),
            return_exceptions=True,
        )
        forecast_result, air_quality_result = results

        if isinstance(forecast_result, BaseException):
            raise forecast_result

        if isinstance(air_quality_result, BaseException):
            logger.warning("air_quality_unavailable", error=str(air_quality_result))
            return forecast_result, None

        return forecast_result, air_quality_result

    async def _record_history(
        self,
        client_id: str | None,
        city: str,
        location: ResolvedLocation,
        units: Units,
    ) -> None:
        if not client_id:
            return
        try:
            await self._history.record(client_id, city, location, units)
        except Exception as exc:
            logger.warning("history_record_failed", error=str(exc))
