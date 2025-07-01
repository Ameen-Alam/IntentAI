"""Core type definitions for the tool detector."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Union


class ParameterType(Enum):
    """Types of parameters that tools can accept."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation_regex: Optional[str] = None
    allowed_values: Optional[List[Any]] = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a parameter value against its constraints."""
        if value is None:
            if self.required and self.default is None:
                return False, f"Parameter '{self.name}' is required"
            return True, None

        # Type validation
        try:
            if self.type == ParameterType.NUMBER:
                float(value)
            elif self.type == ParameterType.BOOLEAN:
                if not isinstance(value, bool):
                    return False, f"Parameter '{self.name}' must be a boolean"
            elif self.type == ParameterType.LIST:
                if not isinstance(value, list):
                    return False, f"Parameter '{self.name}' must be a list"
            elif self.type == ParameterType.DICT:
                if not isinstance(value, dict):
                    return False, f"Parameter '{self.name}' must be a dictionary"
        except ValueError:
            return False, f"Parameter '{self.name}' must be a {self.type.value}"

        # Regex validation
        if self.validation_regex and isinstance(value, str):
            import re
            if not re.match(self.validation_regex, value):
                return False, f"Parameter '{self.name}' does not match required pattern"

        # Allowed values validation
        if self.allowed_values is not None and value not in self.allowed_values:
            return False, f"Parameter '{self.name}' must be one of {self.allowed_values}"

        return True, None


@dataclass
class Tool:
    """Definition of a tool that can be detected and used."""
    name: str
    description: str
    parameters: List[ToolParameter]
    trigger_phrases: List[str]
    examples: List[str]

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate all parameters for this tool."""
        errors = []
        valid = True

        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in params:
                errors.append(f"Missing required parameter: {param.name}")
                valid = False
                continue

            # Validate parameter if present
            if param.name in params:
                is_valid, error = param.validate(params[param.name])
                if not is_valid:
                    valid = False
                    errors.append(error)

        return valid, errors


class DetectionResult(TypedDict):
    """Result of tool detection and parameter extraction."""
    tool: str
    confidence: float
    parameters: Dict[str, Any]
    missing_parameters: List[str]
    validation_errors: List[str] 