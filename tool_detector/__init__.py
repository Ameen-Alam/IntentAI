"""Tool Detector - A lightweight system for parsing user intents into structured tool calls."""

from .detector import detect_tool_and_params

__version__ = "0.1.0"
__all__ = ["detect_tool_and_params"] 