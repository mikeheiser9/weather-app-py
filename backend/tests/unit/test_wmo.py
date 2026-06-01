"""Unit tests for the WMO weather-code to condition-category mapping."""

from __future__ import annotations

import pytest
from app.domain.wmo import DEFAULT_CATEGORY, ConditionCategory, category_for_code


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (0, ConditionCategory.CLEAR),
        (1, ConditionCategory.CLOUDY),
        (2, ConditionCategory.CLOUDY),
        (3, ConditionCategory.CLOUDY),
        (45, ConditionCategory.FOG),
        (48, ConditionCategory.FOG),
        (51, ConditionCategory.DRIZZLE),
        (57, ConditionCategory.DRIZZLE),
        (61, ConditionCategory.RAIN),
        (82, ConditionCategory.RAIN),
        (71, ConditionCategory.SNOW),
        (86, ConditionCategory.SNOW),
        (95, ConditionCategory.THUNDERSTORM),
        (99, ConditionCategory.THUNDERSTORM),
    ],
)
def test_known_codes_map_to_expected_category(code: int, expected: ConditionCategory) -> None:
    assert category_for_code(code) == expected


def test_unknown_code_falls_back_to_default() -> None:
    assert category_for_code(123) == DEFAULT_CATEGORY


def test_none_code_falls_back_to_default() -> None:
    assert category_for_code(None) == DEFAULT_CATEGORY


def test_every_documented_rain_code_is_rain() -> None:
    for code in (61, 63, 65, 66, 67, 80, 81, 82):
        assert category_for_code(code) == ConditionCategory.RAIN
