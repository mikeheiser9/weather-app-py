"""Integration tests for GET /health."""

from __future__ import annotations

import httpx
import respx

from tests.conftest import Harness
from tests.samples import GEO_URL, BrokenRedis, geo_payload


async def test_health_ok(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=geo_payload())
        )
        response = await harness.client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["redis"]["status"] == "ok"
    assert body["mongo"]["status"] == "ok"
    assert body["upstream"]["status"] == "ok"
    assert set(body["breakers"]) == {"geocoding", "forecast", "air_quality"}


async def test_health_503_when_upstream_down(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(return_value=httpx.Response(500))
        response = await harness.client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "down"
    assert body["upstream"]["status"] == "down"


async def test_health_degraded_when_redis_down(make_harness: object) -> None:
    async with make_harness(redis=BrokenRedis()) as harness:  # type: ignore[operator]
        with respx.mock(assert_all_called=False) as router:
            router.get(url__startswith=GEO_URL).mock(
                return_value=httpx.Response(200, json=geo_payload())
            )
            response = await harness.client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["redis"]["status"] == "degraded"
