"""Normalized weather response models.

Raw Open-Meteo JSON is never returned to clients. The service maps upstream
payloads into these models before responding or caching.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.wmo import ConditionCategory
from app.models.common import Units


class ResolvedLocation(BaseModel):
    """The location a city query actually resolved to via geocoding."""

    name: str
    admin1: str | None = None
    country: str | None = None
    country_code: str | None = None
    latitude: float
    longitude: float
    timezone: str | None = None


class CurrentConditions(BaseModel):
    """Current weather snapshot."""

    time: str
    temperature: float | None = None
    apparent_temperature: float | None = None
    relative_humidity: int | None = None
    is_day: bool | None = None
    precipitation: float | None = None
    weather_code: int | None = None
    condition_category: ConditionCategory
    description: str
    wind_speed: float | None = None
    wind_direction: int | None = None


class HourlyPoint(BaseModel):
    """A single hourly forecast point (next ~24h)."""

    time: str
    temperature: float | None = None
    precipitation_probability: int | None = None
    weather_code: int | None = None
    condition_category: ConditionCategory


class DailyPoint(BaseModel):
    """A single daily forecast point (7 day)."""

    date: str
    weather_code: int | None = None
    condition_category: ConditionCategory
    temperature_max: float | None = None
    temperature_min: float | None = None
    precipitation_sum: float | None = None
    sunrise: str | None = None
    sunset: str | None = None


class AirQualityPoint(BaseModel):
    """Hourly US AQI point used for the air-quality trend."""

    time: str
    us_aqi: int | None = None


class AirQuality(BaseModel):
    """Current air quality plus a short US AQI trend."""

    time: str | None = None
    us_aqi: int | None = None
    pm10: float | None = None
    pm2_5: float | None = None
    carbon_monoxide: float | None = None
    nitrogen_dioxide: float | None = None
    ozone: float | None = None
    hourly: list[AirQualityPoint] = Field(default_factory=list)


class UnitLabels(BaseModel):
    """Human-facing unit symbols matching the requested unit system."""

    temperature: str
    wind_speed: str
    precipitation: str


class WeatherResponse(BaseModel):
    """The full normalized weather payload returned by GET /weather."""

    location: ResolvedLocation
    units: Units
    unit_labels: UnitLabels
    condition_category: ConditionCategory
    current: CurrentConditions
    hourly: list[HourlyPoint] = Field(default_factory=list)
    daily: list[DailyPoint] = Field(default_factory=list)
    air_quality: AirQuality | None = None
    cache: bool = False
    fetched_at: str
