"""
Comprehensive example demonstrating all features of the tool-detector library.
"""

from typing import Optional
from pydantic import BaseModel
from tool_detector import (
    tool_call,
    get_tools_from_functions,
    detect_tool_and_params,
    get_openapi_schema_for_tools
)
import json

# 1. Basic tool with docstring
@tool_call
def calculate(expression: str) -> float:
    """
    Calculate the result of a mathematical expression.

    :param expression: The mathematical expression to evaluate
    :trigger calculate
    :trigger what is
    :trigger compute
    :trigger solve
    :examples:
    Calculate 5 * 13
    What is 20 + 7?
    """
    return eval(expression)

# 2. Tool with Pydantic model
class WeatherParams(BaseModel):
    """Parameters for weather lookup."""
    city: str
    units: str = "celsius"

@tool_call
def get_weather(params: WeatherParams) -> str:
    """
    Get weather information for a city.

    :param params: Weather parameters including city and units
    :trigger weather in
    :trigger temperature in
    :trigger forecast for
    :trigger weather forecast
    :examples:
    Weather in London
    Temperature in New York in fahrenheit
    """
    return f"Weather in {params.city}: 72°{params.units[0].upper()}"

# 3. Tool without docstring (demonstrates fallback)
@tool_call
def lookup_stock(symbol: str, include_history: bool = False) -> str:
    """Look up stock information.
    
    Trigger phrases: stock price of, get quote for, price of, stock quote
    Examples: Stock price of MSFT, Get quote for AAPL with history
    """
    return f"Stock {symbol}: $150.00"

# 4. Tool with complex parameters
class SearchParams(BaseModel):
    """Parameters for document search."""
    query: str
    max_results: int = 10
    include_metadata: bool = False
    filters: dict = {}

@tool_call
def search_documents(params: SearchParams) -> str:
    """Search for documents.
    
    Trigger phrases: search for, find documents, look for, search documents
    Examples: Search for "python programming", Find documents about "machine learning" with metadata
    """
    return f"Found {params.max_results} documents matching '{params.query}'"

def main():
    # Register all tools
    tools = get_tools_from_functions(
        calculate,
        get_weather,
        lookup_stock,
        search_documents
    )

    # Print registered tools
    print("\nRegistered Tools:")
    print("================")
    for tool in tools:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Trigger phrases: {tool.trigger_phrases}")
        print(f"Parameters: {[p.name for p in tool.parameters]}")
        print(f"Examples: {tool.examples}")

    # Test tool detection with various dynamic inputs
    test_cases = [
        # Calculator variations
        "Calculate 5 * 13",
        "What is 20 + 7?",
        "Compute 100 / 4",
        "Solve 15 - 8",
        "What's 3 squared?",
        "Calculate the sum of 10 and 20",
        
        # Weather variations
        "Weather in London",
        "Temperature in New York in fahrenheit",
        "Forecast for Tokyo",
        "Weather forecast for Paris",
        "What's the weather like in Berlin?",
        "Temperature in Sydney, Australia",
        "Weather in San Francisco in celsius",
        
        # Stock variations
        "Stock price of MSFT",
        "Get quote for AAPL with history",
        "Price of GOOGL",
        "Stock quote for TSLA",
        "What's the price of AMZN?",
        "Get stock price for NFLX with history",
        "Price of apple stock",
        "Stock price of microsoft",
        
        # Search variations
        "Search for python programming",
        "Find documents about machine learning with metadata",
        "Look for AI research papers",
        "Search documents for blockchain technology",
        "Find information about quantum computing",
        "Search for 'data science' tutorials",
        
        # Edge cases and ambiguous inputs
        "Tell me a joke",  # Should return None
        "What time is it?",  # Should return None
        "Hello world",  # Should return None
        "Price of something",  # Ambiguous - might match stock
        "Weather something",  # Ambiguous - might match weather
        "Calculate something",  # Ambiguous - might match calculator
    ]

    print("\nTesting Dynamic Tool Detection:")
    print("===============================")
    for user_input in test_cases:
        print(f"\nUser input: {user_input!r}")
        result = detect_tool_and_params(
            user_input=user_input,
            available_tools=tools,
            min_confidence=0.6
        )
        if result:
            print(f"✅ Detected tool: {result['tool']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Parameters: {result['parameters']}")
            if result['missing_parameters']:
                print(f"   ⚠️  Missing parameters: {result['missing_parameters']}")
            if result['validation_errors']:
                print(f"   ❌ Validation errors: {result['validation_errors']}")
        else:
            print("❌ No tool detected")

    # Generate and print JSON Schema
    print("\nJSON Schema:")
    print("===========")
    json_schema = get_openapi_schema_for_tools(tools)
    print(json.dumps(json_schema, indent=2))

if __name__ == "__main__":
    main()
