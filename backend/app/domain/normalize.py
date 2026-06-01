"""Normalization of raw Open-Meteo payloads into Pydantic response models.

This is the single place where upstream JSON shapes are read. Everything beyond
this layer works with typed models only.
"""

from __future__ import annotations

from typing import Any

from app.domain.units import unit_labels
from app.domain.wmo import category_for_code
from app.models.common import Units
from app.models.weather import (
    AirQuality,
    AirQualityPoint,
    CurrentConditions,
    DailyPoint,
    HourlyPoint,
    ResolvedLocation,
    WeatherResponse,
)

HOURLY_LIMIT = 24
DAILY_LIMIT = 7


def _at(values: list[Any], index: int) -> Any:
    """Return ``values[index]`` or ``None`` when out of range."""
    return values[index] if index < len(values) else None


def _start_index(times: list[Any], from_time: str | None) -> int:
    """First index whose timestamp is at or after ``from_time`` (else 0)."""
    if not from_time:
        return 0
    for index, value in enumerate(times):
        if value >= from_time:
            return index
    return 0


def normalize_location(result: dict[str, Any]) -> ResolvedLocation:
    """Map a single geocoding result into a ResolvedLocation."""
    return ResolvedLocation(
        name=result["name"],
        admin1=result.get("admin1"),
        country=result.get("country"),
        country_code=result.get("country_code"),
        latitude=result["latitude"],
        longitude=result["longitude"],
        timezone=result.get("timezone"),
    )


def _normalize_current(current: dict[str, Any]) -> CurrentConditions:
    code = current.get("weather_code")
    is_day_raw = current.get("is_day")
    return CurrentConditions(
        time=current.get("time", ""),
        temperature=current.get("temperature_2m"),
        apparent_temperature=current.get("apparent_temperature"),
        relative_humidity=current.get("relative_humidity_2m"),
        is_day=None if is_day_raw is None else bool(is_day_raw),
        precipitation=current.get("precipitation"),
        weather_code=code,
        condition_category=category_for_code(code),
        wind_speed=current.get("wind_speed_10m"),
        wind_direction=current.get("wind_direction_10m"),
    )


def _normalize_hourly(hourly: dict[str, Any], from_time: str | None) -> list[HourlyPoint]:
    times: list[Any] = hourly.get("time") or []
    temps: list[Any] = hourly.get("temperature_2m") or []
    probs: list[Any] = hourly.get("precipitation_probability") or []
    codes: list[Any] = hourly.get("weather_code") or []

    start = _start_index(times, from_time)
    end = min(start + HOURLY_LIMIT, len(times))
    points: list[HourlyPoint] = []
    for index in range(start, end):
        code = _at(codes, index)
        points.append(
            HourlyPoint(
                time=times[index],
                temperature=_at(temps, index),
                precipitation_probability=_at(probs, index),
                weather_code=code,
                condition_category=category_for_code(code),
            )
        )
    return points


def _normalize_daily(daily: dict[str, Any]) -> list[DailyPoint]:
    dates: list[Any] = daily.get("time") or []
    codes: list[Any] = daily.get("weather_code") or []
    tmax: list[Any] = daily.get("temperature_2m_max") or []
    tmin: list[Any] = daily.get("temperature_2m_min") or []
    psum: list[Any] = daily.get("precipitation_sum") or []
    sunrise: list[Any] = daily.get("sunrise") or []
    sunset: list[Any] = daily.get("sunset") or []

    points: list[DailyPoint] = []
    for index in range(min(DAILY_LIMIT, len(dates))):
        code = _at(codes, index)
        points.append(
            DailyPoint(
                date=dates[index],
                weather_code=code,
                condition_category=category_for_code(code),
                temperature_max=_at(tmax, index),
                temperature_min=_at(tmin, index),
                precipitation_sum=_at(psum, index),
                sunrise=_at(sunrise, index),
                sunset=_at(sunset, index),
            )
        )
    return points


def _normalize_air_quality(air_quality: dict[str, Any] | None) -> AirQuality | None:
    if not air_quality:
        return None
    current: dict[str, Any] = air_quality.get("current") or {}
    hourly: dict[str, Any] = air_quality.get("hourly") or {}
    times: list[Any] = hourly.get("time") or []
    aqis: list[Any] = hourly.get("us_aqi") or []

    start = _start_index(times, current.get("time"))
    end = min(start + HOURLY_LIMIT, len(times))
    points = [AirQualityPoint(time=times[i], us_aqi=_at(aqis, i)) for i in range(start, end)]

    return AirQuality(
        time=current.get("time"),
        us_aqi=current.get("us_aqi"),
        pm10=current.get("pm10"),
        pm2_5=current.get("pm2_5"),
        carbon_monoxide=current.get("carbon_monoxide"),
        nitrogen_dioxide=current.get("nitrogen_dioxide"),
        ozone=current.get("ozone"),
        hourly=points,
    )


def normalize_weather(
    *,
    location: ResolvedLocation,
    forecast: dict[str, Any],
    air_quality: dict[str, Any] | None,
    units: Units,
    fetched_at: str,
    cache: bool = False,
) -> WeatherResponse:
    """Build the full normalized weather response from upstream payloads."""
    current = _normalize_current(forecast.get("current") or {})
    return WeatherResponse(
        location=location,
        units=units,
        unit_labels=unit_labels(units),
        condition_category=current.condition_category,
        current=current,
        hourly=_normalize_hourly(forecast.get("hourly") or {}, current.time),
        daily=_normalize_daily(forecast.get("daily") or {}),
        air_quality=_normalize_air_quality(air_quality),
        cache=cache,
        fetched_at=fetched_at,
    )
