"""Favorites service: thin orchestration over the favorites repository."""

from __future__ import annotations

from app.models.favorites import Favorite, FavoriteCreate
from app.repositories.favorites_repo import FavoritesRepository


class FavoritesService:
    def __init__(self, repo: FavoritesRepository) -> None:
        self._repo = repo

    async def list(self, client_id: str) -> list[Favorite]:
        return await self._repo.list(client_id)

    async def create(self, client_id: str, data: FavoriteCreate) -> Favorite:
        return await self._repo.create(client_id, data)

    async def delete(self, client_id: str, favorite_id: str) -> bool:
        return await self._repo.delete(client_id, favorite_id)
