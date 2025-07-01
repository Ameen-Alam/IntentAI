"""Dynamic tool decorator for registering functions as tools with automatic parameter extraction."""

import inspect
import re
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined

from .types import Tool, ToolParameter, ParameterType


def _extract_trigger_phrases(docstring: str) -> List[str]:
    """Extract trigger phrases from docstring - completely dynamic."""
    if not docstring:
        return []
    
    # Look for trigger phrases in various formats
    trigger_patterns = [
        r'@trigger\s+(.+)',  # @trigger phrase
        r'Trigger:\s*(.+)',  # Trigger: phrase
        r'Triggers?:\s*(.+)',  # Triggers: phrase
        r'Use when:\s*(.+)',  # Use when: phrase
        r'Call when:\s*(.+)',  # Call when: phrase
        r'Keywords?:\s*(.+)',  # Keywords: phrase
    ]
    
    triggers = []
    for pattern in trigger_patterns:
        matches = re.findall(pattern, docstring, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Split by commas, semicolons, or newlines
            phrases = re.split(r'[,;\n]', match.strip())
            triggers.extend([phrase.strip() for phrase in phrases if phrase.strip()])
    
    # If no explicit triggers found, generate from function name
    if not triggers:
        # Convert function name to trigger phrases
        func_name = docstring.split('\n')[0].strip()
        if func_name:
            # Remove common prefixes and convert to natural language
            name = func_name.lower()
            if name.startswith('get_'):
                name = name[4:]
            elif name.startswith('fetch_'):
                name = name[6:]
            elif name.startswith('search_'):
                name = name[7:]
            elif name.startswith('calculate_'):
                name = name[10:]
            elif name.startswith('create_'):
                name = name[7:]
            elif name.startswith('update_'):
                name = name[7:]
            elif name.startswith('delete_'):
                name = name[7:]
            
            # Convert to trigger phrases
            triggers = [
                f"get {name.replace('_', ' ')}",
                f"fetch {name.replace('_', ' ')}",
                f"search for {name.replace('_', ' ')}",
                f"calculate {name.replace('_', ' ')}",
                f"create {name.replace('_', ' ')}",
                f"update {name.replace('_', ' ')}",
                f"delete {name.replace('_', ' ')}",
                name.replace('_', ' ')
            ]
    
    return triggers


def _extract_examples(docstring: str) -> List[str]:
    """Extract examples from docstring - completely dynamic."""
    if not docstring:
        return []
    
    examples = []
    
    # Look for examples in various formats
    example_patterns = [
        r'@example\s+(.+)',  # @example text
        r'Example:\s*(.+)',  # Example: text
        r'Examples?:\s*(.+)',  # Examples: text
        r'Usage:\s*(.+)',  # Usage: text
        r'Use cases?:\s*(.+)',  # Use cases: text
    ]
    
    for pattern in example_patterns:
        matches = re.findall(pattern, docstring, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Split by newlines or bullet points
            lines = re.split(r'\n|•|\*', match.strip())
            examples.extend([line.strip() for line in lines if line.strip()])
    
    return examples


def _infer_parameter_type(param: inspect.Parameter) -> ParameterType:
    """Infer parameter type from annotation and default value - completely dynamic."""
    if param.annotation == inspect.Parameter.empty:
        # Infer from default value
        if param.default is None:
            return ParameterType.STRING
        elif isinstance(param.default, bool):
            return ParameterType.BOOLEAN
        elif isinstance(param.default, (int, float)):
            return ParameterType.NUMBER
        elif isinstance(param.default, list):
            return ParameterType.LIST
        elif isinstance(param.default, dict):
            return ParameterType.DICT
        else:
            return ParameterType.STRING
    else:
        # Infer from annotation
        annotation = param.annotation
        if annotation == bool:
            return ParameterType.BOOLEAN
        elif annotation in (int, float):
            return ParameterType.NUMBER
        elif annotation == list:
            return ParameterType.LIST
        elif annotation == dict:
            return ParameterType.DICT
        elif hasattr(annotation, '__origin__') and annotation.__origin__ == list:
            return ParameterType.LIST
        elif hasattr(annotation, '__origin__') and annotation.__origin__ == dict:
            return ParameterType.DICT
        else:
            return ParameterType.STRING


def _extract_parameter_description(param_name: str, docstring: str) -> str:
    """Extract parameter description from docstring - completely dynamic."""
    if not docstring:
        return ""
    
    # Look for parameter descriptions in various formats
    param_patterns = [
        rf'{param_name}:\s*(.+)',  # param: description
        rf'@param\s+{param_name}\s+(.+)',  # @param param description
        rf'Args?:\s*{param_name}:\s*(.+)',  # Args: param: description
    ]
    
    for pattern in param_patterns:
        match = re.search(pattern, docstring, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    
    return ""


def tool_call(
    name: Optional[str] = None,
    description: Optional[str] = None,
    trigger_phrases: Optional[List[str]] = None,
    examples: Optional[List[str]] = None,
    parameters: Optional[Dict[str, Any]] = None
):
    """
    Dynamic decorator to register a function as a tool.
    
    Args:
        name: Optional custom name for the tool
        description: Optional custom description
        trigger_phrases: Optional list of trigger phrases
        examples: Optional list of example inputs
        parameters: Optional dict of parameter overrides
    
    The decorator automatically extracts:
    - Function signature and parameter types
    - Docstring for description, triggers, and examples
    - Parameter descriptions and validation
    """
    def decorator(func: Callable) -> Callable:
        # Extract function metadata
        func_name = name or func.__name__
        func_doc = func.__doc__ or ""
        
        # Extract description
        tool_description = description or func_doc.split('\n')[0].strip()
        
        # Extract trigger phrases
        tool_triggers = trigger_phrases or _extract_trigger_phrases(func_doc)
        
        # Extract examples
        tool_examples = examples or _extract_examples(func_doc)
        
        # Extract parameters from function signature
        sig = inspect.signature(func)
        tool_parameters = []
        
        for param_name, param in sig.parameters.items():
            # Skip self/cls for methods
            if param_name in ('self', 'cls'):
                continue
            
            # Get parameter info
            param_type = _infer_parameter_type(param)
            param_required = param.default == inspect.Parameter.empty
            param_default = None if param_required else param.default
            param_description = _extract_parameter_description(param_name, func_doc)
            
            # Check for parameter overrides
            if parameters and param_name in parameters:
                override = parameters[param_name]
                if isinstance(override, dict):
                    param_type = override.get('type', param_type)
                    param_required = override.get('required', param_required)
                    param_default = override.get('default', param_default)
                    param_description = override.get('description', param_description)
            
            tool_parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                required=param_required,
                default=param_default,
                description=param_description
            ))
        
        # Create tool object
        tool = Tool(
            name=func_name,
            description=tool_description,
            trigger_phrases=tool_triggers,
            examples=tool_examples,
            parameters=tool_parameters
        )
        
        # Store tool metadata on function
        func._tool_metadata = tool
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Copy tool metadata to wrapper
        wrapper._tool_metadata = tool
        
        return wrapper
    
    return decorator


def get_tools_from_functions(*functions: Callable) -> List[Tool]:
    """
    Extract tools from decorated functions - completely dynamic.
    
    Args:
        *functions: Variable number of decorated functions
        
    Returns:
        List of Tool objects extracted from the functions
        
    Raises:
        TypeError: If a list is passed instead of separate arguments
    """
    tools = []
    
    for func in functions:
        if hasattr(func, '_tool_metadata'):
            tools.append(func._tool_metadata)
        else:
            # Create a basic tool from undecorated function
            sig = inspect.signature(func)
            parameters = []
            
            for param_name, param in sig.parameters.items():
                if param_name not in ('self', 'cls'):
                    param_type = _infer_parameter_type(param)
                    param_required = param.default == inspect.Parameter.empty
                    param_default = None if param_required else param.default
                    
                    parameters.append(ToolParameter(
                        name=param_name,
                        type=param_type,
                        required=param_required,
                        default=param_default,
                        description=""
                    ))
            
            tool = Tool(
                name=func.__name__,
                description=func.__doc__ or "",
                trigger_phrases=[func.__name__.replace('_', ' ')],
                examples=[],
                parameters=parameters
            )
            tools.append(tool)
    
    return tools


def generate_json_schema(tools: List[Tool]) -> Dict[str, Any]:
    """
    Generate JSON Schema for tools - completely dynamic.
    
    Args:
        tools: List of Tool objects
        
    Returns:
        JSON Schema dictionary
    """
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "tools": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "trigger_phrases": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "examples": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "parameters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "required": {"type": "boolean"},
                                    "default": {},
                                    "description": {"type": "string"}
                                },
                                "required": ["name", "type", "required"]
                            }
                        }
                    },
                    "required": ["name", "description", "trigger_phrases", "examples", "parameters"]
                }
            }
        },
        "required": ["tools"]
    }
    
    return schema 