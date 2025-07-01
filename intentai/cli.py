#!/usr/bin/env python3
"""
IntentAI CLI - Dynamic Tool Detection and Parameter Extraction

A command-line interface for IntentAI that provides interactive tool detection,
batch processing, and schema generation capabilities.
"""

import argparse
import json
import logging
import sys
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

# Add the package to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from intentai import (
        detect_tool_and_params,
        get_tools_from_functions,
        DetectionResult,
        generate_json_schema
    )
    from intentai.decorator import tool_call
except ImportError:
    print("❌ Error: Could not import IntentAI. Make sure it's installed correctly.")
    sys.exit(1)


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("intentai.log"),
        ],
    )


def load_tools_from_file(file_path: str) -> List:
    """Load tools from a Python file."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("tools_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find all functions decorated with @tool_call
        tools = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, '_tool_metadata'):
                tools.append(attr)
        
        if not tools:
            print(f"Warning: No tools found in {file_path}")
            return []
        
        return tools
    except Exception as e:
        print(f"Error loading tools from {file_path}: {e}")
        return []


def interactive_mode(tools: List) -> None:
    """Run interactive mode for testing tool detection."""
    print("\n" + "="*60)
    print("IntentAI Interactive Mode")
    print("="*60)
    print("Type 'quit' to exit, 'help' for commands, 'tools' to list available tools")
    print("="*60)
    
    available_tools = get_tools_from_functions(*tools)
    
    while True:
        try:
            user_input = input("\nEnter your request: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  help     - Show this help")
                print("  tools    - List available tools")
                print("  schema   - Generate JSON schema")
                print("  quit     - Exit interactive mode")
                continue
            elif user_input.lower() == 'tools':
                print(f"\nAvailable tools ({len(available_tools)}):")
                for i, tool in enumerate(available_tools, 1):
                    print(f"  {i}. {tool.name}")
                    if tool.description:
                        print(f"     Description: {tool.description}")
                    if tool.trigger_phrases:
                        print(f"     Triggers: {', '.join(tool.trigger_phrases)}")
                    print()
                continue
            elif user_input.lower() == 'schema':
                schema = generate_json_schema(available_tools)
                print("\nJSON Schema:")
                print(json.dumps(schema, indent=2))
                continue
            elif not user_input:
                continue
            
            # Detect tool and extract parameters
            result = detect_tool_and_params(user_input, available_tools)
            
            if result:
                if isinstance(result, list):
                    print(f"\nMultiple matches found ({len(result)}):")
                    for i, res in enumerate(result, 1):
                        print(f"\n{i}. Tool: {res['tool']}")
                        print(f"   Confidence: {res['confidence']:.2f}")
                        print(f"   Parameters: {res['parameters']}")
                else:
                    print(f"\nTool detected: {result['tool']}")
                    print(f"Confidence: {result['confidence']:.2f}")
                    print(f"Parameters: {result['parameters']}")
            else:
                print("\nNo tool detected. Try rephrasing your request.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


def detect_single_input(user_input: str, tools: List, verbose: bool = False) -> None:
    """Detect tool for a single input."""
    available_tools = get_tools_from_functions(*tools)
    
    if verbose:
        print(f"Input: {user_input}")
        print(f"Available tools: {[t.name for t in available_tools]}")
    
    result = detect_tool_and_params(user_input, available_tools)
    
    if result:
        if isinstance(result, list):
            print(f"Multiple matches found ({len(result)}):")
            for i, res in enumerate(result, 1):
                print(f"\n{i}. Tool: {res['tool']}")
                print(f"   Confidence: {res['confidence']:.2f}")
                print(f"   Parameters: {res['parameters']}")
        else:
            print(f"Tool: {result['tool']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Parameters: {result['parameters']}")
    else:
        print("No tool detected")


def generate_schema_output(tools: List, output_file: Optional[str] = None) -> None:
    """Generate and output JSON schema."""
    available_tools = get_tools_from_functions(*tools)
    schema = generate_json_schema(available_tools)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Schema saved to {output_file}")
    else:
        print(json.dumps(schema, indent=2))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IntentAI - Dynamic Tool Detection and Parameter Extraction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  intentai --interactive --tools my_tools.py
  intentai "weather in London" --tools my_tools.py
  intentai --schema --tools my_tools.py --output schema.json
  intentai --detect "calculate 2+2" --tools my_tools.py --verbose
        """
    )
    
    parser.add_argument(
        "--tools", 
        required=True,
        help="Python file containing @tool_call decorated functions"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--detect", "-d",
        help="Detect tool for a single input"
    )
    
    parser.add_argument(
        "--schema", "-s",
        action="store_true",
        help="Generate JSON schema for tools"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for schema generation"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="IntentAI 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Load tools
    if not Path(args.tools).exists():
        print(f"Error: Tools file '{args.tools}' not found")
        sys.exit(1)
    
    tools = load_tools_from_file(args.tools)
    if not tools:
        print(f"Error: No tools found in '{args.tools}'")
        sys.exit(1)
    
    # Execute requested action
    if args.interactive:
        interactive_mode(tools)
    elif args.detect:
        detect_single_input(args.detect, tools, args.verbose)
    elif args.schema:
        generate_schema_output(tools, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 