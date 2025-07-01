# Tool Detector Documentation

Welcome to the Tool Detector documentation! This library provides a lightweight system for parsing natural language input into structured tool calls.

## Quick Start

```python
from tool_detector import detect_tool_and_params

# Detect calculator usage
result = detect_tool_and_params("Calculate 5 * 13")
print(result)
# DetectionResult(tool='calculator', params={'expression': '5 * 13'}, confidence=0.85)
```

## Installation

```bash
pip install tool-detector
```

## Features

- 🎯 **Intent Detection**: Parse natural language into structured tool calls
- 🔧 **Decorator-based Registration**: Use `@tool_call` decorator to register functions as tools
- 📊 **Confidence Scoring**: Get confidence scores for tool detection
- ✅ **Parameter Validation**: Automatic parameter extraction and validation with Pydantic
- 🎨 **Flexible Matching**: Support for multiple trigger phrases and examples
- 📋 **Schema Generation**: Generate JSON Schema for your tools
- 🚀 **Lightweight**: Minimal dependencies, fast performance

## Documentation Sections

- [Installation](installation.md)
- [Quick Start Guide](quickstart.md)
- [API Reference](api.md)
- [Examples](examples.md)
- [Advanced Usage](advanced.md)
- [CLI Reference](cli.md)
- [Contributing](contributing.md) 