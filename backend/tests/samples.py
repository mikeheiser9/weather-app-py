"""Shared test data: Open-Meteo sample payloads, settings, and fakes.

Importable from both conftest and individual tests via ``tests.samples``.
"""

from __future__ import annotations

from typing import Any

from app.config import Settings
from redis.exceptions import RedisError

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CLIENT_ID = "11111111-1111-1111-1111-111111111111"


def make_settings(**overrides: Any) -> Settings:
    """Build deterministic, fast test settings (no backoff, small caps)."""
    defaults: dict[str, Any] = {
        "app_env": "dev",
        "retry_initial_backoff": 0.0,
        "retry_max_backoff": 0.0,
        "retry_max_attempts": 3,
        "breaker_fail_max": 5,
        "breaker_reset_timeout": 30,
        "history_max_items": 5,
        "cache_coord_precision": 2,
        "cache_ttl_seconds": 600,
    }
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def geo_payload() -> dict[str, Any]:
    return {
        "results": [
            {
                "name": "London",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "country": "United Kingdom",
                "country_code": "GB",
                "admin1": "England",
                "timezone": "Europe/London",
            }
        ]
    }


def forecast_payload() -> dict[str, Any]:
    times = [f"2026-06-01T{hour:02d}:00" for hour in range(24)]
    times += [f"2026-06-02T{hour:02d}:00" for hour in range(24)]
    count = len(times)
    return {
        "latitude": 51.5,
        "longitude": -0.12,
        "timezone": "Europe/London",
        "current": {
            "time": "2026-06-01T09:00",
            "temperature_2m": 15.2,
            "relative_humidity_2m": 72,
            "apparent_temperature": 14.0,
            "is_day": 1,
            "precipitation": 0.0,
            "weather_code": 3,
            "wind_speed_10m": 12.0,
            "wind_direction_10m": 210,
        },
        "hourly": {
            "time": times,
            "temperature_2m": [10.0 + index * 0.1 for index in range(count)],
            "precipitation_probability": [index % 100 for index in range(count)],
            "weather_code": [3] * count,
        },
        "daily": {
            "time": [f"2026-06-0{day}" for day in range(1, 9)],
            "weather_code": [0, 1, 2, 3, 61, 71, 95, 45],
            "temperature_2m_max": [20.0 + day for day in range(8)],
            "temperature_2m_min": [10.0 + day for day in range(8)],
            "precipitation_sum": [0.0, 1.2, 0.0, 3.4, 5.6, 0.0, 2.1, 0.0],
            "sunrise": [f"2026-06-0{day}T05:00" for day in range(1, 9)],
            "sunset": [f"2026-06-0{day}T21:00" for day in range(1, 9)],
        },
    }


def aqi_payload() -> dict[str, Any]:
    times = [f"2026-06-01T{hour:02d}:00" for hour in range(24)]
    return {
        "current": {
            "time": "2026-06-01T09:00",
            "us_aqi": 42,
            "pm10": 10.1,
            "pm2_5": 6.2,
            "carbon_monoxide": 200.0,
            "nitrogen_dioxide": 12.0,
            "ozone": 60.0,
        },
        "hourly": {
            "time": times,
            "us_aqi": [40 + (index % 10) for index in range(len(times))],
        },
    }


class BrokenRedis:
    """A Redis double whose every operation raises, to test degradation."""

    async def get(self, *args: Any, **kwargs: Any) -> Any:
        raise RedisError("redis down")

    async def set(self, *args: Any, **kwargs: Any) -> Any:
        raise RedisError("redis down")

    async def ping(self, *args: Any, **kwargs: Any) -> Any:
        raise RedisError("redis down")

    async def aclose(self) -> None:
        return None
