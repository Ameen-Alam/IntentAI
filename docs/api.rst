API Reference
============

Core Functions
-------------

detect_tool_and_params
~~~~~~~~~~~~~~~~~~~~~

.. function:: detect_tool_and_params(user_input: str, tools: List[Tool], min_confidence: float = 0.6) -> Optional[DetectionResult] | List[DetectionResult]

   Detect which tool to use and extract its parameters from natural language input.

   **Parameters:**

   * **user_input** (str) -- Natural language input to analyze
   * **tools** (List[Tool]) -- List of available tools
   * **min_confidence** (float, optional) -- Minimum confidence threshold (default: 0.6)

   **Returns:**

   * **DetectionResult | List[DetectionResult]** -- Single result or list of candidates if multiple matches found

   **Example:**

   .. code-block:: python

      from intentai import detect_tool_and_params, get_tools_from_functions
      from my_tools import calculator, weather_checker

      tools = get_tools_from_functions(calculator, weather_checker)
      result = detect_tool_and_params("calculate 2+2", tools)

      if result:
          print(f"Tool: {result['tool']}")
          print(f"Parameters: {result['parameters']}")

get_tools_from_functions
~~~~~~~~~~~~~~~~~~~~~~~

.. function:: get_tools_from_functions(*functions) -> List[Tool]

   Extract tool definitions from decorated functions.

   **Parameters:**

   * **\*functions** -- Variable number of decorated functions

   **Returns:**

   * **List[Tool]** -- List of tool definitions

   **Example:**

   .. code-block:: python

      from intentai import get_tools_from_functions
      from my_tools import calculator, weather_checker

      tools = get_tools_from_functions(calculator, weather_checker)
      print(f"Registered {len(tools)} tools")

generate_json_schema
~~~~~~~~~~~~~~~~~~~

.. function:: generate_json_schema(tools: List[Tool]) -> Dict

   Generate JSON Schema for tools.

   **Parameters:**

   * **tools** (List[Tool]) -- List of tools

   **Returns:**

   * **Dict** -- JSON Schema dictionary

   **Example:**

   .. code-block:: python

      from intentai import generate_json_schema, get_tools_from_functions
      from my_tools import calculator, weather_checker

      tools = get_tools_from_functions(calculator, weather_checker)
      schema = generate_json_schema(tools)
      
      import json
      print(json.dumps(schema, indent=2))

Decorator
---------

tool_call
~~~~~~~~~

.. function:: @tool_call(name: Optional[str] = None, description: Optional[str] = None, trigger_phrases: Optional[List[str]] = None, examples: Optional[List[str]] = None, parameters: Optional[Dict] = None)

   Decorator to register a function as a tool.

   **Parameters:**

   * **name** (str, optional) -- Custom tool name (defaults to function name)
   * **description** (str, optional) -- Tool description (extracted from docstring if not provided)
   * **trigger_phrases** (List[str], optional) -- Trigger phrases for detection (auto-generated if not provided)
   * **examples** (List[str], optional) -- Example inputs (extracted from docstring if not provided)
   * **parameters** (Dict, optional) -- Parameter overrides

   **Example:**

   .. code-block:: python

      from intentai import tool_call

      @tool_call(
          name="weather_checker",
          description="Get weather information for a location",
          trigger_phrases=["weather", "temperature", "forecast"],
          examples=["weather in London", "temperature in Tokyo"]
      )
      def get_weather(location: str, units: str = "celsius") -> str:
          """Get weather information for a location."""
          return f"Weather in {location}: 20°{units[0].upper()}"

Data Models
----------

Tool
~~~~

.. class:: Tool

   Represents a tool with its metadata and parameters.

   **Attributes:**

   * **name** (str) -- Tool name
   * **description** (str) -- Tool description
   * **trigger_phrases** (List[str]) -- Trigger phrases for detection
   * **examples** (List[str]) -- Example inputs
   * **parameters** (Dict[str, Any]) -- Parameter definitions
   * **function** (Callable) -- The actual function to call

DetectionResult
~~~~~~~~~~~~~~

.. class:: DetectionResult

   Represents the result of tool detection.

   **Attributes:**

   * **tool** (str) -- Detected tool name
   * **confidence** (float) -- Confidence score (0.0 to 1.0)
   * **parameters** (Dict[str, Any]) -- Extracted parameters
   * **missing_parameters** (List[str], optional) -- Missing required parameters
   * **validation_errors** (List[str], optional) -- Parameter validation errors

Error Handling
-------------

The API provides comprehensive error handling for various scenarios:

* **No tool detected** -- Returns None when no tool matches the input
* **Multiple candidates** -- Returns a list of DetectionResult objects
* **Parameter extraction failures** -- Includes missing_parameters in the result
* **Validation errors** -- Includes validation_errors in the result

**Example:**

.. code-block:: python

   from intentai import detect_tool_and_params, get_tools_from_functions
   from my_tools import calculator

   tools = get_tools_from_functions(calculator)
   result = detect_tool_and_params("calculate", tools)

   if result:
       if isinstance(result, list):
           print("Multiple matches found:")
           for res in result:
               print(f"- {res['tool']} (confidence: {res['confidence']:.2f})")
       else:
           print(f"Tool: {result['tool']}")
           if result.get('missing_parameters'):
               print(f"Missing: {result['missing_parameters']}")
           if result.get('validation_errors'):
               print(f"Errors: {result['validation_errors']}")
   else:
       print("No tool detected") 