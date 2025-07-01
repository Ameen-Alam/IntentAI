"""Enhanced tool detection with parameter extraction and validation."""

import re
import difflib
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, create_model
from pydantic_core import PydanticUndefined

from .types import DetectionResult, Tool, ToolParameter, ParameterType


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
    
    # Trigger phrase matching
    matched_trigger, trigger_score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
    if trigger_score > 0.7:
        confidence += 0.4 * trigger_score
        if matched_trigger and _normalize(matched_trigger) == input_norm:
            confidence += 0.2
    
    # Parameter extraction quality
    param_count = len(extracted_params)
    required_params = sum(1 for p in tool.parameters if p.required)
    if required_params > 0:
        confidence += 0.4 * (param_count / required_params)
    
    # Example matching
    for example in tool.examples:
        example_norm = _normalize(example)
        if example_norm in input_norm or input_norm in example_norm:
            confidence += 0.2
            break
    
    # Penalty for missing required parameters
    missing_required = sum(1 for p in tool.parameters if p.required and p.name not in extracted_params)
    if missing_required > 0:
        confidence *= 0.5
    
    return min(confidence, 1.0)


# Synonyms for boolean parameter names (expandable by users)
BOOLEAN_SYNONYMS = {
    'include_history': ['history'],
    'include_metadata': ['metadata'],
    # Add more as needed
}

# Priority order for string parameters (for deduplication)
STRING_PARAM_PRIORITY = ['query', 'filters', 'expression', 'city', 'symbol']

def _boolean_param_matches(param_name: str, input_lower: str) -> bool:
    """Check if any synonym or substring of the param name is present in the input."""
    if param_name in input_lower:
        return True
    for syn in BOOLEAN_SYNONYMS.get(param_name, []):
        if syn in input_lower:
            return True
    # Substring match
    for word in param_name.split('_'):
        if word and word in input_lower:
            return True
    return False

def _extract_boolean_parameter(param: ToolParameter, full_input: str) -> Optional[bool]:
    param_name_lower = param.name.lower()
    input_lower = full_input.lower()
    # Check for positive/negative patterns for param name and synonyms
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
    # Add synonym patterns
    for syn in BOOLEAN_SYNONYMS.get(param_name_lower, []):
        positive_patterns.append(rf'with\s+{re.escape(syn)}')
        positive_patterns.append(rf'including\s+{re.escape(syn)}')
        negative_patterns.append(rf'without\s+{re.escape(syn)}')
        negative_patterns.append(rf'no\s+{re.escape(syn)}')
    for pattern in positive_patterns:
        if re.search(pattern, input_lower):
            return True
    for pattern in negative_patterns:
        if re.search(pattern, input_lower):
            return False
    # Fallback: if any synonym or substring is present, treat as True
    if _boolean_param_matches(param_name_lower, input_lower):
        if 'without' in input_lower or 'no' in input_lower or 'exclude' in input_lower:
            return False
        return True
    return None


def _extract_string_parameter(param: ToolParameter, remaining_text: str, full_input: str) -> Optional[str]:
    """Extract string parameters with improved text parsing."""
    param_name_lower = param.name.lower()
    input_lower = full_input.lower()
    
    # Try to find parameter name followed by value
    param_pattern = rf'{re.escape(param_name_lower)}\s+([^\s,;]+)'
    match = re.search(param_pattern, input_lower)
    if match:
        return match.group(1)
    
    # For specific parameter types, use specialized extraction
    if param_name_lower == 'expression':
        # Remove common calculator words
        expression_text = remaining_text
        for word in ['calculate', 'what is', 'compute', 'solve', 'whats']:
            expression_text = re.sub(rf'\b{word}\b', '', expression_text, flags=re.IGNORECASE)
        return expression_text.strip()
    
    elif param_name_lower == 'query':
        # Clean up query text
        query_text = remaining_text
        # Remove common search words
        for word in ['search for', 'find', 'look for', 'search', 'find information about']:
            query_text = re.sub(rf'\b{word}\b', '', query_text, flags=re.IGNORECASE)
        return query_text.strip()
    
    elif param_name_lower == 'symbol':
        # Extract stock symbol - look for uppercase letters or common patterns
        # First try to find after 'of' or 'for'
        symbol_match = re.search(r'(?:of|for)\s+([A-Za-z0-9]+)', input_lower)
        if symbol_match:
            return symbol_match.group(1).upper()
        
        # Look for uppercase stock symbols
        symbol_matches = re.findall(r'\b[A-Z]{1,5}\b', full_input)
        if symbol_matches:
            return symbol_matches[0]
        
        # Fallback: last word that looks like a symbol
        words = re.findall(r'\b[a-zA-Z0-9]{1,5}\b', full_input)
        if words:
            return words[-1].upper()
    
    elif param_name_lower == 'city':
        # Extract city name - look for patterns like "in [City]" or "for [City]"
        city_patterns = [
            r'(?:in|for|at)\s+([A-Za-z\s,]+?)(?:\s+(?:in|with|and|,|$))',
            r'(?:in|for|at)\s+([A-Za-z\s,]+?)(?:\s+(?:celsius|fahrenheit|kelvin|$))',
            r'(?:in|for|at)\s+([A-Za-z\s,]+?)$'
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, input_lower)
            if match:
                city = match.group(1).strip()
                # Clean up the city name
                city = re.sub(r'\s+(?:in|with|and|,).*$', '', city, flags=re.IGNORECASE)
                if city and len(city) > 1:
                    return city.title()
    
    elif param_name_lower == 'units':
        # Extract units from anywhere in the input
        if 'fahrenheit' in input_lower:
            return 'fahrenheit'
        elif 'celsius' in input_lower:
            return 'celsius'
        elif 'kelvin' in input_lower:
            return 'kelvin'
    
    # Default: use remaining text if available
    if remaining_text.strip():
        return remaining_text.strip()
    
    return None


def _extract_generic_parameter(param: ToolParameter, remaining_text: str, full_input: str) -> Any:
    """Generic parameter extraction based only on parameter type and name."""
    if param.type == ParameterType.NUMBER:
        # Look for numbers in the remaining text
        numbers = re.findall(r'\d+(?:\.\d+)?', remaining_text)
        if numbers:
            return float(numbers[0])
    
    elif param.type == ParameterType.BOOLEAN:
        # Use improved boolean extraction
        return _extract_boolean_parameter(param, full_input)
    
    elif param.type == ParameterType.STRING:
        # Use improved string extraction
        return _extract_string_parameter(param, remaining_text, full_input)
    
    return None


def extract_parameters(
    user_input: str,
    tool: Tool,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Extract parameters from user input - improved deduplication and relevance."""
    params = {}
    input_lower = user_input.lower()
    matched_trigger, trigger_score = _fuzzy_trigger_match(user_input, tool.trigger_phrases)
    if matched_trigger:
        trigger_index = input_lower.find(matched_trigger.lower())
        if trigger_index != -1:
            trigger_index += len(matched_trigger)
        else:
            trigger_index = 0
        remaining_text = user_input[trigger_index:].strip()
        # Assign string parameters only to the most relevant one
        string_params = [p for p in tool.parameters if p.type == ParameterType.STRING]
        assigned_string = False
        for param in tool.parameters:
            if param.type == ParameterType.STRING:
                # Assign only to the highest priority string param that matches input, or first in priority
                if not assigned_string:
                    if param.name in input_lower or any(syn in input_lower for syn in BOOLEAN_SYNONYMS.get(param.name, [])):
                        params[param.name] = _extract_string_parameter(param, remaining_text, user_input)
                        assigned_string = True
                    elif param.name in STRING_PARAM_PRIORITY and not any(p in params for p in STRING_PARAM_PRIORITY):
                        params[param.name] = _extract_string_parameter(param, remaining_text, user_input)
                        assigned_string = True
                # Otherwise, skip assignment to avoid duplicates
            elif param.type == ParameterType.BOOLEAN:
                val = _extract_boolean_parameter(param, user_input)
                if val is not None:
                    params[param.name] = val
            elif param.type == ParameterType.NUMBER:
                val = _extract_generic_parameter(param, remaining_text, user_input)
                if val is not None:
                    params[param.name] = val
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
    """Detect which tool to use and extract its parameters - now returns all candidates if ambiguous."""
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