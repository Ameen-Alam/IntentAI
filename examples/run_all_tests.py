#!/usr/bin/env python3
"""
Master test runner for IntentAI.

This script runs both local code tests and published package tests
to ensure everything works correctly in both environments.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_test(test_file: str, description: str) -> bool:
    """Run a test file and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {description}")
    print(f"{'='*60}")
    
    try:
        # Run the test file
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"STDERR: {result.stderr}")
        
        # Check success
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def check_installation() -> bool:
    """Check if IntentAI is properly installed."""
    print(f"\n{'='*60}")
    print("🔍 Checking IntentAI Installation")
    print(f"{'='*60}")
    
    try:
        # Try to import from PyPI
        import intentai
        print(f"✅ IntentAI imported successfully from PyPI")
        print(f"   Version: {intentai.__version__}")
        print(f"   Available functions: {intentai.__all__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import IntentAI from PyPI: {e}")
        print("   Make sure to install it first: pip install intentai")
        return False


def check_local_code() -> bool:
    """Check if local code is accessible."""
    print(f"\n{'='*60}")
    print("🔍 Checking Local IntentAI Code")
    print(f"{'='*60}")
    
    try:
        # Add local path
        local_path = Path(__file__).parent.parent
        sys.path.insert(0, str(local_path))
        
        # Try to import local code
        from intentai import detect_tool_and_params
        print(f"✅ Local IntentAI code accessible")
        print(f"   Path: {local_path}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import local IntentAI code: {e}")
        return False


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print(f"\n{'='*60}")
    print("🚀 IntentAI Comprehensive Test Suite")
    print(f"{'='*60}")
    
    # Check installations
    pypi_ok = check_installation()
    local_ok = check_local_code()
    
    if not pypi_ok and not local_ok:
        print("\n❌ Neither PyPI nor local code is accessible!")
        print("Please ensure IntentAI is properly installed or the local code is available.")
        return False
    
    # Test results tracking
    test_results = []
    
    # Run local code tests (if available)
    if local_ok:
        local_test_file = Path(__file__).parent / "test_local_code.py"
        if local_test_file.exists():
            success = run_test(
                str(local_test_file),
                "Local Code Tests"
            )
            test_results.append(("Local Code", success))
        else:
            print("⚠️ Local test file not found")
    
    # Run published package tests (if available)
    if pypi_ok:
        published_test_file = Path(__file__).parent / "test_published_package.py"
        if published_test_file.exists():
            success = run_test(
                str(published_test_file),
                "Published Package Tests"
            )
            test_results.append(("Published Package", success))
        else:
            print("⚠️ Published package test file not found")
    
    # Run comprehensive example (if available)
    comprehensive_file = Path(__file__).parent / "comprehensive_example.py"
    if comprehensive_file.exists():
        success = run_test(
            str(comprehensive_file),
            "Comprehensive Example"
        )
        test_results.append(("Comprehensive Example", success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! IntentAI is working correctly.")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Please check the output above.")
        return False


def run_quick_test():
    """Run a quick functionality test."""
    print(f"\n{'='*60}")
    print("⚡ Quick Functionality Test")
    print(f"{'='*60}")
    
    try:
        # Try to import and use basic functionality
        from intentai import detect_tool_and_params, tool_call, get_tools_from_functions
        
        @tool_call(
            name="test_tool",
            description="A test tool",
            trigger_phrases=["test"],
            examples=["test this"]
        )
        def test_tool(message: str) -> str:
            return f"Test successful: {message}"
        
        # Register tool
        tools = get_tools_from_functions([test_tool])
        
        # Test detection
        result = detect_tool_and_params("test this message", tools)
        
        if result and result.tool == "test_tool":
            print("✅ Basic functionality test passed!")
            print(f"   Detected tool: {result.tool}")
            print(f"   Confidence: {result.confidence:.3f}")
            return True
        else:
            print("❌ Basic functionality test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IntentAI Test Suite")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only quick functionality test"
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Run only local code tests"
    )
    parser.add_argument(
        "--published-only",
        action="store_true",
        help="Run only published package tests"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_test()
        sys.exit(0 if success else 1)
    
    if args.local_only:
        print("Running local code tests only...")
        local_test_file = Path(__file__).parent / "test_local_code.py"
        if local_test_file.exists():
            success = run_test(str(local_test_file), "Local Code Tests")
            sys.exit(0 if success else 1)
        else:
            print("❌ Local test file not found")
            sys.exit(1)
    
    if args.published_only:
        print("Running published package tests only...")
        published_test_file = Path(__file__).parent / "test_published_package.py"
        if published_test_file.exists():
            success = run_test(str(published_test_file), "Published Package Tests")
            sys.exit(0 if success else 1)
        else:
            print("❌ Published package test file not found")
            sys.exit(1)
    
    # Run comprehensive tests
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 