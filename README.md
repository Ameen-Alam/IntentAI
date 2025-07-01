# IntentAI

[![PyPI version](https://badge.fury.io/py/intentai.svg)](https://badge.fury.io/py/intentai)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Tests](https://github.com/ameenalam/intentai/workflows/Tests/badge.svg)](https://github.com/ameenalam/intentai/actions)
[![Documentation](https://readthedocs.org/projects/intentai/badge/?version=latest)](https://intentai.readthedocs.io/)

AI-powered intent parsing system that converts natural language into structured tool calls. IntentAI understands what you want and transforms your requests into actionable commands with confidence scoring and validation.

## Features

- 🎯 **Intent Detection**: Parse natural language into structured tool calls
- 🔧 **Decorator-based Registration**: Use `@tool_call` decorator to register functions as tools
- 📊 **Confidence Scoring**: Get confidence scores for tool detection
- ✅ **Parameter Validation**: Automatic parameter extraction and validation with Pydantic
- 🎨 **Flexible Matching**: Support for multiple trigger phrases and examples
- 📋 **Schema Generation**: Generate JSON Schema for your tools
- 🚀 **Lightweight**: Minimal dependencies, fast performance

## Installation

```bash
pip install intentai
```

## Quick Start

### Basic Usage

```python
from intentai import detect_tool_and_params

# Detect calculator usage
result = detect_tool_and_params("Calculate 5 * 13")
print(result)
# {'tool': 'calculator', 'params': {'expression': '5 * 13'}}

# Detect weather lookup
result = detect_tool_and_params("Weather in London")
print(result)
# {'tool': 'get_weather', 'params': {'city': 'London'}}
```

### Decorator-based Approach

```python
from intentai import tool_call, get_tools_from_functions, detect_tool_and_params
from pydantic import BaseModel

class WeatherParams(BaseModel):
    city: str
    country: str = "US"

@tool_call(
    name="get_weather",
    description="Get current weather information for a city",
    trigger_phrases=["weather in", "weather for", "temperature in"],
    examples=[
        "weather in New York",
        "what's the temperature in London?",
        "weather for Tokyo"
    ]
)
def get_weather(city: str, country: str = "US") -> str:
    """Get weather information for a city."""
    return f"Weather in {city}, {country}: Sunny, 25°C"

# Register your functions
tools = get_tools_from_functions([get_weather])

# Detect tools in user input
result = detect_tool_and_params("What's the weather like in Paris?", tools)
print(result)
# DetectionResult(tool='get_weather', params={'city': 'Paris', 'country': 'US'}, confidence=0.85)
```

## Advanced Features

### Parameter Validation with Pydantic

```python
from pydantic import BaseModel, Field

class CalculatorParams(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")
    precision: int = Field(default=2, ge=0, le=10, description="Decimal precision")

@tool_call(
    name="calculator",
    description="Evaluate mathematical expressions",
    trigger_phrases=["calculate", "compute", "what is"],
    examples=["calculate 2 + 2", "what is 10 * 5", "compute 100 / 4"]
)
def calculator(expression: str, precision: int = 2) -> float:
    """Evaluate a mathematical expression."""
    return round(eval(expression), precision)
```

### Schema Generation

```python
from intentai import get_openapi_schema_for_tools

# Generate JSON Schema for your tools
schema = get_openapi_schema_for_tools(tools)
print(schema)
```

## API Reference

### Core Functions

- `detect_tool_and_params(text: str, tools: List[Tool] = None) -> DetectionResult`
- `get_tools_from_functions(functions: List[Callable]) -> List[Tool]`
- `get_openapi_schema_for_tools(tools: List[Tool]) -> Dict`

### Decorators

- `@tool_call(name: str, description: str, trigger_phrases: List[str], examples: List[str])`

### Data Models

- `Tool`: Represents a tool with metadata and parameters
- `ToolParameter`: Represents a tool parameter with type and validation
- `DetectionResult`: Result of tool detection with confidence score
- `ParameterType`: Enum of supported parameter types

## Examples

Check out the [examples directory](https://github.com/ameenalam/tool-detector/tree/main/examples) for more comprehensive usage examples:

- [Basic Usage](https://github.com/ameenalam/tool-detector/blob/main/examples/basic_usage.py)
- [Decorator Examples](https://github.com/ameenalam/tool-detector/blob/main/examples/decorator_examples.py)
- [Advanced Features](https://github.com/ameenalam/tool-detector/blob/main/examples/advanced_features.py)

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ameenalam/intentai.git
   cd intentai
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tool_detector --cov-report=html

# Run specific test file
pytest tests/test_detector.py
```

### Code Quality

```bash
# Format code
black intentai tests examples

# Sort imports
isort intentai tests examples

# Type checking
mypy intentai

# Linting
flake8 intentai tests examples
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/ameenalam/intentai/blob/main/CONTRIBUTING.md) for details.

## Documentation

For detailed documentation, visit [intentai.readthedocs.io](https://intentai.readthedocs.io/).

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ameenalam/intentai/blob/main/LICENSE) file for details.

## Changelog

See [CHANGELOG.md](https://github.com/ameenalam/intentai/blob/main/CHANGELOG.md) for a list of changes and version history. 