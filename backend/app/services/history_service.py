"""History service: thin orchestration over the history repository."""

from __future__ import annotations

from app.models.history import HistoryItem
from app.repositories.history_repo import HistoryRepository


class HistoryService:
    def __init__(self, repo: HistoryRepository) -> None:
        self._repo = repo

    async def list(self, client_id: str) -> list[HistoryItem]:
        return await self._repo.list(client_id)
