"""Search history endpoint, scoped by X-Client-Id."""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import ClientIdDep, HistoryServiceDep
from app.models.common import ErrorResponse
from app.models.history import HistoryItem

router = APIRouter(tags=["history"])


@router.get(
    "/history",
    response_model=list[HistoryItem],
    responses={400: {"model": ErrorResponse}},
)
async def list_history(service: HistoryServiceDep, client_id: ClientIdDep) -> list[HistoryItem]:
    return await service.list(client_id)
