# Performance Optimization Guide

This guide provides strategies for optimizing IntentAI performance based on our comprehensive benchmark results.

## Benchmark-Based Performance Insights

Based on our [benchmark results](../benchmarks.md), IntentAI achieves:

- **100% intent detection accuracy** in controlled tests
- **Sub-10ms response times** for typical queries
- **Linear scaling** with tool count
- **Minimal memory footprint** (~2MB base + ~1KB per tool)

## Performance Optimization Strategies

### 1. Tool Registration Optimization

#### Use Descriptive Function Names
```python
# Good - Clear and specific
@tool_call(name="weather_forecast")
def get_weather_forecast(location: str, days: int = 1) -> str:
    """Get weather forecast for a location."""
    pass

# Avoid - Too generic
@tool_call(name="get_data")
def get_data(param: str) -> str:
    """Get some data."""
    pass
```

#### Optimize Docstrings
```python
@tool_call(name="flight_booking")
def book_flight(
    destination: str,
    passengers: int = 1,
    class_type: str = "economy",
    date: str = None
) -> str:
    """
    Book a flight to a destination.
    
    Examples:
        - "book flight to Paris for 2 people business class"
        - "reserve flight to Tokyo economy class"
        - "flight ticket to New York"
    """
    pass
```

### 2. Parameter Extraction Optimization

#### Use Type Hints Consistently
```python
# Good - Clear type hints
@tool_call(name="user_management")
def create_user(
    name: str,
    email: str,
    age: int = None,
    is_active: bool = True,
    preferences: list = None
) -> str:
    pass

# Avoid - Missing type hints
@tool_call(name="user_management")
def create_user(name, email, age=None, is_active=True, preferences=None):
    pass
```

#### Provide Default Values
```python
# Good - Default values reduce extraction complexity
@tool_call(name="calculator")
def calculate(
    expression: str,
    precision: int = 2,
    rounding_mode: str = "round"
) -> float:
    pass

# The system will use defaults when parameters aren't specified
```

### 3. Confidence Threshold Tuning

Based on benchmark results, adjust confidence thresholds for your use case:

```python
from intentai import detect_tool_and_params

# High-precision applications (recommended: 0.8+)
result = detect_tool_and_params("weather in London", tools, min_confidence=0.8)
if result and result['confidence'] >= 0.9:
    # Very high confidence - safe to execute automatically
    execute_tool(result['tool'], result['parameters'])

# Balanced applications (recommended: 0.6-0.8)
result = detect_tool_and_params("calculate 2+2", tools, min_confidence=0.6)
if result and result['confidence'] >= 0.7:
    # Medium confidence - ask for confirmation
    ask_user_confirmation(result)

# High-recall applications (recommended: 0.4-0.6)
result = detect_tool_and_params("book flight", tools, min_confidence=0.4)
if result:
    # Low confidence - show suggestions
    show_tool_suggestions(result)
```

### 4. Batch Processing Optimization

For high-volume applications, use batch processing:

```python
import time
from intentai import detect_tool_and_params

def process_batch(inputs, tools, min_confidence=0.6):
    """Process multiple inputs efficiently."""
    results = []
    start_time = time.time()
    
    for user_input in inputs:
        result = detect_tool_and_params(user_input, tools, min_confidence)
        results.append({
            'input': user_input,
            'result': result,
            'timestamp': time.time()
        })
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"Processed {len(inputs)} inputs in {processing_time:.3f}s")
    print(f"Average time per input: {processing_time/len(inputs)*1000:.2f}ms")
    
    return results

# Usage
inputs = [
    "weather in London",
    "calculate 15 + 25",
    "book flight to Paris",
    "temperature in Tokyo"
]

results = process_batch(inputs, tools)
```

### 5. Memory Optimization

#### Tool Pool Management
```python
# Create tool pools for different contexts
weather_tools = get_tools_from_functions(get_weather, get_forecast)
booking_tools = get_tools_from_functions(book_flight, book_hotel)
calculator_tools = get_tools_from_functions(calculate, convert_units)

# Use specific tool pools based on context
def route_request(user_input, context):
    if context == "weather":
        return detect_tool_and_params(user_input, weather_tools)
    elif context == "booking":
        return detect_tool_and_params(user_input, booking_tools)
    elif context == "calculation":
        return detect_tool_and_params(user_input, calculator_tools)
```

#### Lazy Loading
```python
class ToolManager:
    def __init__(self):
        self._tools_cache = {}
    
    def get_tools_for_category(self, category):
        if category not in self._tools_cache:
            # Load tools only when needed
            if category == "weather":
                self._tools_cache[category] = get_tools_from_functions(
                    get_weather, get_forecast
                )
            elif category == "booking":
                self._tools_cache[category] = get_tools_from_functions(
                    book_flight, book_hotel
                )
        return self._tools_cache[category]
```

### 6. Caching Strategies

#### Result Caching
```python
import functools
from intentai import detect_tool_and_params

@functools.lru_cache(maxsize=1000)
def cached_detection(user_input, tool_names_tuple):
    """Cache detection results for repeated inputs."""
    tools = get_tools_by_names(tool_names_tuple)
    return detect_tool_and_params(user_input, tools)

# Usage
tool_names = ("weather_checker", "calculator", "flight_booking")
result = cached_detection("weather in London", tool_names)
```

#### Parameter Pattern Caching
```python
import re
from collections import defaultdict

class ParameterPatternCache:
    def __init__(self):
        self.patterns = defaultdict(list)
        self._compile_patterns()
    
    def _compile_patterns(self):
        # Cache common parameter patterns
        self.patterns['email'] = [re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')]
        self.patterns['phone'] = [re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')]
        self.patterns['date'] = [re.compile(r'\b(today|tomorrow|next \w+|yesterday)\b')]
    
    def extract_parameters(self, text):
        extracted = {}
        for param_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    extracted[param_type] = matches[0]
        return extracted
```

### 7. Monitoring and Profiling

#### Performance Monitoring
```python
import time
import logging
from intentai import detect_tool_and_params

logger = logging.getLogger(__name__)

def monitored_detection(user_input, tools, min_confidence=0.6):
    """Monitor detection performance."""
    start_time = time.time()
    
    try:
        result = detect_tool_and_params(user_input, tools, min_confidence)
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        # Log performance metrics
        logger.info(f"Detection completed in {processing_time:.2f}ms")
        logger.info(f"Input: {user_input}")
        logger.info(f"Result: {result}")
        
        # Alert on slow performance
        if processing_time > 50:  # 50ms threshold
            logger.warning(f"Slow detection: {processing_time:.2f}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise
```

#### Performance Metrics Collection
```python
import statistics
from collections import defaultdict

class PerformanceMetrics:
    def __init__(self):
        self.response_times = []
        self.confidence_scores = []
        self.success_rate = []
        self.tool_usage = defaultdict(int)
    
    def record_detection(self, user_input, result, response_time):
        self.response_times.append(response_time)
        
        if result:
            self.confidence_scores.append(result.get('confidence', 0))
            self.tool_usage[result.get('tool', 'unknown')] += 1
            self.success_rate.append(1)
        else:
            self.success_rate.append(0)
    
    def get_statistics(self):
        return {
            'avg_response_time': statistics.mean(self.response_times),
            'avg_confidence': statistics.mean(self.confidence_scores) if self.confidence_scores else 0,
            'success_rate': statistics.mean(self.success_rate),
            'tool_usage': dict(self.tool_usage),
            'total_detections': len(self.response_times)
        }
```

## Performance Best Practices Summary

1. **Tool Design**
   - Use descriptive function names
   - Provide clear docstrings with examples
   - Use consistent type hints
   - Include relevant default values

2. **Confidence Management**
   - Set appropriate confidence thresholds
   - Implement fallback strategies
   - Monitor confidence distributions

3. **System Architecture**
   - Use tool pools for different contexts
   - Implement lazy loading for large tool sets
   - Cache frequently used results
   - Monitor performance metrics

4. **Production Deployment**
   - Set up performance monitoring
   - Implement alerting for slow responses
   - Use load balancing for high-volume applications
   - Regular performance reviews

## Performance Checklist

- [ ] All functions have clear type hints
- [ ] Docstrings include relevant examples
- [ ] Confidence thresholds are appropriate for use case
- [ ] Performance monitoring is implemented
- [ ] Caching is used where appropriate
- [ ] Tool pools are organized by context
- [ ] Error handling includes performance considerations
- [ ] Regular performance testing is conducted

For detailed benchmark results and performance metrics, see the [Benchmarks Documentation](../benchmarks.md). 