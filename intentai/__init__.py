"""
IntentAI - Dynamic Tool Detection and Parameter Extraction

A powerful, dynamic tool detection and parameter extraction system that converts 
natural language into structured tool calls. Works with ANY tools without hardcoded logic.

Key Features:
- Completely dynamic system with no hardcoded logic
- Generic parameter extraction for any tool function
- Intelligent confidence scoring
- Production-ready CLI with interactive mode
- JSON Schema generation
- Cross-platform compatibility

Example:
    from intentai import tool_call, get_tools_from_functions, detect_tool_and_params
    
    @tool_call(name="calculator")
    def calculate(expression: str) -> float:
        return eval(expression)
    
    tools = get_tools_from_functions(calculate)
    result = detect_tool_and_params("calculate 2+2", tools)
"""

__version__ = "1.0.0"
__author__ = "IntentAI Team"
__email__ = "team@intentai.com"
__description__ = "Dynamic tool detection and parameter extraction system"

from .core import (
    Tool,
    DetectionResult,
    detect_tool_and_params,
    get_tools_from_functions,
    generate_json_schema,
)
from .decorator import tool_call

__all__ = [
    "Tool",
    "DetectionResult", 
    "detect_tool_and_params",
    "get_tools_from_functions",
    "generate_json_schema",
    "tool_call",
] 