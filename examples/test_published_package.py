#!/usr/bin/env python3
"""
Test the published IntentAI package from PyPI.

This example demonstrates:
- Installing and using the published package
- Real-world intent parsing scenarios
- Integration with external APIs
- Error handling and edge cases
"""

import json
import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Import from the published package
try:
    from intentai import (
        detect_tool_and_params,
        tool_call,
        get_tools_from_functions,
        generate_json_schema,
        DetectionResult
    )
    print("[OK] Successfully imported IntentAI from PyPI!")
except ImportError as e:
    print(f"[FAIL] Failed to import IntentAI: {e}")
    print("Make sure to install it first: pip install intentai")
    exit(1)


# Real-world API integration examples
class WeatherData(BaseModel):
    city: str = Field(..., description="City name")
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition")
    humidity: int = Field(..., description="Humidity percentage")


class StockData(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    price: float = Field(..., description="Current stock price")
    change: float = Field(..., description="Price change")
    volume: int = Field(..., description="Trading volume")


# Mock API functions (in real world, these would call actual APIs)
def get_weather_api(city: str) -> WeatherData:
    """Mock weather API call."""
    # Simulate API response
    weather_data = {
        "New York": {"temperature": 22.5, "condition": "Sunny", "humidity": 65},
        "London": {"temperature": 15.2, "condition": "Cloudy", "humidity": 78},
        "Tokyo": {"temperature": 28.1, "condition": "Rainy", "humidity": 82},
        "Paris": {"temperature": 18.7, "condition": "Partly Cloudy", "humidity": 70},
    }
    
    if city in weather_data:
        data = weather_data[city]
        return WeatherData(
            city=city,
            temperature=data["temperature"],
            condition=data["condition"],
            humidity=data["humidity"]
        )
    else:
        # Default response for unknown cities
        return WeatherData(
            city=city,
            temperature=20.0,
            condition="Unknown",
            humidity=50
        )


def get_stock_api(symbol: str) -> StockData:
    """Mock stock API call."""
    # Simulate API response
    stock_data = {
        "AAPL": {"price": 150.25, "change": 2.15, "volume": 45000000},
        "GOOGL": {"price": 2750.80, "change": -15.20, "volume": 12000000},
        "MSFT": {"price": 320.45, "change": 5.30, "volume": 28000000},
        "TSLA": {"price": 850.75, "change": -25.50, "volume": 35000000},
    }
    
    if symbol.upper() in stock_data:
        data = stock_data[symbol.upper()]
        return StockData(
            symbol=symbol.upper(),
            price=data["price"],
            change=data["change"],
            volume=data["volume"]
        )
    else:
        # Default response for unknown symbols
        return StockData(
            symbol=symbol.upper(),
            price=100.0,
            change=0.0,
            volume=1000000
        )


# IntentAI tool definitions with real-world scenarios
@tool_call(
    name="get_weather",
    description="Get current weather information for a city",
    trigger_phrases=[
        "weather in", "weather for", "temperature in", "what's the weather",
        "how's the weather", "weather forecast", "current weather"
    ],
    examples=[
        "weather in New York",
        "what's the temperature in London?",
        "how's the weather in Tokyo",
        "weather forecast for Paris",
        "current weather in San Francisco"
    ]
)
def get_weather(city: str, units: str = "celsius") -> str:
    """Get weather information for a city using external API."""
    try:
        weather = get_weather_api(city)
        unit_symbol = "°C" if units == "celsius" else "°F"
        temp = weather.temperature if units == "celsius" else (weather.temperature * 9/5) + 32
        
        return f"Weather in {weather.city}: {temp:.1f}{unit_symbol}, {weather.condition}, Humidity: {weather.humidity}%"
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"


@tool_call(
    name="get_stock_price",
    description="Get current stock price and market data",
    trigger_phrases=[
        "stock price of", "stock quote for", "price of", "stock value",
        "market price", "stock market", "trading price"
    ],
    examples=[
        "stock price of AAPL",
        "what's the price of GOOGL?",
        "stock quote for MSFT",
        "market price of TSLA",
        "trading price for AMZN"
    ]
)
def get_stock_price(symbol: str, include_volume: bool = False) -> str:
    """Get stock price information using external API."""
    try:
        stock = get_stock_api(symbol)
        change_symbol = "+" if stock.change >= 0 else ""
        volume_info = f", Volume: {stock.volume:,}" if include_volume else ""
        
        return f"{stock.symbol}: ${stock.price:.2f} ({change_symbol}{stock.change:.2f}){volume_info}"
    except Exception as e:
        return f"Error getting stock price for {symbol}: {str(e)}"


@tool_call(
    name="calculate",
    description="Perform mathematical calculations",
    trigger_phrases=[
        "calculate", "compute", "what is", "solve", "math",
        "add", "subtract", "multiply", "divide", "percentage"
    ],
    examples=[
        "calculate 15 * 7 + 3",
        "what is 100 divided by 4?",
        "compute 2 to the power of 10",
        "solve 25 + 17 - 8",
        "calculate 15% of 200"
    ]
)
def calculate(expression: str, precision: int = 2) -> str:
    """Evaluate mathematical expressions safely."""
    try:
        # Basic safety check - only allow basic math operations
        allowed_chars = set("0123456789+-*/.()% ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        # Replace percentage with division
        expression = expression.replace("%", "/100")
        
        result = eval(expression)
        return f"Result: {round(result, precision)}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool_call(
    name="search_web",
    description="Search the web for information",
    trigger_phrases=[
        "search for", "find", "look up", "search web", "google",
        "find information about", "search about", "look for"
    ],
    examples=[
        "search for Python tutorials",
        "find information about machine learning",
        "look up current events",
        "search web for best practices",
        "google latest technology news"
    ]
)
def search_web(query: str, max_results: int = 5) -> str:
    """Mock web search functionality."""
    # In a real implementation, this would call a search API
    return f"Found {max_results} results for: '{query}' (Mock search - would integrate with Google/Bing API)"


def test_published_package():
    """Test the published IntentAI package with real-world scenarios."""
    print("[TEST] Testing Published IntentAI Package")
    print("=" * 50)
    
    # Register all tools
    tools = get_tools_from_functions(
        get_weather,
        get_stock_price,
        calculate,
        search_web
    )
    
    print(f"[INFO] Registered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    # Test scenarios
    test_scenarios = [
        # Weather scenarios
        "What's the weather like in New York?",
        "Weather in London please",
        "How's the temperature in Tokyo?",
        "Weather forecast for Paris",
        
        # Stock scenarios
        "What's the stock price of AAPL?",
        "Stock quote for GOOGL",
        "Market price of MSFT",
        "Trading price for TSLA with volume",
        
        # Calculator scenarios
        "Calculate 25 * 4 + 10",
        "What is 100 divided by 5?",
        "Compute 2 to the power of 8",
        "Solve 15 + 27 - 8",
        
        # Search scenarios
        "Search for Python programming tutorials",
        "Find information about artificial intelligence",
        "Look up latest technology news",
        "Search web for machine learning best practices",
        
        # Edge cases
        "Tell me a joke",  # Should return None
        "What time is it?",  # Should return None
        "Random text that doesn't match",  # Should return None
    ]
    
    print("[TEST] Testing Intent Detection:")
    print("=" * 50)
    
    for i, user_input in enumerate(test_scenarios, 1):
        print(f"\n{i}. Input: '{user_input}'")
        
        # Detect intent
        result = detect_tool_and_params(user_input, tools)
        
        if result:
            # Handle both single result and list of results
            if isinstance(result, list):
                # Multiple candidates found
                print(f"   [WARN] Multiple candidates detected:")
                for i, res in enumerate(result, 1):
                    print(f"     {i}. {res['tool']} (confidence: {res['confidence']:.3f})")
                # Use the first result for execution
                result = result[0]
            else:
                # Single result
                print(f"   [OK] Detected: {result['tool']}")
                print(f"   [INFO] Confidence: {result['confidence']:.3f}")
                print(f"   [PARAM] Parameters: {result['parameters']}")
            
            # Execute the detected tool
            try:
                if result['tool'] == "get_weather":
                    city = result['parameters'].get("city", "")
                    units = result['parameters'].get("units", "celsius")
                    output = get_weather(city, units)
                elif result['tool'] == "get_stock_price":
                    symbol = result['parameters'].get("symbol", "")
                    include_volume = result['parameters'].get("include_volume", False)
                    output = get_stock_price(symbol, include_volume)
                elif result['tool'] == "calculate":
                    expression = result['parameters'].get("expression", "")
                    precision = result['parameters'].get("precision", 2)
                    output = calculate(expression, precision)
                elif result['tool'] == "search_web":
                    query = result['parameters'].get("query", "")
                    max_results = result['parameters'].get("max_results", 5)
                    output = search_web(query, max_results)
                else:
                    output = "Tool not implemented"
                
                print(f"   [OUTPUT] Output: {output}")
            except Exception as e:
                print(f"   [ERROR] Error: {e}")
        else:
            print("   [FAIL] No intent detected")
    
    # Test confidence thresholds
    print("\n" + "=" * 50)
    print("[TEST] Confidence Threshold Testing:")
    print("=" * 50)
    
    confidence_tests = [
        ("Weather in New York", 0.8),
        ("Stock price of AAPL", 0.7),
        ("Calculate 2 + 2", 0.6),
        ("Search for Python", 0.5),
        ("Random text", 0.3)
    ]
    
    for user_input, threshold in confidence_tests:
        result = detect_tool_and_params(user_input, tools)
        print(f"\nInput: '{user_input}' (threshold: {threshold})")
        
        if result and result['confidence'] >= threshold:
            print(f"[OK] PASS: {result['tool']} (confidence: {result['confidence']:.3f})")
        elif result:
            print(f"[FAIL] BELOW THRESHOLD: {result['tool']} (confidence: {result['confidence']:.3f})")
        else:
            print("[FAIL] NO DETECTION")
    
    # Generate and display schema
    print("\n" + "=" * 50)
    print("[INFO] Generated JSON Schema:")
    print("=" * 50)
    
    schema = generate_json_schema(tools)
    print(json.dumps(schema, indent=2))
    
    print("\n[DONE] Published package test completed successfully!")


if __name__ == "__main__":
    test_published_package() 