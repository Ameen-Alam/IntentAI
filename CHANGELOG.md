# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CLI interface with `tool-detector` command
- JSON schema generation for tools
- Confidence scoring for tool detection
- Parameter validation with Pydantic models
- Decorator-based tool registration with `@tool_call`
- Support for multiple trigger phrases and examples
- Built-in tools: calculator, weather lookup, stock lookup

### Changed
- Improved parameter extraction logic
- Enhanced tool detection accuracy
- Better error handling and validation

### Fixed
- Fixed parameter extraction for complex expressions
- Improved confidence scoring algorithm
- Fixed docstring parsing in decorator

## [0.1.0] - 2025-01-XX

### Added
- Initial release
- Basic tool detection functionality
- Parameter extraction from natural language
- Support for simple arithmetic and text-based tools
- Core API with `detect_tool_and_params` function
- Type definitions and data models 