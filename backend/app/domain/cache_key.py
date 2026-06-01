"""Cache key derivation.

Keys are derived from resolved coordinates (rounded to a configurable
precision so nearby lookups collapse to the same key) plus the unit system.
"""

from __future__ import annotations

from app.models.common import Units


def build_weather_cache_key(
    latitude: float,
    longitude: float,
    units: Units,
    precision: int,
) -> str:
    """Build a deterministic cache key for a resolved weather lookup.

    Coordinates are rounded to ``precision`` decimal places. At precision 2 this
    is roughly a 1 km grid, so repeated lookups of the same city hit one key.
    """
    lat = round(latitude, precision)
    lon = round(longitude, precision)
    return f"weather:v1:{lat}:{lon}:{units.value}"
