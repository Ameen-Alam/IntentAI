"""Enhanced tool detection with parameter extraction and validation."""

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined

from .types import DetectionResult, Tool, ToolParameter, ParameterType


def calculate_confidence(
    tool: Tool,
    user_input: str,
    extracted_params: Dict[str, Any]
) -> float:
    """Calculate confidence score for tool detection."""
    confidence = 0.0
    input_lower = user_input.lower()
    
    # Check if any trigger phrase is present (more lenient matching)
    for phrase in tool.trigger_phrases:
        phrase_lower = phrase.lower()
        if phrase_lower in input_lower:
            confidence += 0.4  # Base confidence for trigger phrase match
            # Additional confidence for exact matches
            if phrase_lower == input_lower.strip():
                confidence += 0.2
            break
    
    # Check parameter extraction
    param_count = len(extracted_params)
    required_params = sum(1 for p in tool.parameters if p.required)
    if required_params > 0:
        # Higher weight for required parameters
        confidence += 0.4 * (param_count / required_params)
    
    # Check if input matches any example (more lenient matching)
    for example in tool.examples:
        example_lower = example.lower()
        if example_lower in input_lower or input_lower in example_lower:
            confidence += 0.2
            break
    
    # Penalize if required parameters are missing
    missing_required = sum(1 for p in tool.parameters if p.required and p.name not in extracted_params)
    if missing_required > 0:
        confidence *= 0.5  # Significant penalty for missing required parameters
    
    return min(confidence, 1.0)


def extract_parameters(
    user_input: str,
    tool: Tool,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract parameters from user input."""
    params = {}
    input_lower = user_input.lower()
    
    # Find the longest matching trigger phrase
    best_trigger = None
    best_trigger_len = 0
    for phrase in tool.trigger_phrases:
        phrase_lower = phrase.lower()
        if phrase_lower in input_lower and len(phrase_lower) > best_trigger_len:
            best_trigger = phrase_lower
            best_trigger_len = len(phrase_lower)
    
    if best_trigger:
        # Extract the part after the trigger phrase
        trigger_index = input_lower.find(best_trigger) + len(best_trigger)
        remaining_text = user_input[trigger_index:].strip()
        
        # Extract parameters based on their types and names
        for param in tool.parameters:
            param_name_lower = param.name.lower()
            
            # Look for parameter name in the text
            param_index = remaining_text.lower().find(param_name_lower)
            
            if param.type == ParameterType.NUMBER:
                # Look for numbers in the remaining text
                numbers = re.findall(r'\d+', remaining_text)
                if numbers:
                    params[param.name] = float(numbers[0])
            elif param.type == ParameterType.BOOLEAN:
                # Look for boolean indicators
                if 'with' in remaining_text.lower() and param_name_lower in remaining_text.lower():
                    params[param.name] = True
                elif 'without' in remaining_text.lower() and param_name_lower in remaining_text.lower():
                    params[param.name] = False
            elif param.type == ParameterType.STRING:
                # For string parameters, try to extract based on context
                if param_name_lower == 'city':
                    # Special handling for city parameter
                    city_text = remaining_text
                    for unit in ['celsius', 'fahrenheit', 'kelvin']:
                        city_text = city_text.replace(unit, '').strip()
                    if 'in' in city_text.lower():
                        city_text = city_text.split('in')[-1].strip()
                    params[param.name] = city_text
                elif param_name_lower == 'query':
                    # For query parameters, use the remaining text
                    params[param.name] = remaining_text
                elif param_index != -1:
                    # For other string parameters, try to extract after the parameter name
                    value = remaining_text[param_index + len(param_name_lower):].strip()
                    if value:
                        # Remove any trailing punctuation or common words
                        value = re.sub(r'[.,;:!?].*$', '', value).strip()
                        params[param.name] = value
    
    # Apply default values for missing parameters
    for param in tool.parameters:
        if param.name not in params and param.default is not None:
            params[param.name] = param.default
    
    return params


def detect_tool_and_params(
    user_input: str,
    available_tools: List[Tool],
    min_confidence: float = 0.6,  # Lowered minimum confidence threshold
    context: Optional[Dict[str, Any]] = None
) -> Optional[DetectionResult]:
    """Detect which tool to use and extract its parameters from user input."""
    best_match = None
    best_confidence = 0.0
    best_params = {}
    validation_errors = []
    missing_params = []
    
    # First check if any tool's trigger phrases match the input
    input_lower = user_input.lower()
    matching_tools = []
    for tool in available_tools:
        for phrase in tool.trigger_phrases:
            if phrase.lower() in input_lower:
                matching_tools.append(tool)
                break
    
    # If no tools match, return None immediately
    if not matching_tools:
        return None
    
    # Only process matching tools
    for tool in matching_tools:
        # Extract parameters
        params = extract_parameters(user_input, tool, context)
        
        # Calculate confidence
        confidence = calculate_confidence(tool, user_input, params)
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = (tool, params)
            best_params = params
    
    if best_match and best_confidence >= min_confidence:
        tool, params = best_match
        
        # Validate parameters
        for param in tool.parameters:
            if param.required and param.name not in params:
                missing_params.append(param.name)
            elif param.name in params:
                value = params[param.name]
                if value is PydanticUndefined:
                    validation_errors.append(f"Parameter '{param.name}' is undefined")
                elif not isinstance(value, (str, int, float, bool, dict, list)):
                    validation_errors.append(f"Parameter '{param.name}' has invalid type: {type(value)}")
        
        return DetectionResult(
            tool=tool.name,
            confidence=best_confidence,
            parameters=params,
            validation_errors=validation_errors,
            missing_parameters=missing_params
        )
    
    return None 