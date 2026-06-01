"""Integration tests for GET /weather with Open-Meteo mocked via respx."""

from __future__ import annotations

import httpx
import respx

from tests.conftest import Harness
from tests.samples import (
    AQ_URL,
    FORECAST_URL,
    GEO_URL,
    BrokenRedis,
    aqi_payload,
    forecast_payload,
    geo_payload,
)


def _mock_all_ok(router: respx.Router) -> None:
    router.get(url__startswith=GEO_URL).mock(return_value=httpx.Response(200, json=geo_payload()))
    router.get(url__startswith=FORECAST_URL).mock(
        return_value=httpx.Response(200, json=forecast_payload())
    )
    router.get(url__startswith=AQ_URL).mock(return_value=httpx.Response(200, json=aqi_payload()))


async def test_weather_happy_path(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        _mock_all_ok(router)
        response = await harness.client.get("/weather", params={"city": "London"})

    assert response.status_code == 200
    body = response.json()
    assert body["location"]["name"] == "London"
    assert body["location"]["country_code"] == "GB"
    assert body["current"]["temperature"] == 15.2
    assert body["condition_category"] == "cloudy"
    assert body["current"]["description"] == "Overcast"
    assert body["units"] == "metric"
    assert body["cache"] is False
    assert len(body["hourly"]) == 24
    assert len(body["daily"]) == 7
    assert body["air_quality"]["us_aqi"] == 42
    assert "X-Request-Id" in response.headers


async def test_second_call_is_served_from_cache(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        forecast_route = router.get(url__startswith=FORECAST_URL).mock(
            return_value=httpx.Response(200, json=forecast_payload())
        )
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=geo_payload())
        )
        router.get(url__startswith=AQ_URL).mock(
            return_value=httpx.Response(200, json=aqi_payload())
        )

        first = await harness.client.get("/weather", params={"city": "London"})
        second = await harness.client.get("/weather", params={"city": "London"})

    assert first.json()["cache"] is False
    assert second.json()["cache"] is True
    assert forecast_route.call_count == 1


async def test_city_not_found_returns_404(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json={"results": []})
        )
        response = await harness.client.get("/weather", params={"city": "Nowhereville"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "city_not_found"


async def test_upstream_5xx_then_recovery(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=geo_payload())
        )
        router.get(url__startswith=AQ_URL).mock(
            return_value=httpx.Response(200, json=aqi_payload())
        )
        forecast_route = router.get(url__startswith=FORECAST_URL).mock(
            side_effect=[
                httpx.Response(500),
                httpx.Response(200, json=forecast_payload()),
            ]
        )
        response = await harness.client.get("/weather", params={"city": "London"})

    assert response.status_code == 200
    assert forecast_route.call_count == 2


async def test_breaker_open_fast_fails(make_harness: object) -> None:
    async with make_harness(retry_max_attempts=1, breaker_fail_max=1) as harness:  # type: ignore[operator]
        with respx.mock(assert_all_called=False) as router:
            router.get(url__startswith=GEO_URL).mock(
                return_value=httpx.Response(200, json=geo_payload())
            )
            router.get(url__startswith=AQ_URL).mock(
                return_value=httpx.Response(200, json=aqi_payload())
            )
            forecast_route = router.get(url__startswith=FORECAST_URL).mock(
                return_value=httpx.Response(500)
            )

            first = await harness.client.get("/weather", params={"city": "London"})
            second = await harness.client.get("/weather", params={"city": "London"})

        assert first.status_code in (502, 503)
        assert second.status_code == 503
        assert second.json()["error"]["code"] == "upstream_unavailable"
        # The open breaker means the forecast upstream is not hit on the 2nd call.
        assert forecast_route.call_count == 1


async def test_geocode_returns_candidates(harness: Harness) -> None:
    payload = {
        "results": [
            {
                "name": "London",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "country": "United Kingdom",
                "country_code": "GB",
                "admin1": "England",
                "timezone": "Europe/London",
            },
            {
                "name": "London",
                "latitude": 42.9834,
                "longitude": -81.233,
                "country": "Canada",
                "country_code": "CA",
                "admin1": "Ontario",
                "timezone": "America/Toronto",
            },
        ]
    }
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(return_value=httpx.Response(200, json=payload))
        response = await harness.client.get("/geocode", params={"q": "Lond", "count": 5})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["country_code"] == "GB"
    assert body[1]["country_code"] == "CA"


async def test_geocode_no_matches_returns_empty(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=GEO_URL).mock(return_value=httpx.Response(200, json={}))
        response = await harness.client.get("/geocode", params={"q": "zzzzzz"})

    assert response.status_code == 200
    assert response.json() == []


async def test_weather_by_coordinates_skips_geocoding(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        geo_route = router.get(url__startswith=GEO_URL).mock(
            return_value=httpx.Response(200, json=geo_payload())
        )
        router.get(url__startswith=FORECAST_URL).mock(
            return_value=httpx.Response(200, json=forecast_payload())
        )
        router.get(url__startswith=AQ_URL).mock(
            return_value=httpx.Response(200, json=aqi_payload())
        )
        response = await harness.client.get("/weather", params={"lat": 51.51, "lon": -0.13})

    assert response.status_code == 200
    assert response.json()["location"]["name"] == "Current location"
    assert geo_route.call_count == 0


async def test_weather_by_coordinates_uses_provided_name(harness: Harness) -> None:
    with respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=FORECAST_URL).mock(
            return_value=httpx.Response(200, json=forecast_payload())
        )
        router.get(url__startswith=AQ_URL).mock(
            return_value=httpx.Response(200, json=aqi_payload())
        )
        response = await harness.client.get(
            "/weather", params={"lat": 48.85, "lon": 2.35, "name": "Paris"}
        )

    assert response.status_code == 200
    assert response.json()["location"]["name"] == "Paris"


async def test_weather_requires_city_or_coordinates(harness: Harness) -> None:
    response = await harness.client.get("/weather")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"


async def test_redis_down_still_serves_weather(make_harness: object) -> None:
    async with make_harness(redis=BrokenRedis()) as harness:  # type: ignore[operator]
        with respx.mock(assert_all_called=False) as router:
            _mock_all_ok(router)
            response = await harness.client.get("/weather", params={"city": "London"})

    assert response.status_code == 200
    assert response.json()["cache"] is False
