from tool_detector import tool_call, get_tools_from_functions, detect_tool_and_params
from pydantic import BaseModel

class WeatherParams(BaseModel):
    """Parameters for weather lookup."""
    city: str
    units: str = "celsius"

@tool_call
def lookup_stock(symbol: str, include_history: bool = False) -> str:
    """Look up stock information.
    
    Trigger phrases: stock price of, get quote for
    Examples: Stock price of MSFT, Get quote for AAPL with history
    """
    return f"Stock {symbol}: $150.00"

@tool_call
def get_weather(params: WeatherParams) -> str:
    """
    Get weather information for a city.

    :param params: Weather parameters including city and units
    :trigger weather in
    :trigger temperature in
    :examples:
    Weather in London
    Temperature in New York in fahrenheit
    """
    return f"Weather in {params.city}: 72°{params.units[0].upper()}"

# Test both tools
tools = get_tools_from_functions(lookup_stock, get_weather)

print("Registered tools:")
for tool in tools:
    print(f"  {tool.name}: {tool.trigger_phrases}")

test_cases = [
    "Stock price of MSFT",
    "Temperature in New York in fahrenheit",
    "Weather in London"
]

for test_input in test_cases:
    print(f"\nTesting: {test_input}")
    
    result = detect_tool_and_params(
        user_input=test_input,
        available_tools=tools,
        min_confidence=0.6
    )
    
    if result:
        print(f"  Detected tool: {result['tool']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Parameters: {result['parameters']}")
    else:
        print("  No tool detected") 