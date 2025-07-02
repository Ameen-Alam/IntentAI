#!/usr/bin/env python3
"""
Dynamic IntentAI Demo - Shows how the system works with ANY tools
No hardcoded logic, completely generic parameter extraction and detection.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import intentai
sys.path.insert(0, str(Path(__file__).parent.parent))

from intentai import tool_call, get_tools_from_functions, detect_tool_and_params


# ============================================================================
# EXAMPLE 1: Simple Tools with Dynamic Parameter Extraction
# ============================================================================

@tool_call(
    name="calculator",
    description="Perform mathematical calculations",
    trigger_phrases=["calculate", "compute", "solve", "what is", "math"],
    examples=["calculate 2+2", "what is 10 * 5", "solve 15 / 3"]
)
def calculate(expression: str) -> str:
    """Calculate mathematical expressions."""
    try:
        # Safe evaluation of mathematical expressions
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool_call(
    name="weather_checker",
    description="Get weather information for a location",
    trigger_phrases=["weather", "temperature", "forecast", "climate"],
    examples=["weather in London", "temperature in Tokyo", "forecast for Paris"]
)
def get_weather(location: str, units: str = "celsius") -> str:
    """Get weather information for a location."""
    # Mock weather data
    weather_data = {
        "london": {"temp": 18, "condition": "cloudy"},
        "tokyo": {"temp": 25, "condition": "sunny"},
        "paris": {"temp": 22, "condition": "rainy"},
        "new york": {"temp": 15, "condition": "windy"}
    }
    
    location_lower = location.lower()
    if location_lower in weather_data:
        data = weather_data[location_lower]
        temp = data["temp"]
        if units.lower() == "fahrenheit":
            temp = (temp * 9/5) + 32
        return f"Weather in {location}: {temp}°{units[0].upper()}, {data['condition']}"
    else:
        return f"Weather data not available for {location}"


# ============================================================================
# EXAMPLE 2: Complex Tools with Multiple Parameter Types
# ============================================================================

@tool_call(
    name="user_manager",
    description="Manage user accounts and profiles",
    trigger_phrases=["create user", "add user", "user management", "profile"],
    examples=["create user John with email john@example.com", "add user Alice age 25"]
)
def create_user(
    name: str, 
    email: str, 
    age: int = None, 
    is_active: bool = True,
    preferences: list = None
) -> str:
    """Create a new user account."""
    user_info = {
        "name": name,
        "email": email,
        "age": age,
        "is_active": is_active,
        "preferences": preferences or []
    }
    return f"User created: {user_info}"


@tool_call(
    name="data_analyzer",
    description="Analyze data and generate reports",
    trigger_phrases=["analyze", "report", "data analysis", "statistics"],
    examples=["analyze sales data", "generate report for Q1", "data analysis with charts"]
)
def analyze_data(
    dataset: str,
    include_charts: bool = False,
    format: str = "pdf",
    filters: dict = None
) -> str:
    """Analyze data and generate reports."""
    analysis = {
        "dataset": dataset,
        "charts": include_charts,
        "format": format,
        "filters": filters or {},
        "summary": "Analysis completed successfully"
    }
    return f"Analysis result: {analysis}"


# ============================================================================
# EXAMPLE 3: API Integration Tools (Generic)
# ============================================================================

@tool_call(
    name="api_client",
    description="Make API calls to external services",
    trigger_phrases=["api call", "fetch data", "http request", "rest api"],
    examples=["fetch data from api", "api call to users endpoint", "http request to /api/data"]
)
def make_api_call(
    endpoint: str,
    method: str = "GET",
    headers: dict = None,
    data: dict = None,
    timeout: int = 30
) -> str:
    """Make an API call to an external service."""
    # Mock API call
    api_info = {
        "endpoint": endpoint,
        "method": method.upper(),
        "headers": headers or {},
        "data": data or {},
        "timeout": timeout,
        "status": "success"
    }
    return f"API call completed: {api_info}"


# ============================================================================
# EXAMPLE 4: File Operations (Generic)
# ============================================================================

@tool_call(
    name="file_processor",
    description="Process files and perform file operations",
    trigger_phrases=["file", "process file", "read file", "write file"],
    examples=["read file data.txt", "process file with encoding utf-8", "write file output.json"]
)
def process_file(
    filename: str,
    operation: str = "read",
    encoding: str = "utf-8",
    create_backup: bool = False
) -> str:
    """Process files with various operations."""
    file_info = {
        "filename": filename,
        "operation": operation,
        "encoding": encoding,
        "backup": create_backup,
        "status": "completed"
    }
    return f"File operation: {file_info}"


# ============================================================================
# DEMO FUNCTION
# ============================================================================

def run_dynamic_demo():
    """Run the dynamic demo showing IntentAI working with any tools."""
    print("🚀 IntentAI Dynamic System Demo")
    print("=" * 60)
    print("This demo shows how IntentAI works with ANY tools without hardcoded logic.")
    print("All parameter extraction and detection is completely dynamic and generic.")
    print()
    
    # Get all tools
    tools = get_tools_from_functions(
        calculate,
        get_weather,
        create_user,
        analyze_data,
        make_api_call,
        process_file
    )
    
    print(f"📋 Registered {len(tools)} tools:")
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}: {tool.description}")
        print(f"   Triggers: {', '.join(tool.trigger_phrases[:3])}")
        print(f"   Parameters: {len(tool.parameters)}")
        print()
    
    # Test cases - completely natural language
    test_cases = [
        # Simple calculations
        "calculate 15 + 25",
        "what is 100 / 4",
        "solve 2 * 8 + 3",
        
        # Weather queries
        "weather in London",
        "temperature in Tokyo with fahrenheit",
        "forecast for Paris",
        
        # User management
        "create user John with email john@example.com",
        "add user Alice age 25 is_active false",
        "create user Bob email bob@test.com preferences ['admin', 'user']",
        
        # Data analysis
        "analyze sales data with charts",
        "generate report for Q1 format json",
        "data analysis with filters {'region': 'europe'}",
        
        # API calls
        "fetch data from /api/users",
        "api call to /api/data method POST",
        "http request to /api/weather headers {'auth': 'token'}",
        
        # File operations
        "read file data.txt",
        "process file config.json operation write",
        "write file output.csv encoding utf-8 create_backup true",
        
        # Edge cases
        "what's the weather like?",
        "can you help me calculate something?",
        "I need to create a new user account"
    ]
    
    print("🧪 Testing Dynamic Detection:")
    print("-" * 60)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input: '{test_input}'")
        
        result = detect_tool_and_params(test_input, tools)
        
        if result:
            if isinstance(result, list):
                print(f"   Multiple matches ({len(result)}):")
                for j, res in enumerate(result, 1):
                    print(f"   {j}. {res['tool']} (Confidence: {res['confidence']:.2f})")
                    if res['parameters']:
                        print(f"      Parameters: {res['parameters']}")
            else:
                print(f"   Detected: {result['tool']} (Confidence: {result['confidence']:.2f})")
                if result['parameters']:
                    print(f"   Parameters: {result['parameters']}")
                if result['missing_parameters']:
                    print(f"   Missing: {result['missing_parameters']}")
        else:
            print("   No tool detected")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! IntentAI successfully detected tools and extracted")
    print("   parameters dynamically without any hardcoded logic.")
    print("\n🎯 Key Features Demonstrated:")
    print("   • Generic parameter extraction for any parameter type")
    print("   • Dynamic trigger phrase matching")
    print("   • Automatic confidence scoring")
    print("   • Support for any tool function")
    print("   • No hardcoded parameter names or patterns")


if __name__ == "__main__":
    run_dynamic_demo() 