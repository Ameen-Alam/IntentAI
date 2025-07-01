# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-02

### 🚀 Major Release - Dynamic System Overhaul

This is a **major release** that completely transforms IntentAI into a dynamic, generic tool detection system with no hardcoded logic.

#### ✨ **New Features**

- **🎯 Completely Dynamic System**
  - Removed ALL hardcoded parameter extraction logic
  - Generic parameter extraction that works with ANY tool function
  - Automatic type inference from function signatures
  - Dynamic trigger phrase generation from function names

- **🔧 Enhanced Decorator System**
  - `@tool_call` decorator now supports parameter overrides
  - Automatic extraction of descriptions, triggers, and examples from docstrings
  - Support for complex parameter types (lists, dicts, Pydantic models)
  - Improved function metadata preservation

- **🎯 Intelligent Detection Engine**
  - Multi-factor confidence scoring system
  - Support for multiple tool candidates with similar confidence
  - Context-aware parameter extraction quality assessment
  - Configurable confidence thresholds

- **🛠 Production-Ready CLI**
  - Interactive mode for testing and development
  - Batch processing capabilities
  - JSON output support
  - Verbose debugging options
  - Cross-platform compatibility

- **📊 Enhanced Schema Generation**
  - Renamed `get_openapi_schema_for_tools` to `generate_json_schema`
  - Improved JSON Schema format
  - Better parameter type representation
  - Support for complex nested structures

#### 🔄 **Breaking Changes**

- **Function Rename**: `get_openapi_schema_for_tools()` → `generate_json_schema()`
- **Removed Hardcoded Logic**: All parameter-specific extraction patterns removed
- **Updated CLI**: New command structure and options
- **Decorator Changes**: Enhanced `@tool_call` decorator with new parameters

#### 🐛 **Bug Fixes**

- Fixed Unicode encoding issues in Windows terminals
- Resolved parameter extraction edge cases
- Improved error handling for malformed inputs
- Fixed confidence scoring inconsistencies
- Corrected schema generation for complex types

#### 📚 **Documentation**

- Complete README rewrite with dynamic system focus
- Updated API documentation
- Comprehensive examples for all features
- CLI usage guide
- Migration guide from v0.x

#### 🧪 **Testing**

- Comprehensive test suite with 3 test categories
- Local development testing
- Published package testing
- Feature demonstration examples
- Cross-platform compatibility testing

#### 🛠 **Developer Experience**

- Better error messages and debugging information
- Improved logging throughout the system
- Enhanced type hints and annotations
- Cleaner code organization
- Professional project structure

---

## [0.2.0] - 2025-07-01

### Added
- Enhanced parameter extraction with more patterns
- Improved confidence scoring algorithm
- Better error handling and validation
- CLI improvements with interactive mode
- Professional logging system

### Changed
- Updated parameter extraction logic for better accuracy
- Enhanced confidence calculation with multiple factors
- Improved CLI user experience

### Fixed
- Parameter extraction edge cases
- Confidence scoring inconsistencies
- CLI encoding issues

---

## [0.1.0] - 2025-07-01

### Added
- Initial release of IntentAI
- Basic tool detection functionality
- Parameter extraction from natural language
- `@tool_call` decorator for tool registration
- Simple CLI interface
- JSON Schema generation
- Basic confidence scoring

### Features
- Tool detection with trigger phrases
- Parameter extraction for common types
- Confidence scoring system
- Basic validation and error handling
- Documentation and examples 