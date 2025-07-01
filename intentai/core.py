"""
intentai.core - Main public API for IntentAI

Exports the main types and functions for tool detection, parameter extraction, and schema generation.
"""

from .types import Tool, DetectionResult
from .detector import detect_tool_and_params, get_tools_from_functions, generate_json_schema

__all__ = [
    "Tool",
    "DetectionResult",
    "detect_tool_and_params",
    "get_tools_from_functions",
    "generate_json_schema",
] 