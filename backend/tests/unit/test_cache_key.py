"""Unit tests for cache key derivation."""

from __future__ import annotations

from app.domain.cache_key import build_weather_cache_key
from app.models.common import Units


def test_key_is_deterministic() -> None:
    first = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 2)
    second = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 2)
    assert first == second


def test_nearby_coordinates_collapse_to_same_key() -> None:
    a = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 2)
    b = build_weather_cache_key(51.5101, -0.1299, Units.METRIC, 2)
    assert a == b


def test_units_change_the_key() -> None:
    metric = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 2)
    imperial = build_weather_cache_key(51.5074, -0.1278, Units.IMPERIAL, 2)
    assert metric != imperial


def test_precision_affects_rounding() -> None:
    coarse = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 0)
    fine = build_weather_cache_key(51.5074, -0.1278, Units.METRIC, 4)
    assert coarse != fine
    assert coarse.endswith("52.0:-0.0:metric") or coarse.endswith("52:-0:metric")
