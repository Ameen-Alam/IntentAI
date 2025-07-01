#!/usr/bin/env python3
"""
Comprehensive example demonstrating all features of Tool Detector.

This example shows:
- Basic tool detection
- Decorator-based tool registration
- Parameter validation with Pydantic
- Schema generation
- CLI usage simulation
"""

import json
from typing import List, Optional

from pydantic import BaseModel, Field

from intentai import (
    detect_tool_and_params,
    tool_call,
    get_tools_from_functions,
    generate_json_schema,
    DetectionResult,
)


# Example 1: Basic Pydantic models for parameter validation
class WeatherParams(BaseModel):
    city: str = Field(..., description="City name to get weather for")
    country: str = Field(default="US", description="Country code")
    units: str = Field(default="celsius", description="Temperature units")


class CalculatorParams(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")
    precision: int = Field(default=2, ge=0, le=10, description="Decimal precision")


class EmailParams(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    cc: Optional[List[str]] = Field(default=None, description="CC recipients")


# Example 2: Decorator-based tool registration
@tool_call(
    name="get_weather",
    description="Get current weather information for a city",
    trigger_phrases=["weather in", "weather for", "temperature in", "what's the weather"],
    examples=[
        "weather in New York",
        "what's the temperature in London?",
        "weather for Tokyo",
        "how's the weather in Paris"
    ]
)
def get_weather(city: str, country: str = "US", units: str = "celsius") -> str:
    """Get weather information for a city."""
    return f"Weather in {city}, {country}: Sunny, 25°{units[0].upper()}"


@tool_call(
    name="calculator",
    description="Evaluate mathematical expressions",
    trigger_phrases=["calculate", "compute", "what is", "solve"],
    examples=[
        "calculate 2 + 2",
        "what is 10 * 5",
        "compute 100 / 4",
        "solve 15 + 27"
    ]
)
def calculator(expression: str, precision: int = 2) -> float:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression)
        return round(result, precision)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")


@tool_call(
    name="send_email",
    description="Send an email to specified recipients",
    trigger_phrases=["send email", "email to", "send message to"],
    examples=[
        "send email to john@example.com",
        "email to alice@company.com about meeting",
        "send message to team@project.com"
    ]
)
def send_email(to: str, subject: str, body: str, cc: Optional[List[str]] = None) -> str:
    """Send an email to the specified recipient."""
    cc_str = f", CC: {', '.join(cc)}" if cc else ""
    return f"Email sent to {to}{cc_str} with subject: {subject}"


@tool_call(
    name="search_web",
    description="Search the web for information",
    trigger_phrases=["search for", "find", "look up", "search web"],
    examples=[
        "search for Python tutorials",
        "find information about machine learning",
        "look up current events",
        "search web for best practices"
    ]
)
def search_web(query: str, max_results: int = 10) -> str:
    """Search the web for the given query."""
    return f"Found {max_results} results for: {query}"


def main():
    """Demonstrate all features of IntentAI."""
    print("[START] IntentAI Comprehensive Example\n")
    
    # Register all tools
    tools = get_tools_from_functions(
        get_weather,
        calculator,
        send_email,
        search_web
    )
    
    print(f"[INFO] Registered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    # Example 3: Test various user inputs
    test_inputs = [
        "What's the weather like in Tokyo?",
        "Calculate 15 * 7 + 3",
        "Send email to alice@company.com about the meeting tomorrow",
        "Search for Python best practices",
        "What is 100 divided by 4?",
        "Weather in Paris, France",
        "Find information about machine learning algorithms",
        "Compute 2 to the power of 10",
        "Email to john@example.com with subject 'Project Update'",
        "Look up current stock market trends"
    ]
    
    print("[TEST] Testing Tool Detection:")
    print("=" * 50)
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: '{user_input}'")
        
        # Detect tool and parameters
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
            
            # Simulate tool execution
            try:
                if result['tool'] == "get_weather":
                    city = result['parameters'].get("city", "")
                    country = result['parameters'].get("country", "US")
                    units = result['parameters'].get("units", "celsius")
                    output = get_weather(city, country, units)
                elif result['tool'] == "calculator":
                    expression = result['parameters'].get("expression", "")
                    precision = result['parameters'].get("precision", 2)
                    output = calculator(expression, precision)
                elif result['tool'] == "send_email":
                    to = result['parameters'].get("to", "")
                    subject = result['parameters'].get("subject", "")
                    body = result['parameters'].get("body", "")
                    cc = result['parameters'].get("cc")
                    output = send_email(to, subject, body, cc)
                elif result['tool'] == "search_web":
                    query = result['parameters'].get("query", "")
                    max_results = result['parameters'].get("max_results", 10)
                    output = search_web(query, max_results)
                else:
                    output = "Tool not implemented"
                
                print(f"   [OUTPUT] Output: {output}")
            except Exception as e:
                print(f"   [ERROR] Error: {e}")
        else:
            print("   [FAIL] No tool detected")
    
    # Example 4: Generate JSON Schema
    print("\n" + "=" * 50)
    print("[INFO] Generated JSON Schema:")
    print("=" * 50)
    
    schema = generate_json_schema(tools)
    print(json.dumps(schema, indent=2))
    
    # Example 5: CLI simulation
    print("\n" + "=" * 50)
    print("[CLI] CLI Simulation:")
    print("=" * 50)
    
    cli_inputs = [
        "weather in London",
        "calculate 2 + 2",
        "search for Python docs"
    ]
    
    for user_input in cli_inputs:
        print(f"\n$ intentai '{user_input}'")
        result = detect_tool_and_params(user_input, tools)
        
        if result:
            output = {
                "tool": result['tool'],
                "params": result['parameters'],
                "confidence": round(result['confidence'], 3)
            }
            print(json.dumps(output, indent=2))
        else:
            print("None")
    
    # Example 6: Confidence threshold demonstration
    print("\n" + "=" * 50)
    print("[TEST] Confidence Threshold Examples:")
    print("=" * 50)
    
    threshold_tests = [
        ("Weather in New York", 0.8),
        ("Calculate 5 + 3", 0.7),
        ("Send email to test@example.com", 0.6),
        ("Random text that doesn't match any tool", 0.5)
    ]
    
    for user_input, threshold in threshold_tests:
        result = detect_tool_and_params(user_input, tools)
        print(f"\nInput: '{user_input}'")
        print(f"Threshold: {threshold}")
        
        if result and result['confidence'] >= threshold:
            print(f"[OK] PASS: {result['tool']} (confidence: {result['confidence']:.3f})")
        elif result:
            print(f"[FAIL] BELOW THRESHOLD: {result['tool']} (confidence: {result['confidence']:.3f})")
        else:
            print("[FAIL] NO DETECTION")

    print("[DONE] Demo completed! IntentAI successfully detected tools and extracted")


if __name__ == "__main__":
    main()
