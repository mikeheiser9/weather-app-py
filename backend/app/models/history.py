"""Search history models (persisted in MongoDB, scoped by client id)."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.common import Units
from app.models.weather import ResolvedLocation


class HistoryItem(BaseModel):
    """A single search history entry returned to the client."""

    query: str
    location: ResolvedLocation
    units: Units
    searched_at: str
