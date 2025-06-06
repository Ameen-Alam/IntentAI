# Tool Detector

A lightweight Python library for detecting tools and extracting parameters from user text. This library provides a simple way to parse natural language input into structured tool calls.

## Installation

```bash
pip install tool-detector
```

## Quick Start

```python
from tool_detector import detect_tool_and_params

# Detect calculator usage
result = detect_tool_and_params("Calculate 5 * 13")
print(result)
# {'tool': 'calculator', 'params': {'expression': '5 * 13'}}

# Detect weather lookup
result = detect_tool_and_params("Weather in London")
print(result)
# {'tool': 'get_weather', 'params': {'city': 'London'}}

# Detect stock lookup
result = detect_tool_and_params("Stock price of MSFT")
print(result)
# {'tool': 'lookup_stock', 'params': {'symbol': 'MSFT'}}
```

## Supported Tools

1. **Calculator**
   - Trigger phrases: "calculate", "what is"
   - Parameter: `expression` (arithmetic expression)

2. **Weather Lookup**
   - Trigger phrase: "weather in"
   - Parameter: `city` (city name)

3. **Stock Price Lookup**
   - Trigger phrase: "stock price of"
   - Parameter: `symbol` (stock ticker)

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tool-detector.git
   cd tool-detector
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License - see LICENSE file for details. 