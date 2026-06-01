"""Favorites CRUD endpoints, scoped by X-Client-Id."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.dependencies import ClientIdDep, FavoritesServiceDep
from app.errors import ResourceNotFoundError
from app.models.common import ErrorResponse
from app.models.favorites import Favorite, FavoriteCreate

router = APIRouter(prefix="/favorites", tags=["favorites"])

_CLIENT_ID_RESPONSES: dict[int | str, dict[str, object]] = {400: {"model": ErrorResponse}}


@router.get("", response_model=list[Favorite], responses=_CLIENT_ID_RESPONSES)
async def list_favorites(service: FavoritesServiceDep, client_id: ClientIdDep) -> list[Favorite]:
    return await service.list(client_id)


@router.post(
    "",
    response_model=Favorite,
    status_code=status.HTTP_201_CREATED,
    responses=_CLIENT_ID_RESPONSES,
)
async def create_favorite(
    data: FavoriteCreate,
    service: FavoritesServiceDep,
    client_id: ClientIdDep,
) -> Favorite:
    return await service.create(client_id, data)


@router.delete(
    "/{favorite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**_CLIENT_ID_RESPONSES, 404: {"model": ErrorResponse}},
)
async def delete_favorite(
    favorite_id: str,
    service: FavoritesServiceDep,
    client_id: ClientIdDep,
) -> Response:
    deleted = await service.delete(client_id, favorite_id)
    if not deleted:
        raise ResourceNotFoundError("Favorite not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
