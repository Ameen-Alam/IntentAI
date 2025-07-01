"""IntentAI - AI-powered intent parsing system that converts natural language into structured tool calls."""

from .detector import detect_tool_and_params
from .types import Tool, ToolParameter, ParameterType, DetectionResult
from .decorator import tool_call, get_tools_from_functions, get_openapi_schema_for_tools

__version__ = "0.1.0"
__all__ = [
    "detect_tool_and_params",
    "Tool",
    "ToolParameter",
    "ParameterType",
    "DetectionResult",
    "tool_call",
    "get_tools_from_functions",
    "get_openapi_schema_for_tools"
] 