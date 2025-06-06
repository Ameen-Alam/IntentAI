"""Tests for the tool detector functionality."""

import pytest
from tool_detector import detect_tool_and_params


@pytest.mark.parametrize(
    "input_text,expected",
    [
        # Calculator tests
        ("Calculate 5 * 13", {"tool": "calculator", "params": {"expression": "5 * 13"}}),
        ("What is 20 + 7?", {"tool": "calculator", "params": {"expression": "20 + 7"}}),
        ("Calculate", None),  # Empty expression
        # Weather tests
        ("Weather in new york", {"tool": "get_weather", "params": {"city": "New York"}}),
        ("Weather in", None),  # Empty city
        # Stock tests
        ("Stock price of msft", {"tool": "lookup_stock", "params": {"symbol": "MSFT"}}),
        ("Stock price of 123", None),  # Invalid symbol
        # No tool detected
        ("Tell me a joke", None),
        ("", None),
    ],
)
def test_detect_tool_and_params(input_text: str, expected: dict | None) -> None:
    """Test tool detection with various inputs."""
    assert detect_tool_and_params(input_text) == expected 