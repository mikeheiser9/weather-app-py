"""Unit tests for unit-system mapping and conversion helpers."""

from __future__ import annotations

import pytest
from app.domain.units import (
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    kmh_to_mph,
    mm_to_inch,
    open_meteo_params,
    unit_labels,
)
from app.models.common import Units


def test_metric_params() -> None:
    params = open_meteo_params(Units.METRIC)
    assert params == {
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }


def test_imperial_params() -> None:
    params = open_meteo_params(Units.IMPERIAL)
    assert params == {
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    }


def test_unit_labels() -> None:
    metric = unit_labels(Units.METRIC)
    imperial = unit_labels(Units.IMPERIAL)
    assert metric.temperature == "°C"
    assert metric.wind_speed == "km/h"
    assert metric.precipitation == "mm"
    assert imperial.temperature == "°F"
    assert imperial.wind_speed == "mph"
    assert imperial.precipitation == "in"


@pytest.mark.parametrize(
    ("celsius", "fahrenheit"),
    [(0.0, 32.0), (100.0, 212.0), (-40.0, -40.0), (37.0, 98.6)],
)
def test_temperature_conversions_round_trip(celsius: float, fahrenheit: float) -> None:
    assert celsius_to_fahrenheit(celsius) == pytest.approx(fahrenheit)
    assert fahrenheit_to_celsius(fahrenheit) == pytest.approx(celsius)


def test_speed_and_precip_conversions() -> None:
    assert kmh_to_mph(100.0) == pytest.approx(62.1371, rel=1e-4)
    assert mm_to_inch(25.4) == pytest.approx(1.0)
