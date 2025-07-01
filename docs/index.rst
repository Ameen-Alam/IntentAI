IntentAI Documentation
=====================

**IntentAI** is a powerful, dynamic tool detection and parameter extraction system that converts natural language into structured tool calls. It works with **ANY** tools without hardcoded logic - completely generic and future-proof.

.. image:: https://badge.fury.io/py/intentai.svg
   :target: https://badge.fury.io/py/intentai
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

Key Features
-----------

✨ **Completely Dynamic System**
   - No hardcoded logic - Works with any tool function automatically
   - Generic parameter extraction for any function signature
   - Automatic type inference from function annotations
   - Dynamic trigger phrase generation from function names

🎯 **Intelligent Detection**
   - Fuzzy matching with confidence scoring
   - Multiple candidates handling
   - Context-aware parameter extraction quality assessment
   - Configurable confidence thresholds

🔧 **Developer-Friendly**
   - Simple `@tool_call` decorator for easy tool registration
   - Automatic metadata extraction from docstrings
   - Type safety with Pydantic integration
   - JSON Schema generation for API integration

🛠 **Production Ready**
   - Comprehensive CLI with interactive mode
   - Robust error handling and validation
   - Professional logging for debugging
   - Cross-platform compatibility

Quick Start
----------

Installation
~~~~~~~~~~~

.. code-block:: bash

   pip install intentai

Basic Usage
~~~~~~~~~~

.. code-block:: python

   from intentai import tool_call, get_tools_from_functions, detect_tool_and_params

   @tool_call(
       name="weather_checker",
       description="Get weather information for a location",
       trigger_phrases=["weather", "temperature", "forecast"],
       examples=["weather in London", "temperature in Tokyo"]
   )
   def get_weather(location: str, units: str = "celsius") -> str:
       """Get weather information for a location."""
       return f"Weather in {location}: 20°{units[0].upper()}"

   # Register tools
   tools = get_tools_from_functions(get_weather)

   # Detect tool and extract parameters
   result = detect_tool_and_params("weather in London", tools)

   if result:
       print(f"Tool: {result['tool']}")
       print(f"Confidence: {result['confidence']:.2f}")
       print(f"Parameters: {result['parameters']}")

CLI Usage
~~~~~~~~~

.. code-block:: bash

   # Interactive mode
   intentai --interactive --tools my_tools.py

   # Single detection
   intentai "calculate 15 + 25" --tools my_tools.py

   # Generate schema
   intentai --schema --tools my_tools.py

Table of Contents
----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   cli
   examples
   advanced
   contributing

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 