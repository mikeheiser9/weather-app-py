"""Weather endpoint. Contains no business logic; delegates to WeatherService."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.dependencies import OptionalClientIdDep, WeatherServiceDep
from app.models.common import ErrorResponse, Units
from app.models.weather import ResolvedLocation, WeatherResponse

router = APIRouter(tags=["weather"])


@router.get(
    "/weather",
    response_model=WeatherResponse,
    responses={
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def get_weather(
    service: WeatherServiceDep,
    client_id: OptionalClientIdDep,
    city: Annotated[
        str | None, Query(min_length=1, description="City name to resolve and forecast.")
    ] = None,
    lat: Annotated[
        float | None, Query(ge=-90, le=90, description="Latitude (with lon, for geolocation).")
    ] = None,
    lon: Annotated[
        float | None, Query(ge=-180, le=180, description="Longitude (with lat, for geolocation).")
    ] = None,
    name: Annotated[
        str | None,
        Query(
            min_length=1, description="Optional label for a coordinate lookup (e.g. a picked city)."
        ),
    ] = None,
    units: Units = Units.METRIC,
) -> WeatherResponse:
    """Resolve a city (or coordinates), return normalized weather, and record history."""
    return await service.get_weather(
        city=city,
        latitude=lat,
        longitude=lon,
        name=name,
        units=units,
        client_id=client_id,
    )


@router.get(
    "/geocode",
    response_model=list[ResolvedLocation],
    responses={502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def geocode(
    service: WeatherServiceDep,
    q: Annotated[str, Query(min_length=1, description="Partial city name for typeahead.")],
    count: Annotated[int, Query(ge=1, le=10, description="Max candidate locations.")] = 5,
) -> list[ResolvedLocation]:
    """Return candidate locations for search typeahead (empty list when none match)."""
    return await service.search_locations(q, count)
