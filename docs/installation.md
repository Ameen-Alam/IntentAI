# Installation

## Requirements

Tool Detector requires Python 3.8 or higher.

## Installing from PyPI

The easiest way to install Tool Detector is using pip:

```bash
pip install tool-detector
```

## Installing from Source

If you want to install the latest development version:

```bash
git clone https://github.com/ameenalam/tool-detector.git
cd tool-detector
pip install -e .
```

## Development Installation

For development, install with development dependencies:

```bash
git clone https://github.com/ameenalam/tool-detector.git
cd tool-detector
pip install -e ".[dev]"
```

This installs additional tools for development:
- pytest for testing
- black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting
- pre-commit for git hooks

## Verifying Installation

You can verify the installation by running:

```python
import tool_detector
print(tool_detector.__version__)
```

Or test the CLI:

```bash
tool-detector --help
```

## Dependencies

Tool Detector has minimal dependencies:
- pydantic >= 2.0.0 (for data validation and serialization)

Optional dependencies for development:
- pytest >= 7.0 (testing)
- black >= 23.0 (code formatting)
- isort >= 5.0 (import sorting)
- mypy >= 1.0 (type checking)
- flake8 >= 6.0 (linting)
- pre-commit >= 3.0 (git hooks) 