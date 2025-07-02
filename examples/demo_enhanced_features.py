#!/usr/bin/env python3
"""
Enhanced IntentAI Features Demo

This script demonstrates all the professional improvements made to the IntentAI system:
- Enhanced parameter extraction
- Improved confidence scoring
- Better error handling
- Professional logging
- Robust type safety
- Advanced CLI features
"""

import sys
import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# Add the local package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from intentai import (
    tool_call,
    get_tools_from_functions,
    detect_tool_and_params,
    generate_json_schema,
    DetectionResult
)


# Enhanced data models with validation
class UserProfile(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name")
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address")
    age: int = Field(..., ge=0, le=120, description="User's age (0-120)")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")


class ProductInfo(BaseModel):
    name: str = Field(..., min_length=1, description="Product name")
    price: float = Field(..., ge=0, description="Product price (non-negative)")
    category: str = Field(..., min_length=1, description="Product category")
    description: Optional[str] = Field(None, description="Product description")


# Enhanced tools with better parameter extraction
@tool_call(
    name="create_user",
    description="Create a new user profile with validation",
    trigger_phrases=[
        "create user", "add user", "new user", "register user",
        "sign up user", "create account", "add account"
    ],
    examples=[
        "create user John Doe with email john@example.com age 25",
        "add user Alice Smith alice@company.com 30",
        "new user Bob Johnson bob@test.org 35 with preferences"
    ]
)
def create_user(name: str, email: str, age: int, preferences: Dict[str, Any] = None) -> str:
    """
    Create a new user profile with comprehensive validation.
    
    Triggers: create user, add user, new user, register user
    Examples: 
    - "create user John Doe with email john@example.com age 25"
    - "add user Alice Smith alice@company.com 30"
    """
    try:
        user = UserProfile(
            name=name,
            email=email,
            age=age,
            preferences=preferences or {}
        )
        return f"✅ User created successfully: {user.name} ({user.email}), Age: {user.age}"
    except Exception as e:
        return f"❌ Error creating user: {str(e)}"


@tool_call(
    name="add_product",
    description="Add a new product to inventory with validation",
    trigger_phrases=[
        "add product", "create product", "new product", "insert product",
        "add item", "create item", "new item"
    ],
    examples=[
        "add product MacBook Pro with price 1299.99 category Electronics",
        "create product Coffee Mug 12.50 category Kitchen",
        "new item Wireless Headphones 89.99 category Audio"
    ]
)
def add_product(name: str, price: float, category: str, description: str = None) -> str:
    """
    Add a new product to the inventory with validation.
    
    Triggers: add product, create product, new product, insert product
    Examples:
    - "add product MacBook Pro with price 1299.99 category Electronics"
    - "create product Coffee Mug 12.50 category Kitchen"
    """
    try:
        product = ProductInfo(
            name=name,
            price=price,
            category=category,
            description=description
        )
        return f"✅ Product added: {product.name}, Price: ${product.price:.2f}, Category: {product.category}"
    except Exception as e:
        return f"❌ Error adding product: {str(e)}"


@tool_call(
    name="analyze_text",
    description="Analyze text for sentiment and extract key information",
    trigger_phrases=[
        "analyze text", "text analysis", "sentiment analysis", "analyze sentiment",
        "text processing", "analyze content", "process text"
    ],
    examples=[
        "analyze text 'I absolutely love this amazing product!'",
        "sentiment analysis of 'This is terrible and disappointing'",
        "text processing for user feedback analysis"
    ]
)
def analyze_text(text: str, include_sentiment: bool = True, extract_keywords: bool = True) -> str:
    """
    Analyze text for sentiment and extract key information.
    
    Triggers: analyze text, text analysis, sentiment analysis, analyze sentiment
    Examples:
    - "analyze text 'I absolutely love this amazing product!'"
    - "sentiment analysis of 'This is terrible and disappointing'"
    """
    try:
        if not text or not text.strip():
            return "❌ Error: No text provided for analysis"
        
        words = text.lower().split()
        word_count = len(words)
        
        # Enhanced sentiment analysis
        positive_words = ['love', 'great', 'good', 'excellent', 'amazing', 'wonderful', 'fantastic', 'perfect']
        negative_words = ['hate', 'terrible', 'bad', 'awful', 'horrible', 'disappointing', 'worst', 'useless']
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Enhanced keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words][:5]
        
        result = f"📊 Text Analysis Results:\n"
        result += f"   • Word count: {word_count}\n"
        
        if include_sentiment:
            result += f"   • Sentiment: {sentiment} (positive: {positive_count}, negative: {negative_count})\n"
        
        if extract_keywords:
            result += f"   • Keywords: {', '.join(keywords) if keywords else 'None'}\n"
        
        return result
    except Exception as e:
        return f"❌ Error analyzing text: {str(e)}"


@tool_call(
    name="generate_report",
    description="Generate comprehensive reports based on data",
    trigger_phrases=[
        "generate report", "create report", "make report", "build report",
        "report generation", "create summary", "generate summary"
    ],
    examples=[
        "generate report for sales data from database",
        "create report for user analytics from API",
        "make report for inventory status from CSV"
    ]
)
def generate_report(report_type: str, data_source: str, format: str = "text", include_charts: bool = False) -> str:
    """
    Generate comprehensive reports based on specified parameters.
    
    Triggers: generate report, create report, make report, build report
    Examples:
    - "generate report for sales data from database"
    - "create report for user analytics from API"
    """
    try:
        report = f"📊 {report_type.title()} Report\n"
        report += f"   • Source: {data_source}\n"
        report += f"   • Format: {format}\n"
        report += f"   • Charts: {'Included' if include_charts else 'Not included'}\n"
        report += f"   • Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Enhanced report content based on type
        if "sales" in report_type.lower():
            report += "📈 Sales Summary:\n"
            report += "   • Total Revenue: $125,000 (+15% vs last month)\n"
            report += "   • Units Sold: 1,250 (+8% vs last month)\n"
            report += "   • Top Product: MacBook Pro (234 units)\n"
            report += "   • Growth Rate: +15% month-over-month\n"
        elif "user" in report_type.lower():
            report += "👥 User Analytics:\n"
            report += "   • Active Users: 5,420 (+12% vs last week)\n"
            report += "   • New Signups: 234 (+5% vs last week)\n"
            report += "   • Retention Rate: 87% (+2% vs last week)\n"
            report += "   • Avg Session Duration: 12.5 minutes\n"
        elif "inventory" in report_type.lower():
            report += "📦 Inventory Status:\n"
            report += "   • Total Items: 2,450 (+45 vs last week)\n"
            report += "   • Low Stock: 15 items (needs attention)\n"
            report += "   • Out of Stock: 3 items (urgent)\n"
            report += "   • Inventory Value: $89,500\n"
        else:
            report += "📋 General Report:\n"
            report += "   • Data points: 1,000\n"
            report += "   • Processing time: 2.3s\n"
            report += "   • Status: Complete\n"
            report += "   • Quality Score: 98.5%\n"
        
        return report
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"


def demo_enhanced_features():
    """Demonstrate all enhanced features of IntentAI."""
    print("🚀 IntentAI Enhanced Features Demo")
    print("=" * 60)
    print("This demo showcases all professional improvements:")
    print("• Enhanced parameter extraction")
    print("• Improved confidence scoring")
    print("• Better error handling")
    print("• Professional logging")
    print("• Robust type safety")
    print("• Advanced CLI features")
    print()
    
    # Register tools
    tools = get_tools_from_functions(
        create_user,
        add_product,
        analyze_text,
        generate_report
    )
    
    print(f"📋 Registered {len(tools)} enhanced tools:")
    for tool in tools:
        print(f"   • {tool.name}: {tool.description}")
    print()
    
    # Test scenarios demonstrating enhanced features
    test_scenarios = [
        # Enhanced parameter extraction tests
        {
            "input": "Create user John Smith with email john.smith@company.com age 28",
            "description": "Enhanced name, email, and age extraction"
        },
        {
            "input": "Add product MacBook Pro with price $1299.99 category Electronics",
            "description": "Enhanced price and category extraction"
        },
        {
            "input": "Analyze text 'This product is absolutely amazing and wonderful!'",
            "description": "Enhanced sentiment analysis with more words"
        },
        {
            "input": "Generate report for sales data from database with charts",
            "description": "Enhanced parameter extraction with boolean flags"
        },
        
        # Edge cases and error handling
        {
            "input": "Create user with invalid email",
            "description": "Error handling for invalid data"
        },
        {
            "input": "Add product with negative price",
            "description": "Validation error handling"
        },
        {
            "input": "Analyze empty text",
            "description": "Empty input handling"
        },
        
        # Complex natural language
        {
            "input": "Please create a new user account for Alice Johnson, her email is alice.j@example.org and she's 32 years old",
            "description": "Complex natural language parsing"
        },
        {
            "input": "I need to add a new product to our inventory: it's a wireless mouse, costs 29.99 dollars, and belongs in the computer accessories category",
            "description": "Complex product description parsing"
        }
    ]
    
    print("🔍 Testing Enhanced Intent Detection:")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['description']}")
        print(f"   Input: '{scenario['input']}'")
        
        # Detect intent
        result = detect_tool_and_params(scenario['input'], tools)
        
        if result:
            # Handle both single result and list of results
            if isinstance(result, list):
                print(f"   ⚠️ Multiple candidates detected:")
                for j, res in enumerate(result, 1):
                    print(f"     {j}. {res['tool']} (confidence: {res['confidence']:.3f})")
                result = result[0]  # Use first result
            else:
                print(f"   ✅ Detected: {result['tool']}")
                print(f"   📊 Confidence: {result['confidence']:.3f}")
                print(f"   🔧 Parameters: {result['parameters']}")
            
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
                    description = result['parameters'].get("description")
                    output = add_product(name, price, category, description)
                elif result['tool'] == "analyze_text":
                    text = result['parameters'].get("text", "")
                    include_sentiment = result['parameters'].get("include_sentiment", True)
                    extract_keywords = result['parameters'].get("extract_keywords", True)
                    output = analyze_text(text, include_sentiment, extract_keywords)
                elif result['tool'] == "generate_report":
                    report_type = result['parameters'].get("report_type", "")
                    data_source = result['parameters'].get("data_source", "")
                    format = result['parameters'].get("format", "text")
                    include_charts = result['parameters'].get("include_charts", False)
                    output = generate_report(report_type, data_source, format, include_charts)
                else:
                    output = "Tool not implemented"
                
                print(f"   📤 Output: {output}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print("   ❌ No intent detected")
    
    # Demonstrate schema generation
    print(f"\n" + "=" * 60)
    print("📋 Enhanced JSON Schema Generation:")
    print("=" * 60)
    
    schema = generate_json_schema(tools)
    print("✅ Schema generated successfully with enhanced parameter definitions")
    print(f"   • Tools defined: {len(schema.get('definitions', {}))}")
    print(f"   • Schema version: {schema.get('$schema', 'Unknown')}")
    
    # Show a sample of the schema
    if 'definitions' in schema and 'create_user' in schema['definitions']:
        print("\n📄 Sample Schema (create_user):")
        print(json.dumps(schema['definitions']['create_user'], indent=2))
    
    print(f"\n" + "=" * 60)
    print("🎯 Enhanced Confidence Scoring Demo:")
    print("=" * 60)
    
    confidence_tests = [
        ("Create user John Doe with email john@example.com age 25", 0.8),
        ("Add product MacBook Pro with price 1299.99 category Electronics", 0.7),
        ("Analyze text 'I love this amazing product!'", 0.9),
        ("Generate report for sales data from database", 0.6),
        ("Random text that doesn't match anything", 0.3)
    ]
    
    for user_input, expected_min in confidence_tests:
        result = detect_tool_and_params(user_input, tools)
        if result:
            confidence = result['confidence']
            status = "✅" if confidence >= expected_min else "⚠️"
            print(f"   {status} '{user_input}': {confidence:.3f} (expected ≥{expected_min})")
        else:
            print(f"   ❌ '{user_input}': No detection")
    
    print(f"\n[DONE] Enhanced Features Demo Completed!")
    print("The system now provides:")
    print("   • Better parameter extraction from natural language")
    print("   • Enhanced confidence scoring with multiple factors")
    print("   • Robust error handling and validation")
    print("   • Professional logging and debugging")
    print("   • Type-safe TypedDict implementation")
    print("   • Advanced CLI with interactive mode")


if __name__ == "__main__":
    demo_enhanced_features() 