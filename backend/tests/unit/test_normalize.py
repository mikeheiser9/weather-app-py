"""Unit tests for upstream payload normalization."""

from __future__ import annotations

from app.domain.normalize import (
    DAILY_LIMIT,
    HOURLY_LIMIT,
    normalize_location,
    normalize_weather,
)
from app.domain.wmo import ConditionCategory
from app.models.common import Units

from tests.samples import aqi_payload, forecast_payload, geo_payload


def test_normalize_location() -> None:
    location = normalize_location(geo_payload()["results"][0])
    assert location.name == "London"
    assert location.country_code == "GB"
    assert location.admin1 == "England"
    assert location.latitude == 51.5074


def test_normalize_weather_full_payload() -> None:
    location = normalize_location(geo_payload()["results"][0])
    response = normalize_weather(
        location=location,
        forecast=forecast_payload(),
        air_quality=aqi_payload(),
        units=Units.METRIC,
        fetched_at="2026-06-01T09:00:00+00:00",
    )

    assert response.current.temperature == 15.2
    assert response.current.is_day is True
    assert response.current.condition_category == ConditionCategory.CLOUDY
    assert response.condition_category == ConditionCategory.CLOUDY
    assert response.units == Units.METRIC
    assert response.cache is False


def test_hourly_is_capped_and_starts_at_current_hour() -> None:
    location = normalize_location(geo_payload()["results"][0])
    response = normalize_weather(
        location=location,
        forecast=forecast_payload(),
        air_quality=None,
        units=Units.METRIC,
        fetched_at="2026-06-01T09:00:00+00:00",
    )
    assert len(response.hourly) == HOURLY_LIMIT
    assert response.hourly[0].time == "2026-06-01T09:00"


def test_daily_is_capped_to_seven() -> None:
    location = normalize_location(geo_payload()["results"][0])
    response = normalize_weather(
        location=location,
        forecast=forecast_payload(),
        air_quality=None,
        units=Units.METRIC,
        fetched_at="2026-06-01T09:00:00+00:00",
    )
    assert len(response.daily) == DAILY_LIMIT
    assert response.daily[4].condition_category == ConditionCategory.RAIN


def test_air_quality_absent_when_none() -> None:
    location = normalize_location(geo_payload()["results"][0])
    response = normalize_weather(
        location=location,
        forecast=forecast_payload(),
        air_quality=None,
        units=Units.METRIC,
        fetched_at="2026-06-01T09:00:00+00:00",
    )
    assert response.air_quality is None


def test_air_quality_normalized() -> None:
    location = normalize_location(geo_payload()["results"][0])
    response = normalize_weather(
        location=location,
        forecast=forecast_payload(),
        air_quality=aqi_payload(),
        units=Units.METRIC,
        fetched_at="2026-06-01T09:00:00+00:00",
    )
    assert response.air_quality is not None
    assert response.air_quality.us_aqi == 42
    assert response.air_quality.pm2_5 == 6.2
    assert len(response.air_quality.hourly) > 0
