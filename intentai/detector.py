"""Enhanced tool detection with dynamic parameter extraction and validation."""

import re
import difflib
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined

from .types import DetectionResult, Tool, ToolParameter, ParameterType
from .decorator import get_tools_from_functions, generate_json_schema


def _normalize(text):
    """Normalize text for comparison by removing punctuation and extra spaces."""
    # Handle contractions
    text = re.sub(r"what's", "what is", text, flags=re.IGNORECASE)
    text = re.sub(r"it's", "it is", text, flags=re.IGNORECASE)
    text = re.sub(r"that's", "that is", text, flags=re.IGNORECASE)
    return ' '.join(re.sub(r'[^a-zA-Z0-9 ]', '', text.lower()).split())


def _fuzzy_trigger_match(input_text, trigger_phrases, threshold=0.7):
    """Generic fuzzy matching for trigger phrases with improved flexibility."""
    input_norm = _normalize(input_text)
    best = None
    best_score = 0
    
    for phrase in trigger_phrases:
        phrase_norm = _normalize(phrase)
        if phrase_norm in input_norm:
            return phrase, 1.0
        # Fuzzy match using sequence matcher
        score = difflib.SequenceMatcher(None, phrase_norm, input_norm).ratio()
        if score > best_score:
            best = phrase
            best_score = score
    
    if best_score >= threshold:
        return best, best_score
    return None, 0


def calculate_confidence(
    tool: Tool,
    user_input: str,
    extracted_params: Dict[str, Any]
) -> float:
    """Calculate confidence score for tool detection - completely generic."""
    confidence = 0.0
    input_norm = _normalize(user_input)
    
    # Trigger phrase matching (40% weight)
    matched_trigger, trigger_score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
    if trigger_score > 0.7:
        confidence += 0.4 * trigger_score
        # Bonus for exact trigger match
        if matched_trigger and _normalize(matched_trigger) in input_norm:
            confidence += 0.1
    
    # Parameter extraction quality (30% weight)
    param_count = len(extracted_params)
    required_params = sum(1 for p in tool.parameters if p.required)
    if required_params > 0:
        param_ratio = param_count / required_params
        confidence += 0.3 * param_ratio
        # Bonus for extracting all required parameters
        if param_ratio >= 1.0:
            confidence += 0.1
    
    # Example matching (20% weight)
    best_example_score = 0.0
    for example in tool.examples:
        example_norm = _normalize(example)
        # Check for substring matches
        if example_norm in input_norm or input_norm in example_norm:
            best_example_score = max(best_example_score, 0.8)
        else:
            # Fuzzy match for examples
            example_score = difflib.SequenceMatcher(None, example_norm, input_norm).ratio()
            best_example_score = max(best_example_score, example_score)
    
    confidence += 0.2 * best_example_score
    
    # Input length and complexity bonus (10% weight)
    input_words = len(user_input.split())
    if input_words >= 3:  # More complex inputs get a small bonus
        confidence += 0.05
    if input_words >= 5:
        confidence += 0.05
    
    # Penalty for missing required parameters
    missing_required = sum(1 for p in tool.parameters if p.required and p.name not in extracted_params)
    if missing_required > 0:
        confidence *= (0.8 ** missing_required)  # Exponential penalty
    
    # Penalty for very low confidence
    if confidence < 0.3:
        confidence *= 0.5
    
    return min(confidence, 1.0)


def _extract_boolean_parameter(param: ToolParameter, full_input: str) -> Optional[bool]:
    """Extract boolean parameters dynamically based on parameter name."""
    param_name_lower = param.name.lower()
    input_lower = full_input.lower()
    
    # Check for positive/negative patterns
    positive_patterns = [
        rf'with\s+{re.escape(param_name_lower)}',
        rf'including\s+{re.escape(param_name_lower)}',
        rf'show\s+{re.escape(param_name_lower)}',
        rf'include\s+{re.escape(param_name_lower)}',
        rf'with\s+{re.escape(param_name_lower)}\s+enabled',
        rf'with\s+{re.escape(param_name_lower)}\s+on'
    ]
    negative_patterns = [
        rf'without\s+{re.escape(param_name_lower)}',
        rf'no\s+{re.escape(param_name_lower)}',
        rf'exclude\s+{re.escape(param_name_lower)}',
        rf'without\s+{re.escape(param_name_lower)}\s+enabled',
        rf'without\s+{re.escape(param_name_lower)}\s+on'
    ]
    
    for pattern in positive_patterns:
        if re.search(pattern, input_lower):
            return True
    for pattern in negative_patterns:
        if re.search(pattern, input_lower):
            return False
    
    # Fallback: if parameter name is present, treat as True unless explicitly negative
    if param_name_lower in input_lower:
        if 'without' in input_lower or 'no' in input_lower or 'exclude' in input_lower:
            return False
        return True
    
    return None


def _extract_dynamic_parameter(param: ToolParameter, remaining_text: str, full_input: str) -> Any:
    """
    Extract parameters dynamically based on type and name - completely generic.
    No hardcoded parameter names or patterns.
    """
    param_name_lower = param.name.lower()
    input_lower = full_input.lower()
    
    if param.type == ParameterType.BOOLEAN:
        return _extract_boolean_parameter(param, full_input)
    
    elif param.type == ParameterType.NUMBER:
        # Look for numbers in the input
        numbers = re.findall(r'\d+(?:\.\d+)?', full_input)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
    
    elif param.type == ParameterType.STRING:
        # Generic string extraction - look for parameter name followed by value
        param_pattern = rf'{re.escape(param_name_lower)}\s+([^\s,;]+)'
        match = re.search(param_pattern, input_lower)
        if match:
            return match.group(1)
        
        # Look for quoted strings
        quoted_pattern = r'"([^"]+)"'
        quoted_matches = re.findall(quoted_pattern, full_input)
        if quoted_matches:
            return quoted_matches[0]
        
        # Look for values after common prepositions
        prep_patterns = [
            rf'(?:for|with|to|in|of)\s+{re.escape(param_name_lower)}\s+([^\s,;]+)',
            rf'{re.escape(param_name_lower)}\s+(?:is|as)\s+([^\s,;]+)',
            rf'{re.escape(param_name_lower)}\s*[:=]\s*([^\s,;]+)'
        ]
        
        for pattern in prep_patterns:
            match = re.search(pattern, input_lower)
            if match:
                return match.group(1)
        
        # Fallback: use remaining text if available
        if remaining_text.strip():
            return remaining_text.strip()
    
    elif param.type == ParameterType.LIST:
        # Look for list-like patterns
        list_patterns = [
            r'\[([^\]]+)\]',
            r'\(([^)]+)\)',
            r'list\s+of\s+([^,;]+)'
        ]
        
        for pattern in list_patterns:
            match = re.search(pattern, input_lower)
            if match:
                items = [item.strip() for item in match.group(1).split(',')]
                return items
        
        # Fallback: split by common separators
        if remaining_text.strip():
            items = [item.strip() for item in re.split(r'[,;]', remaining_text.strip())]
            return items
    
    elif param.type == ParameterType.DICT:
        # Look for key-value patterns
        dict_patterns = [
            r'\{([^}]+)\}',
            r'(\w+:\s*\w+(?:\s*,\s*\w+:\s*\w+)*)'
        ]
        
        for pattern in dict_patterns:
            match = re.search(pattern, input_lower)
            if match:
                # Simple key-value parsing
                pairs = re.findall(r'(\w+):\s*(\w+)', match.group(1))
                if pairs:
                    return dict(pairs)
    
    return None


def extract_parameters(
    user_input: str,
    tool: Tool,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract parameters from user input - completely dynamic and generic."""
    params = {}
    input_lower = user_input.lower()
    
    # Find trigger phrase and get remaining text
    matched_trigger, trigger_score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
    if matched_trigger:
        trigger_index = input_lower.find(matched_trigger.lower())
        if trigger_index != -1:
            trigger_index += len(matched_trigger)
        else:
            trigger_index = 0
        remaining_text = user_input[trigger_index:].strip()
    else:
        remaining_text = user_input
    
    # Extract parameters dynamically for each tool parameter
    for param in tool.parameters:
        extracted_value = _extract_dynamic_parameter(param, remaining_text, user_input)
        if extracted_value is not None:
            params[param.name] = extracted_value
    
    # Apply default values for missing parameters
    for param in tool.parameters:
        if param.name not in params and param.default is not None:
            params[param.name] = param.default
    
    return params


def detect_tool_and_params(
    user_input: str,
    available_tools: List[Tool],
    min_confidence: float = 0.6,
    context: Optional[Dict[str, Any]] = None
) -> Optional[DetectionResult]:
    """Detect which tool to use and extract its parameters - completely dynamic."""
    best_match = None
    best_confidence = 0.0
    best_params = {}
    validation_errors = []
    missing_params = []
    candidates = []
    
    # Find tools that match the input
    matching_tools = []
    for tool in available_tools:
        matched_trigger, trigger_score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
        if trigger_score > 0.7:
            matching_tools.append(tool)
    
    if not matching_tools:
        return None
    
    # Evaluate each matching tool
    for tool in matching_tools:
        params = extract_parameters(user_input, tool, context)
        confidence = calculate_confidence(tool, user_input, params)
        candidates.append((tool, params, confidence))
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = (tool, params)
            best_params = params
    
    # If multiple candidates have similar confidence, return all
    top_candidates = [c for c in candidates if abs(c[2] - best_confidence) < 0.1 and c[2] >= min_confidence]
    if len(top_candidates) > 1:
        # Return a list of DetectionResult for all top candidates
        return [
            DetectionResult(
                tool=tool.name,
                confidence=conf,
                parameters=params,
                validation_errors=[],
                missing_parameters=[p.name for p in tool.parameters if p.required and p.name not in params]
            ) for tool, params, conf in top_candidates
        ]
    
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