"""Tool Detector - A library for detecting tools and extracting parameters from user input."""

import inspect
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined
from .types import Tool, ToolParameter, ParameterType


def _get_parameter_type(param_type: Type) -> ParameterType:
    """Convert Python type to ParameterType."""
    if param_type == str:
        return ParameterType.STRING
    elif param_type in (int, float):
        return ParameterType.NUMBER
    elif param_type == bool:
        return ParameterType.BOOLEAN
    elif hasattr(param_type, '__mro__') and any(base.__name__ == 'BaseModel' for base in param_type.__mro__):
        return ParameterType.DICT
    else:
        return ParameterType.STRING


def _extract_parameters_from_signature(func: Callable) -> List[ToolParameter]:
    """Extract parameters from function signature."""
    sig = inspect.signature(func)
    params =[]
    
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
            
        param_type = param.annotation
        default = param.default if param.default is not inspect.Parameter.empty else None
        
        # Handle Pydantic models
        if hasattr(param_type, '__mro__') and any(base.__name__ == 'BaseModel' for base in param_type.__mro__):
            # Extract fields from Pydantic model
            for field_name, field in param_type.model_fields.items():
                field_type = _get_parameter_type(field.annotation)
                field_default = field.default if field.default is not PydanticUndefined else None
                params.append(ToolParameter(
                    name=field_name,
                    type=field_type,
                    description=field.description or f"Parameter {field_name}",
                    required=field.is_required(),
                    default=field_default
                ))
        else:
            # Handle regular parameters
            param_type = _get_parameter_type(param_type)
            params.append(ToolParameter(
                name=name,
                type=param_type,
                description=f"Parameter {name}",
                required=param.default is inspect.Parameter.empty,
                default=default
            ))
    
    return params


def _extract_trigger_phrases(docstring: str) -> List[str]:
    """Extract trigger phrases from docstring."""
    if not docstring:
        return []
    
    phrases = []
    
    # Look for multiple :trigger lines
    trigger_lines = re.findall(r':trigger\s+(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    for line in trigger_lines:
        phrases.extend([p.strip() for p in line.split(',') if p.strip()])
    
    # Look for Trigger phrases: format (comma-separated)
    trigger_match = re.search(r'Trigger phrases:\s*(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    if trigger_match:
        phrases.extend([p.strip() for p in trigger_match.group(1).split(',') if p.strip()])
    
    # Look for :trigger: format (comma-separated)
    trigger_colon_match = re.search(r':trigger:\s*(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    if trigger_colon_match:
        phrases.extend([p.strip() for p in trigger_colon_match.group(1).split(',') if p.strip()])
    
    return list(set(phrases))  # Remove duplicates


def _extract_examples(docstring: str) -> List[str]:
    """Extract examples from docstring."""
    if not docstring:
        return []
    
    examples = []
    
    # Look for multiple :examples lines
    example_lines = re.findall(r':examples\s+(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    for line in example_lines:
        examples.extend([e.strip() for e in line.split(',') if e.strip()])
    
    # Look for Examples: format (comma-separated)
    example_match = re.search(r'Examples:\s*(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    if example_match:
        examples.extend([e.strip() for e in example_match.group(1).split(',') if e.strip()])
    
    # Look for :examples: format (comma-separated)
    example_colon_match = re.search(r':examples:\s*(.*?)(?:\n|$)', docstring, re.IGNORECASE)
    if example_colon_match:
        examples.extend([e.strip() for e in example_colon_match.group(1).split(',') if e.strip()])
    
    return list(set(examples))  # Remove duplicates


def tool_call(
    func_or_name: Optional[Union[Callable, str]] = None,
    description: Optional[str] = None,
    trigger_phrases: Optional[List[str]] = None,
    examples: Optional[List[str]] = None
):
    """Decorator to register a function as a tool."""
    def decorator(func: Callable) -> Callable:
        # Get function metadata
        name = func.__name__
        docstring = func.__doc__ or ""
        
        # Extract parameters from function signature
        parameters = _extract_parameters_from_signature(func)
        
        # Extract trigger phrases and examples from docstring
        extracted_triggers = _extract_trigger_phrases(docstring)
        extracted_examples = _extract_examples(docstring)
        
        # Use provided values or fall back to extracted ones
        final_triggers = trigger_phrases or extracted_triggers or [name.replace('_', ' ')]
        final_examples = examples or extracted_examples or []
        
        # Create tool definition
        tool = Tool(
            name=name,
            description=description or docstring.split('\n')[0] or name,
            parameters=parameters,
            trigger_phrases=final_triggers,
            examples=final_examples
        )
        
        # Store tool in function
        func._tool = tool
        
        return func
    
    # Handle both @tool_call and @tool_call() syntax
    if func_or_name is None:
        return decorator
    elif callable(func_or_name):
        return decorator(func_or_name)
    else:
        name = func_or_name
        def decorator_with_name(func: Callable) -> Callable:
            func_name = name
            return decorator(func)
        return decorator_with_name


def get_tools_from_functions(*functions: Callable) -> List[Tool]:
    """Get tool definitions from decorated functions."""
    tools = []
    for func in functions:
        if hasattr(func, '_tool'):
            tools.append(func._tool)
    return tools


def get_openapi_schema_for_tools(tools: List[Tool]) -> Dict[str, Any]:
    """Generate JSON Schema for tools."""
    schemas = {}
    
    for tool in tools:
        # Create schema for tool
        schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        
        # Add parameters to schema
        for param in tool.parameters:
            param_schema = {
                "type": param.type.value.lower()
            }
            
            # Add default value if present
            if param.default is not None and param.default is not PydanticUndefined:
                param_schema["default"] = param.default
            
            # Add description if present
            if param.description:
                param_schema["description"] = param.description
            
            # Add to properties
            schema["properties"][param.name] = param_schema
            
            # Add to required if parameter is required
            if param.required:
                schema["required"].append(param.name)
        
        schemas[tool.name] = schema
    
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "definitions": schemas
    } 