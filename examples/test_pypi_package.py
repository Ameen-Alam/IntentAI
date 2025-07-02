#!/usr/bin/env python3
"""
Test the published IntentAI package from PyPI.

This script verifies that the published package works correctly
with all core features including tool detection, parameter extraction,
and schema generation.

NOTE: All intentai imports are at the top-level for global access.
"""

import json
import sys
from typing import Dict, Any

# Import all core API at the top-level for global access in all test functions
from intentai import (
    detect_tool_and_params,
    tool_call,
    get_tools_from_functions,
    generate_json_schema,
    DetectionResult,
    Tool
)

def test_basic_imports():
    """Test that all core imports are present and callable."""
    print("🔍 Testing basic imports...")
    try:
        assert callable(detect_tool_and_params)
        assert callable(tool_call)
        assert callable(get_tools_from_functions)
        assert callable(generate_json_schema)
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tool_registration():
    """Test tool registration with decorator."""
    print("\n🔧 Testing tool registration...")
    
    @tool_call(
        name="test_calculator",
        description="A simple calculator for testing",
        trigger_phrases=["calculate", "compute", "math"],
        examples=["calculate 2+2", "compute 10*5"]
    )
    def calculate(expression: str) -> float:
        """Calculate mathematical expressions."""
        return eval(expression)
    
    @tool_call(
        name="test_weather",
        description="Get weather information",
        trigger_phrases=["weather", "temperature"],
        examples=["weather in London", "temperature in Tokyo"]
    )
    def get_weather(city: str, units: str = "celsius") -> str:
        """Get weather for a city."""
        return f"Weather in {city}: 20°{units[0].upper()}"
    
    try:
        tools = get_tools_from_functions(calculate, get_weather)
        print(f"✅ Registered {len(tools)} tools successfully!")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        return tools
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
        return None

def test_tool_detection(tools):
    """Test tool detection and parameter extraction."""
    print("\n🎯 Testing tool detection...")
    
    test_cases = [
        ("calculate 2+2", "test_calculator"),
        ("weather in London", "test_weather"),
        ("compute 10*5", "test_calculator"),
        ("temperature in Tokyo", "test_weather"),
        ("random text that doesn't match", None)
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected_tool in test_cases:
        try:
            result = detect_tool_and_params(input_text, tools)
            
            if expected_tool is None:
                if result is None:
                    print(f"✅ '{input_text}' -> No tool detected (expected)")
                    passed += 1
                else:
                    print(f"❌ '{input_text}' -> Detected {result['tool']} (expected None)")
            else:
                if result and result['tool'] == expected_tool:
                    print(f"✅ '{input_text}' -> {result['tool']} (confidence: {result['confidence']:.2f})")
                    passed += 1
                else:
                    detected = result['tool'] if result else "None"
                    print(f"❌ '{input_text}' -> {detected} (expected {expected_tool})")
                    
        except Exception as e:
            print(f"❌ Error testing '{input_text}': {e}")
    
    print(f"\n📊 Detection accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
    return passed == total

def test_schema_generation(tools):
    """Test JSON schema generation."""
    print("\n📋 Testing schema generation...")
    
    try:
        schema = generate_json_schema(tools)
        
        # Validate schema structure
        required_keys = ["$schema", "type", "properties", "required"]
        if all(key in schema for key in required_keys):
            print("✅ Schema generated successfully!")
            print(f"   - Schema type: {schema['type']}")
            print(f"   - Tools in schema: {len(schema['properties']['tools']['items']['properties'])}")
            
            # Pretty print a sample of the schema
            print("\n📄 Schema sample:")
            print(json.dumps(schema, indent=2)[:500] + "...")
            return True
        else:
            print("❌ Schema missing required keys")
            return False
            
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        return False

def test_confidence_thresholds(tools):
    """Test confidence threshold functionality."""
    print("\n🎚️ Testing confidence thresholds...")
    
    test_cases = [
        ("calculate 2+2", 0.8, True),   # Should pass high threshold
        ("weather in London", 0.6, True),  # Should pass medium threshold
        ("random text", 0.3, False),    # Should fail low threshold
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, threshold, should_pass in test_cases:
        try:
            result = detect_tool_and_params(input_text, tools, min_confidence=threshold)
            
            if should_pass:
                if result and result['confidence'] >= threshold:
                    print(f"✅ '{input_text}' (threshold {threshold}) -> PASS")
                    passed += 1
                else:
                    print(f"❌ '{input_text}' (threshold {threshold}) -> FAIL")
            else:
                if result is None or result['confidence'] < threshold:
                    print(f"✅ '{input_text}' (threshold {threshold}) -> PASS (no detection)")
                    passed += 1
                else:
                    print(f"❌ '{input_text}' (threshold {threshold}) -> FAIL (unexpected detection)")
                    
        except Exception as e:
            print(f"❌ Error testing '{input_text}': {e}")
    
    print(f"\n📊 Threshold accuracy: {passed}/{total} ({passed/total*100:.1f}%)")
    return passed == total

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🛡️ Testing error handling...")
    
    try:
        # Test with empty tools list
        result = detect_tool_and_params("test input", [])
        if result is None:
            print("✅ Empty tools list handled correctly")
        else:
            print("❌ Empty tools list should return None")
            return False
        
        # Test with invalid input
        result = detect_tool_and_params("", [])
        if result is None:
            print("✅ Empty input handled correctly")
        else:
            print("❌ Empty input should return None")
            return False
        
        # Test with None input
        result = detect_tool_and_params(None, [])
        if result is None:
            print("✅ None input handled correctly")
        else:
            print("❌ None input should return None")
            return False
            
        print("✅ All error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 IntentAI PyPI Package Test Suite")
    print("=" * 50)
    
    # Test basic imports
    if not test_basic_imports():
        print("\n❌ Basic imports failed. Exiting.")
        sys.exit(1)
    
    # Test tool registration
    tools = test_tool_registration()
    if not tools:
        print("\n❌ Tool registration failed. Exiting.")
        sys.exit(1)
    
    # Test tool detection
    detection_ok = test_tool_detection(tools)
    
    # Test schema generation
    schema_ok = test_schema_generation(tools)
    
    # Test confidence thresholds
    threshold_ok = test_confidence_thresholds(tools)
    
    # Test error handling
    error_ok = test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", True),
        ("Tool Registration", bool(tools)),
        ("Tool Detection", detection_ok),
        ("Schema Generation", schema_ok),
        ("Confidence Thresholds", threshold_ok),
        ("Error Handling", error_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! IntentAI PyPI package is working correctly!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 