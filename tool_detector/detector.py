"""Core tool detection functionality."""

import re
from typing import Any, Dict, Optional, TypedDict


class ToolParams(TypedDict):
    """Type definition for tool parameters."""

    expression: str  # For calculator
    city: str  # For weather
    symbol: str  # For stock lookup


class ToolResult(TypedDict):
    """Type definition for tool detection result."""

    tool: str
    params: ToolParams


# Mapping from trigger phrases to tool names
TOOL_KEYWORDS = {
    "calculate": "calculator",
    "what is": "calculator",
    "weather in": "get_weather",
    "stock price of": "lookup_stock",
}


def detect_tool_and_params(user_text: str) -> Optional[ToolResult]:
    """Detect which tool to use and extract its parameters from user text.

    Args:
        user_text: The user's input text to analyze.

    Returns:
        A dictionary containing the detected tool name and its parameters,
        or None if no tool is detected.

    Example:
        >>> detect_tool_and_params("Calculate 5 * 13")
        {'tool': 'calculator', 'params': {'expression': '5 * 13'}}
        >>> detect_tool_and_params("Weather in London")
        {'tool': 'get_weather', 'params': {'city': 'London'}}
    """
    text = user_text.strip().lower()

    # Check each trigger phrase in descending order of length
    for phrase, tool_name in sorted(TOOL_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if phrase in text:
            # Split on the first occurrence of the phrase
            before, sep, after = text.partition(phrase)
            raw_args = after.strip()

            # Extract params based on which tool we've picked
            if tool_name == "calculator":
                expr = raw_args
                if not expr:
                    return None
                expr = expr.rstrip(" ?")
                return {"tool": "calculator", "params": {"expression": expr}}

            elif tool_name == "get_weather":
                city = raw_args.title()
                if not city:
                    return None
                return {"tool": "get_weather", "params": {"city": city}}

            elif tool_name == "lookup_stock":
                symbol = raw_args.upper()
                if not re.fullmatch(r"[A-Za-z]+", symbol):
                    return None
                return {"tool": "lookup_stock", "params": {"symbol": symbol}}

    return None 