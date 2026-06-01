"""MongoDB repository for search history (system of record, scoped by client).

History is de-duplicated by resolved location on write (a repeat lookup moves
to the top) and capped per client, so reads are a simple recent-first slice.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.db_types import MongoDatabase
from app.models.common import Units
from app.models.history import HistoryItem
from app.models.weather import ResolvedLocation

COLLECTION = "history"


class HistoryRepository:
    """Append, de-duplicate, cap, and read search history per client."""

    def __init__(self, db: MongoDatabase, max_items: int) -> None:
        self._col = db[COLLECTION]
        self._max_items = max_items

    async def ensure_indexes(self) -> None:
        await self._col.create_index([("client_id", 1), ("searched_at", -1)])

    async def record(
        self,
        client_id: str,
        query: str,
        location: ResolvedLocation,
        units: Units,
    ) -> None:
        await self._col.delete_many(
            {
                "client_id": client_id,
                "latitude": location.latitude,
                "longitude": location.longitude,
            }
        )
        doc: dict[str, Any] = {
            "client_id": client_id,
            "query": query,
            "location": location.model_dump(),
            "latitude": location.latitude,
            "longitude": location.longitude,
            "units": units.value,
            "searched_at": datetime.now(UTC).isoformat(),
        }
        await self._col.insert_one(doc)
        await self._trim(client_id)

    async def _trim(self, client_id: str) -> None:
        cursor = self._col.find({"client_id": client_id}, {"_id": 1}).sort("searched_at", -1)
        docs = await cursor.to_list(length=None)
        stale_ids = [doc["_id"] for doc in docs[self._max_items :]]
        if stale_ids:
            await self._col.delete_many({"_id": {"$in": stale_ids}})

    async def list(self, client_id: str) -> list[HistoryItem]:
        cursor = self._col.find({"client_id": client_id}).sort("searched_at", -1)
        docs = await cursor.to_list(length=self._max_items)
        return [
            HistoryItem(
                query=doc["query"],
                location=ResolvedLocation(**doc["location"]),
                units=Units(doc["units"]),
                searched_at=doc["searched_at"],
            )
            for doc in docs
        ]
