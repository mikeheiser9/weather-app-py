"""Favorite city models (persisted in MongoDB, scoped by client id)."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.weather import ResolvedLocation


class FavoriteCreate(BaseModel):
    """Request body to save a favorite city.

    The client sends the resolved location it already obtained from a weather
    lookup so the favorite card can be re-rendered without another geocode.
    """

    query: str
    location: ResolvedLocation


class Favorite(BaseModel):
    """A stored favorite returned to the client."""

    id: str
    query: str
    location: ResolvedLocation
    created_at: str
