"""Integration tests for search history, recorded via /weather and scoped by client."""

from __future__ import annotations

from typing import Any

import httpx
import respx

from tests.conftest import Harness
from tests.samples import AQ_URL, CLIENT_ID, FORECAST_URL, GEO_URL, aqi_payload, forecast_payload

_HEADERS = {"X-Client-Id": CLIENT_ID}


def _geo(name: str, lat: float, lon: float) -> dict[str, Any]:
    return {
        "results": [
            {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "country": "Country",
                "country_code": "CC",
                "admin1": "Region",
                "timezone": "UTC",
            }
        ]
    }


def _mock_forecast_aqi(router: respx.Router) -> None:
    router.get(url__startswith=FORECAST_URL).mock(
        return_value=httpx.Response(200, json=forecast_payload())
    )
    router.get(url__startswith=AQ_URL).mock(return_value=httpx.Response(200, json=aqi_payload()))


async def test_history_requires_client_id(harness: Harness) -> None:
    response = await harness.client.get("/history")
    assert response.status_code == 400


async def test_weather_lookup_is_recorded(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=_geo("London", 51.5, -0.12))
        )
        _mock_forecast_aqi(router)
        await harness.client.get("/weather", params={"city": "London"}, headers=_HEADERS)

    history = await harness.client.get("/history", headers=_HEADERS)
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    assert items[0]["query"] == "London"
    assert items[0]["location"]["name"] == "London"


async def test_history_deduplicates_same_location(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=_geo("London", 51.5, -0.12))
        )
        _mock_forecast_aqi(router)
        await harness.client.get("/weather", params={"city": "London"}, headers=_HEADERS)
        await harness.client.get("/weather", params={"city": "London"}, headers=_HEADERS)

    history = await harness.client.get("/history", headers=_HEADERS)
    assert len(history.json()) == 1


async def test_history_is_capped(make_harness: object) -> None:
    async with make_harness(history_max_items=3) as harness:  # type: ignore[operator]
        with respx.mock(assert_all_called=False) as router:
            _mock_forecast_aqi(router)
            geo_route = router.get(url__startswith=GEO_URL)
            geo_route.mock(
                side_effect=[
                    httpx.Response(200, json=_geo(f"City{index}", 10.0 + index, 20.0 + index))
                    for index in range(5)
                ]
            )
            for index in range(5):
                await harness.client.get(
                    "/weather", params={"city": f"City{index}"}, headers=_HEADERS
                )

        history = await harness.client.get("/history", headers=_HEADERS)
        items = history.json()
        assert len(items) == 3
        assert items[0]["query"] == "City4"


async def test_history_scoped_per_client(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=_geo("London", 51.5, -0.12))
        )
        _mock_forecast_aqi(router)
        await harness.client.get("/weather", params={"city": "London"}, headers=_HEADERS)

    other = await harness.client.get(
        "/history", headers={"X-Client-Id": "33333333-3333-3333-3333-333333333333"}
    )
    assert other.json() == []
