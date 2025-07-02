#!/usr/bin/env python3
"""
Test the local IntentAI code (development version).

This example demonstrates:
- Testing local code without installing from PyPI
- Development workflow testing
- Local debugging and validation
- Integration testing with local changes
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Add the local package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from local code
try:
    from intentai import (
        detect_tool_and_params,
        tool_call,
        get_tools_from_functions,
        generate_json_schema,
        DetectionResult,
        Tool
    )
    print("[OK] Successfully imported IntentAI from local code!")
except ImportError as e:
    print(f"[FAIL] Failed to import IntentAI from local code: {e}")
    print("Make sure you're running this from the project root directory")
    exit(1)


# Test data models
class UserProfile(BaseModel):
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    age: int = Field(..., ge=0, le=120, description="User's age")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")


class ProductInfo(BaseModel):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")
    category: str = Field(..., description="Product category")


# Local development tools
@tool_call(
    name="create_user",
    description="Create a new user profile",
    trigger_phrases=[
        "create user", "add user", "new user", "register user",
        "sign up user", "create account", "add account"
    ],
    examples=[
        "create user John Doe with email john@example.com",
        "add user Alice Smith age 25",
        "new user Bob Johnson bob@company.com",
        "register user with preferences"
    ]
)
def create_user(name: str, email: str, age: int, preferences: Dict[str, Any] = None) -> str:
    """Create a new user profile."""
    try:
        user = UserProfile(
            name=name,
            email=email,
            age=age,
            preferences=preferences or {}
        )
        return f"[OK] User created: {user.name} ({user.email}), Age: {user.age}"
    except Exception as e:
        return f"[ERROR] Error creating user: {str(e)}"


@tool_call(
    name="add_product",
    description="Add a new product to inventory",
    trigger_phrases=[
        "add product", "create product", "new product", "insert product",
        "add item", "create item", "new item"
    ],
    examples=[
        "add product Laptop with price 999.99",
        "create product iPhone 15 category Electronics",
        "new product Book price 29.99",
        "add item Coffee Mug 15.50 category Kitchen"
    ]
)
def add_product(name: str, price: float, category: str, product_id: str = None) -> str:
    """Add a new product to the inventory."""
    try:
        if not product_id:
            product_id = f"PROD_{len(name)}_{int(price)}"
        
        product = ProductInfo(
            id=product_id,
            name=name,
            price=price,
            category=category
        )
        return f"[OK] Product added: {product.name} (ID: {product.id}), Price: ${product.price}, Category: {product.category}"
    except Exception as e:
        return f"[ERROR] Error adding product: {str(e)}"


@tool_call(
    name="analyze_text",
    description="Analyze text for sentiment and key information",
    trigger_phrases=[
        "analyze text", "text analysis", "sentiment analysis", "analyze sentiment",
        "text processing", "analyze content", "process text"
    ],
    examples=[
        "analyze text 'I love this product!'",
        "sentiment analysis of 'This is terrible'",
        "analyze content for key information",
        "text processing of user feedback"
    ]
)
def analyze_text(text: str, include_sentiment: bool = True, extract_keywords: bool = True) -> str:
    """Analyze text for sentiment and extract key information."""
    try:
        # Simple mock analysis
        words = text.lower().split()
        word_count = len(words)
        
        # Mock sentiment analysis
        positive_words = ['love', 'great', 'good', 'excellent', 'amazing', 'wonderful']
        negative_words = ['hate', 'terrible', 'bad', 'awful', 'horrible', 'disappointing']
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        sentiment = "positive" if positive_count > negative_count else "negative" if negative_count > positive_count else "neutral"
        
        # Mock keyword extraction
        keywords = [word for word in words if len(word) > 4][:5]
        
        result = f"Text Analysis Results:\n"
        result += f"- Word count: {word_count}\n"
        
        if include_sentiment:
            result += f"- Sentiment: {sentiment}\n"
        
        if extract_keywords:
            result += f"- Keywords: {', '.join(keywords) if keywords else 'None'}\n"
        
        return result
    except Exception as e:
        return f"[ERROR] Error analyzing text: {str(e)}"


@tool_call(
    name="generate_report",
    description="Generate a report based on data",
    trigger_phrases=[
        "generate report", "create report", "make report", "build report",
        "report generation", "create summary", "generate summary"
    ],
    examples=[
        "generate report for sales data",
        "create report for user analytics",
        "make report for inventory status",
        "generate summary of monthly performance"
    ]
)
def generate_report(report_type: str, data_source: str, format: str = "text") -> str:
    """Generate a report based on specified parameters."""
    try:
        # Mock report generation
        report = f"[REPORT] {report_type.title()} Report\n"
        report += f"Source: {data_source}\n"
        report += f"Format: {format}\n"
        report += f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Mock data
        if "sales" in report_type.lower():
            report += "Sales Summary:\n- Total Revenue: $125,000\n- Units Sold: 1,250\n- Growth: +15%\n"
        elif "user" in report_type.lower():
            report += "User Analytics:\n- Active Users: 5,420\n- New Signups: 234\n- Retention Rate: 87%\n"
        elif "inventory" in report_type.lower():
            report += "Inventory Status:\n- Total Items: 2,450\n- Low Stock: 15 items\n- Out of Stock: 3 items\n"
        else:
            report += "General Report:\n- Data points: 1,000\n- Processing time: 2.3s\n- Status: Complete\n"
        
        return report
    except Exception as e:
        return f"[ERROR] Error generating report: {str(e)}"


def test_local_code():
    """Test the local IntentAI code with development scenarios."""
    print("[TEST] Testing Local IntentAI Code")
    print("=" * 50)
    
    # Register all tools
    tools = get_tools_from_functions(
        create_user,
        add_product,
        analyze_text,
        generate_report
    )
    
    print(f"[INFO] Registered {len(tools)} local tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()
    
    # Test local development scenarios
    test_scenarios = [
        # User management scenarios
        "Create user John Smith with email john@example.com age 30",
        "Add user Alice Johnson alice@company.com 25",
        "New user Bob Wilson bob@test.org 35 with preferences",
        
        # Product management scenarios
        "Add product MacBook Pro with price 1299.99 category Electronics",
        "Create product Coffee Mug 12.50 category Kitchen",
        "New item Wireless Headphones 89.99 category Audio",
        
        # Text analysis scenarios
        "Analyze text 'I absolutely love this amazing product!'",
        "Sentiment analysis of 'This is terrible and disappointing'",
        "Text processing for user feedback analysis",
        
        # Report generation scenarios
        "Generate report for sales data from database",
        "Create report for user analytics from API",
        "Make report for inventory status from CSV",
        
        # Edge cases and error handling
        "Create user with invalid email",  # Should handle gracefully
        "Add product with negative price",  # Should validate
        "Analyze empty text",  # Should handle edge case
        "Generate report without data source",  # Should handle missing params
    ]
    
    print("\n[TEST] Testing Local Intent Detection:")
    print("=" * 50)
    
    for i, user_input in enumerate(test_scenarios, 1):
        print(f"\n{i}. Input: '{user_input}'")
        # Debug: print trigger phrases and fuzzy match scores
        for tool in tools:
            from intentai.detector import _fuzzy_trigger_match
            matched_trigger, score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
            print(f"   [DEBUG] Tool '{tool.name}' triggers: {tool.trigger_phrases}")
            print(f"   [DEBUG] Best match: '{matched_trigger}' (score: {score:.3f})")
        # Detect intent
        result = detect_tool_and_params(user_input, tools)
        print(f"   [DEBUG] Type of result: {type(result)}")
        
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
                if result['tool'] == "create_user":
                    name = result['parameters'].get("name", "")
                    email = result['parameters'].get("email", "")
                    age = result['parameters'].get("age", 0)
                    preferences = result['parameters'].get("preferences", {})
                    output = create_user(name, email, age, preferences)
                elif result['tool'] == "add_product":
                    name = result['parameters'].get("name", "")
                    price = result['parameters'].get("price", 0.0)
                    category = result['parameters'].get("category", "")
                    product_id = result['parameters'].get("product_id")
                    output = add_product(name, price, category, product_id)
                elif result['tool'] == "analyze_text":
                    text = result['parameters'].get("text", "")
                    include_sentiment = result['parameters'].get("include_sentiment", True)
                    extract_keywords = result['parameters'].get("extract_keywords", True)
                    output = analyze_text(text, include_sentiment, extract_keywords)
                elif result['tool'] == "generate_report":
                    report_type = result['parameters'].get("report_type", "")
                    data_source = result['parameters'].get("data_source", "")
                    format = result['parameters'].get("format", "text")
                    output = generate_report(report_type, data_source, format)
                else:
                    output = "Tool not implemented"
                
                print(f"   [OUTPUT] Output: {output}")
            except Exception as e:
                print(f"   [ERROR] Error: {e}")
        else:
            print("   [FAIL] No intent detected")
    
    # Test local development features
    print("\n" + "=" * 50)
    print("[TEST] Local Development Features:")
    print("=" * 50)
    
    # Test parameter validation
    print("\n1. Testing Parameter Validation:")
    try:
        # This should fail validation
        invalid_user = UserProfile(name="", email="invalid", age=-5)
        print("[FAIL] Validation should have failed")
    except Exception as e:
        print(f"[OK] Validation caught error: {e}")
    
    # Test tool registration
    print("\n2. Testing Tool Registration:")
    print(f"   - Total tools registered: {len(tools)}")
    print(f"   - Tool names: {[tool.name for tool in tools]}")
    
    # Test schema generation
    print("\n3. Testing Schema Generation:")
    schema = generate_json_schema(tools)
    print(f"   - Schema generated successfully")
    print(f"   - Contains {len(schema.get('paths', {}))} tool paths")
    
    # Test confidence scoring
    print("\n4. Testing Confidence Scoring:")
    confidence_tests = [
        ("Create user John Doe", 0.7),
        ("Add product Laptop", 0.6),
        ("Analyze text content", 0.5),
        ("Generate sales report", 0.8)
    ]
    
    for user_input, expected_min in confidence_tests:
        result = detect_tool_and_params(user_input, tools)
        if result:
            confidence = result['confidence']
            status = "[OK]" if confidence >= expected_min else "[WARN]"
            print(f"   {status} '{user_input}': {confidence:.3f} (expected >={expected_min})")
        else:
            print(f"   [FAIL] '{user_input}': No detection")
    
    print("\n[DONE] Local code test completed successfully!")


if __name__ == "__main__":
    test_local_code() 