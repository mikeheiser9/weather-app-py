"""Integration tests for favorites CRUD, scoped by X-Client-Id."""

from __future__ import annotations

from typing import Any

from tests.conftest import Harness
from tests.samples import CLIENT_ID

_LOCATION: dict[str, Any] = {
    "name": "London",
    "admin1": "England",
    "country": "United Kingdom",
    "country_code": "GB",
    "latitude": 51.5074,
    "longitude": -0.1278,
    "timezone": "Europe/London",
}
_BODY = {"query": "London", "location": _LOCATION}
_HEADERS = {"X-Client-Id": CLIENT_ID}


async def test_create_requires_client_id(harness: Harness) -> None:
    response = await harness.client.post("/favorites", json=_BODY)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_client_id"


async def test_invalid_client_id_rejected(harness: Harness) -> None:
    response = await harness.client.get("/favorites", headers={"X-Client-Id": "not-a-uuid"})
    assert response.status_code == 400


async def test_create_list_delete_flow(harness: Harness) -> None:
    created = await harness.client.post("/favorites", json=_BODY, headers=_HEADERS)
    assert created.status_code == 201
    favorite_id = created.json()["id"]
    assert created.json()["location"]["country_code"] == "GB"

    listed = await harness.client.get("/favorites", headers=_HEADERS)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = await harness.client.delete(f"/favorites/{favorite_id}", headers=_HEADERS)
    assert deleted.status_code == 204

    listed_again = await harness.client.get("/favorites", headers=_HEADERS)
    assert listed_again.json() == []


async def test_duplicate_favorite_is_idempotent(harness: Harness) -> None:
    first = await harness.client.post("/favorites", json=_BODY, headers=_HEADERS)
    second = await harness.client.post("/favorites", json=_BODY, headers=_HEADERS)
    assert first.json()["id"] == second.json()["id"]

    listed = await harness.client.get("/favorites", headers=_HEADERS)
    assert len(listed.json()) == 1


async def test_delete_missing_returns_404(harness: Harness) -> None:
    response = await harness.client.delete("/favorites/000000000000000000000000", headers=_HEADERS)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_favorites_scoped_per_client(harness: Harness) -> None:
    await harness.client.post("/favorites", json=_BODY, headers=_HEADERS)
    other = await harness.client.get(
        "/favorites", headers={"X-Client-Id": "22222222-2222-2222-2222-222222222222"}
    )
    assert other.json() == []
