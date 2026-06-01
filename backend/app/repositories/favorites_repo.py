"""MongoDB repository for favorite cities (system of record, scoped by client)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId

from app.db_types import MongoDatabase
from app.models.favorites import Favorite, FavoriteCreate
from app.models.weather import ResolvedLocation

COLLECTION = "favorites"


class FavoritesRepository:
    """CRUD for favorites, every operation scoped by ``client_id``."""

    def __init__(self, db: MongoDatabase) -> None:
        self._col = db[COLLECTION]

    async def ensure_indexes(self) -> None:
        await self._col.create_index("client_id")
        await self._col.create_index(
            [("client_id", 1), ("latitude", 1), ("longitude", 1)],
            unique=True,
        )

    @staticmethod
    def _to_model(doc: dict[str, Any]) -> Favorite:
        return Favorite(
            id=str(doc["_id"]),
            query=doc["query"],
            location=ResolvedLocation(**doc["location"]),
            created_at=doc["created_at"],
        )

    async def list(self, client_id: str) -> list[Favorite]:
        cursor = self._col.find({"client_id": client_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=200)
        return [self._to_model(doc) for doc in docs]

    async def create(self, client_id: str, data: FavoriteCreate) -> Favorite:
        location = data.location
        query_filter = {
            "client_id": client_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
        existing = await self._col.find_one(query_filter)
        if existing is not None:
            return self._to_model(existing)

        doc: dict[str, Any] = {
            "client_id": client_id,
            "query": data.query,
            "location": location.model_dump(),
            "latitude": location.latitude,
            "longitude": location.longitude,
            "created_at": datetime.now(UTC).isoformat(),
        }
        result = await self._col.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_model(doc)

    async def delete(self, client_id: str, favorite_id: str) -> bool:
        try:
            object_id = ObjectId(favorite_id)
        except (InvalidId, TypeError):
            return False
        result = await self._col.delete_one({"_id": object_id, "client_id": client_id})
        return result.deleted_count > 0
