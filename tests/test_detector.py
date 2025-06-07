"""Tests for the tool detector functionality."""

import pytest
from pydantic import BaseModel
from tool_detector import tool_call, get_tools_from_functions, detect_tool_and_params

# Define the same tools as in the examples
@tool_call
def calculator(expression: str) -> float:
    """
    Calculate the result of a mathematical expression.
    :trigger calculate
    :trigger what is
    :examples: Calculate 5 * 13, What is 20 + 7?
    """
    return eval(expression)

class WeatherParams(BaseModel):
    city: str
    units: str = "celsius"

@tool_call
def get_weather(params: WeatherParams) -> str:
    """
    Get weather information for a city.
    :trigger weather in
    :trigger temperature in
    :examples: Weather in new york, Temperature in New York in fahrenheit
    """
    return f"Weather in {params.city}: 72°{params.units[0].upper()}"

@tool_call
def lookup_stock(symbol: str) -> str:
    """
    Look up stock information.
    :trigger stock price of
    :examples: Stock price of msft
    """
    return f"Stock {symbol}: $150.00"

tools = get_tools_from_functions(calculator, get_weather, lookup_stock)

print("\nRegistered Tools for Testing:")
for tool in tools:
    print(f"Tool: {tool.name}, Triggers: {tool.trigger_phrases}")

@pytest.mark.parametrize(
    "input_text,expected",
    [
        # Calculator tests
        ("Calculate 5 * 13", {"tool": "calculator", "parameters": {"expression": "5 * 13"}}),
        ("What is 20 + 7?", {"tool": "calculator", "parameters": {"expression": "20 + 7"}}),
        ("Calculate", None),  # Empty expression
        # Weather tests
        ("Weather in new york", {"tool": "get_weather", "parameters": {"city": "new york", "units": "celsius"}}),
        ("Weather in", None),  # Empty city
        # Stock tests
        ("Stock price of msft", {"tool": "lookup_stock", "parameters": {"symbol": "MSFT"}}),
        ("Stock price of 123", None),  # Invalid symbol
        # No tool detected
        ("Tell me a joke", None),
        ("", None),
    ],
)
def test_detect_tool_and_params(input_text: str, expected: dict | None) -> None:
    """Test tool detection with various inputs."""
    result = detect_tool_and_params(input_text, available_tools=tools)
    if expected is None:
        assert result is None
    else:
        # Only compare tool and parameters for simplicity
        assert result['tool'] == expected['tool']
        for k, v in expected['parameters'].items():
            assert result['parameters'].get(k) == v 