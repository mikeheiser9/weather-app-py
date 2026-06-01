"""Unit-system mapping and conversion helpers.

Maps the client-facing ``metric``/``imperial`` choice onto Open-Meteo's unit
query parameters and the symbols shown in the UI. Pure conversion helpers are
provided for completeness and unit testing.
"""

from __future__ import annotations

from app.models.common import Units
from app.models.weather import UnitLabels

# Open-Meteo unit query parameters per unit system.
# Docs: https://open-meteo.com/en/docs (temperature_unit, wind_speed_unit, precipitation_unit)
_OPEN_METEO_PARAMS: dict[Units, dict[str, str]] = {
    Units.METRIC: {
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    },
    Units.IMPERIAL: {
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
    },
}

_UNIT_LABELS: dict[Units, UnitLabels] = {
    Units.METRIC: UnitLabels(temperature="°C", wind_speed="km/h", precipitation="mm"),
    Units.IMPERIAL: UnitLabels(temperature="°F", wind_speed="mph", precipitation="in"),
}


def open_meteo_params(units: Units) -> dict[str, str]:
    """Return the Open-Meteo unit query parameters for a unit system."""
    return dict(_OPEN_METEO_PARAMS[units])


def unit_labels(units: Units) -> UnitLabels:
    """Return the display unit symbols for a unit system."""
    return _UNIT_LABELS[units].model_copy()


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9.0 / 5.0 + 32.0


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32.0) * 5.0 / 9.0


def kmh_to_mph(kmh: float) -> float:
    """Convert kilometers per hour to miles per hour."""
    return kmh * 0.621371


def mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / 25.4
