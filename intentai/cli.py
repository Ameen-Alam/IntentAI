"""Command-line interface for IntentAI."""

import argparse
import json
import sys
from typing import List, Optional

from .detector import detect_tool_and_params
from .decorator import get_tools_from_functions, get_openapi_schema_for_tools
from .types import Tool


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IntentAI - AI-powered intent parsing system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  intentai "calculate 2 + 2"
  intentai "weather in London" --json
  intentai --schema-only
        """,
    )
    
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to analyze for tool detection"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Generate and output JSON schema for built-in tools"
    )
    
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (default: 0.5)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.schema_only:
        # Generate schema for built-in tools
        from .detector import BUILTIN_TOOLS
        schema = get_openapi_schema_for_tools(BUILTIN_TOOLS)
        print(json.dumps(schema, indent=2))
        return
    
    if not args.text:
        parser.error("Text argument is required unless --schema-only is used")
    
    try:
        # Detect tool in the provided text
        result = detect_tool_and_params(args.text)
        
        if result is None:
            if args.verbose:
                print("No tool detected in the provided text.")
            else:
                print("None")
            return
        
        # Apply confidence threshold
        if result.confidence < args.confidence_threshold:
            if args.verbose:
                print(f"Confidence {result.confidence:.2f} below threshold {args.confidence_threshold}")
            else:
                print("None")
            return
        
        if args.json:
            # Output as JSON
            output = {
                "tool": result.tool,
                "params": result.params,
                "confidence": round(result.confidence, 3)
            }
            print(json.dumps(output, indent=2))
        else:
            # Output as formatted text
            if args.verbose:
                print(f"Detected tool: {result.tool}")
                print(f"Parameters: {result.params}")
                print(f"Confidence: {result.confidence:.3f}")
            else:
                print(f"Tool: {result.tool}")
                print(f"Params: {result.params}")
    
    except Exception as e:
        if args.verbose:
            print(f"Error: {e}", file=sys.stderr)
        else:
            print("Error occurred during intent detection", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 