Command Line Interface
=====================

IntentAI provides a comprehensive command-line interface for tool detection, interactive testing, and schema generation.

Installation
-----------

The CLI is automatically installed with the package:

.. code-block:: bash

   pip install intentai

Basic Usage
----------

The CLI requires a Python file containing `@tool_call` decorated functions:

.. code-block:: bash

   intentai --tools my_tools.py [options]

Interactive Mode
---------------

Run in interactive mode for testing and development:

.. code-block:: bash

   intentai --interactive --tools my_tools.py
   # or
   intentai -i --tools my_tools.py

Interactive mode provides:

* Real-time tool detection testing
* Available tools listing
* JSON schema generation
* Help system

**Interactive Commands:**

* ``help`` - Show available commands
* ``tools`` - List all available tools with descriptions
* ``schema`` - Generate and display JSON schema
* ``quit`` or ``exit`` - Exit interactive mode

Single Detection
---------------

Detect tools for a specific input:

.. code-block:: bash

   intentai --detect "calculate 2+2" --tools my_tools.py
   # or
   intentai -d "weather in London" --tools my_tools.py

Schema Generation
----------------

Generate JSON schema for tools:

.. code-block:: bash

   # Display schema to console
   intentai --schema --tools my_tools.py
   
   # Save schema to file
   intentai --schema --tools my_tools.py --output schema.json
   # or
   intentai -s --tools my_tools.py -o schema.json

Verbose Output
--------------

Enable verbose output for debugging:

.. code-block:: bash

   intentai --detect "calculate 2+2" --tools my_tools.py --verbose
   # or
   intentai -d "weather in London" --tools my_tools.py -v

Verbose mode includes:

* Detailed logging information
* Available tools listing
* Parameter extraction details
* Confidence scoring breakdown

Command Reference
----------------

.. program:: intentai

.. option:: --tools <file>

   Python file containing @tool_call decorated functions (required)

.. option:: --interactive, -i

   Run in interactive mode

.. option:: --detect <input>, -d <input>

   Detect tool for specific input

.. option:: --schema, -s

   Generate JSON schema for tools

.. option:: --output <file>, -o <file>

   Output file for schema generation

.. option:: --verbose, -v

   Enable verbose output

.. option:: --version

   Show version information

.. option:: --help, -h

   Show help message

Examples
--------

Basic Tool Detection
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create a tools file
   cat > my_tools.py << 'EOF'
   from intentai import tool_call
   
   @tool_call(name="calculator")
   def calculate(expression: str) -> float:
       return eval(expression)
   
   @tool_call(name="weather")
   def get_weather(location: str) -> str:
       return f"Weather in {location}: Sunny"
   EOF
   
   # Test detection
   intentai --detect "calculate 15 + 25" --tools my_tools.py
   intentai --detect "weather in Tokyo" --tools my_tools.py

Interactive Testing
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   intentai --interactive --tools my_tools.py
   
   # In interactive mode:
   Enter your request: calculate 2+2
   Tool detected: calculator
   Confidence: 0.85
   Parameters: {'expression': '2+2'}
   
   Enter your request: weather in London
   Tool detected: weather
   Confidence: 0.92
   Parameters: {'location': 'London'}

Schema Generation
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Generate and display schema
   intentai --schema --tools my_tools.py
   
   # Save schema to file
   intentai --schema --tools my_tools.py --output tools_schema.json

Verbose Debugging
~~~~~~~~~~~~~~~~

.. code-block:: bash

   intentai --detect "calculate 2+2" --tools my_tools.py --verbose
   
   # Output includes:
   # - Available tools listing
   # - Parameter extraction details
   # - Confidence scoring breakdown
   # - Detailed logging

Error Handling
-------------

The CLI provides clear error messages for common issues:

**File Not Found:**
.. code-block:: bash

   Error: Tools file 'nonexistent.py' not found

**No Tools Found:**
.. code-block:: bash

   Error: No tools found in 'empty_file.py'

**Import Errors:**
.. code-block:: bash

   Error loading tools from my_tools.py: No module named 'missing_module'

**Detection Failures:**
.. code-block:: bash

   No tool detected. Try rephrasing your request.

Logging
-------

The CLI creates a log file `intentai.log` in the current directory with detailed information about:

* Tool loading
* Detection attempts
* Parameter extraction
* Confidence calculations
* Errors and warnings

Configuration
------------

The CLI respects the following environment variables:

* ``INTENTAI_LOG_LEVEL`` - Set logging level (DEBUG, INFO, WARNING, ERROR)
* ``INTENTAI_MIN_CONFIDENCE`` - Set default minimum confidence threshold

.. code-block:: bash

   export INTENTAI_LOG_LEVEL=DEBUG
   export INTENTAI_MIN_CONFIDENCE=0.7
   intentai --detect "calculate 2+2" --tools my_tools.py 