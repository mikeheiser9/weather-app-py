"""Single source of truth for WMO weather-code to condition-category mapping.

The WMO 4677 weather interpretation codes returned by Open-Meteo
(https://open-meteo.com/en/docs, "weather_code") are collapsed into a small set
of condition categories. This category is reused for response normalization and
is surfaced to the frontend so the UI selects its background from the same
mapping rather than re-deriving it.
"""

from __future__ import annotations

from enum import StrEnum


class ConditionCategory(StrEnum):
    """Coarse weather condition categories derived from WMO codes."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"


# Default category for any code outside the known set. Cloudy is the most
# visually neutral background and a safe fallback.
DEFAULT_CATEGORY = ConditionCategory.CLOUDY

_CODE_TO_CATEGORY: dict[int, ConditionCategory] = {
    0: ConditionCategory.CLEAR,
    1: ConditionCategory.CLOUDY,
    2: ConditionCategory.CLOUDY,
    3: ConditionCategory.CLOUDY,
    45: ConditionCategory.FOG,
    48: ConditionCategory.FOG,
    51: ConditionCategory.DRIZZLE,
    53: ConditionCategory.DRIZZLE,
    55: ConditionCategory.DRIZZLE,
    56: ConditionCategory.DRIZZLE,
    57: ConditionCategory.DRIZZLE,
    61: ConditionCategory.RAIN,
    63: ConditionCategory.RAIN,
    65: ConditionCategory.RAIN,
    66: ConditionCategory.RAIN,
    67: ConditionCategory.RAIN,
    80: ConditionCategory.RAIN,
    81: ConditionCategory.RAIN,
    82: ConditionCategory.RAIN,
    71: ConditionCategory.SNOW,
    73: ConditionCategory.SNOW,
    75: ConditionCategory.SNOW,
    77: ConditionCategory.SNOW,
    85: ConditionCategory.SNOW,
    86: ConditionCategory.SNOW,
    95: ConditionCategory.THUNDERSTORM,
    96: ConditionCategory.THUNDERSTORM,
    99: ConditionCategory.THUNDERSTORM,
}


def category_for_code(weather_code: int | None) -> ConditionCategory:
    """Map a WMO weather code to its condition category.

    Unknown or missing codes fall back to ``DEFAULT_CATEGORY``.
    """
    if weather_code is None:
        return DEFAULT_CATEGORY
    return _CODE_TO_CATEGORY.get(weather_code, DEFAULT_CATEGORY)


# Default human-facing label for any code outside the known set.
DEFAULT_DESCRIPTION = "Unknown"

# Precise WMO 4677 descriptions. Distinct from the coarse category above: the
# category drives background selection, while this drives the user-facing label
# so the UI can say "Partly cloudy" or "Overcast" instead of a generic "Cloudy".
_CODE_TO_DESCRIPTION: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def description_for_code(weather_code: int | None) -> str:
    """Map a WMO weather code to a precise human-facing description.

    Unknown or missing codes fall back to ``DEFAULT_DESCRIPTION``.
    """
    if weather_code is None:
        return DEFAULT_DESCRIPTION
    return _CODE_TO_DESCRIPTION.get(weather_code, DEFAULT_DESCRIPTION)
