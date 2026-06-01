"""Open-Meteo upstream client (keyless, CC BY 4.0).

All three upstreams (geocoding, forecast, air quality) are reached through a
single reused ``httpx.AsyncClient`` and wrapped with retry plus circuit-breaker
resilience. Parameter names follow the current Open-Meteo docs
(https://open-meteo.com/en/docs): the modern ``current=`` parameter set is used,
not the legacy ``current_weather=true`` shape.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog

from app.clients.resilience import Resilience, TransientUpstreamError
from app.config import Settings
from app.domain.normalize import normalize_location
from app.domain.units import open_meteo_params
from app.errors import CityNotFoundError, UpstreamError
from app.models.common import Units
from app.models.weather import ResolvedLocation

logger = structlog.get_logger(__name__)

# Current Open-Meteo forecast field selections.
_CURRENT_FIELDS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,"
    "precipitation,weather_code,wind_speed_10m,wind_direction_10m"
)
_HOURLY_FIELDS = "temperature_2m,precipitation_probability,weather_code"
_DAILY_FIELDS = (
    "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,sunrise,sunset"
)
_AQ_CURRENT_FIELDS = "us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone"
_AQ_HOURLY_FIELDS = "us_aqi"

_FORECAST_DAYS = 7


class OpenMeteoClient:
    """Async client for the Open-Meteo geocoding, forecast, and AQI endpoints."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: Settings,
        resilience: Resilience,
    ) -> None:
        self._client = client
        self._settings = settings
        self._resilience = resilience

    async def _get_json(self, upstream: str, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch JSON from an upstream, applying retry and circuit-breaker."""

        async def _fetch() -> dict[str, Any]:
            start = time.perf_counter()
            try:
                response = await self._client.get(url, params=params)
            except httpx.TransportError as exc:
                logger.warning(
                    "upstream_call",
                    upstream=upstream,
                    error=str(exc),
                    duration_ms=round((time.perf_counter() - start) * 1000, 2),
                )
                raise TransientUpstreamError(f"{upstream}: {exc}") from exc

            logger.info(
                "upstream_call",
                upstream=upstream,
                status=response.status_code,
                duration_ms=round((time.perf_counter() - start) * 1000, 2),
            )

            if response.status_code >= 500:
                raise TransientUpstreamError(f"{upstream} returned {response.status_code}")
            if response.status_code >= 400:
                raise UpstreamError(f"{upstream} returned {response.status_code}")

            data: dict[str, Any] = response.json()
            return data

        return await self._resilience.call(upstream, _fetch)

    async def geocode(self, city: str) -> ResolvedLocation:
        """Resolve a city name to a single location, or raise CityNotFoundError."""
        params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }
        payload = await self._get_json("geocoding", self._settings.geocoding_base_url, params)
        results = payload.get("results") or []
        if not results:
            raise CityNotFoundError(f"No matching city was found for '{city}'.")
        return normalize_location(results[0])

    async def geocode_search(self, query: str, count: int) -> list[ResolvedLocation]:
        """Return up to ``count`` candidate locations for a partial query.

        Used for search typeahead. Unlike ``geocode`` this never raises on an
        empty result set; it simply returns an empty list.
        """
        params = {
            "name": query,
            "count": count,
            "language": "en",
            "format": "json",
        }
        payload = await self._get_json("geocoding", self._settings.geocoding_base_url, params)
        results = payload.get("results") or []
        return [normalize_location(result) for result in results]

    async def forecast(self, latitude: float, longitude: float, units: Units) -> dict[str, Any]:
        """Fetch the current, hourly, and daily forecast for coordinates."""
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
            "current": _CURRENT_FIELDS,
            "hourly": _HOURLY_FIELDS,
            "daily": _DAILY_FIELDS,
            "forecast_days": _FORECAST_DAYS,
            **open_meteo_params(units),
        }
        return await self._get_json("forecast", self._settings.forecast_base_url, params)

    async def air_quality(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Fetch current and hourly air quality for coordinates."""
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
            "current": _AQ_CURRENT_FIELDS,
            "hourly": _AQ_HOURLY_FIELDS,
        }
        return await self._get_json("air_quality", self._settings.air_quality_base_url, params)

    async def reachable(self) -> bool:
        """Cheap upstream reachability probe for /health (no retry or breaker)."""
        try:
            response = await self._client.get(
                self._settings.geocoding_base_url,
                params={"name": "London", "count": 1, "format": "json"},
                timeout=self._settings.health_upstream_timeout,
            )
        except httpx.HTTPError:
            return False
        return response.status_code < 500
