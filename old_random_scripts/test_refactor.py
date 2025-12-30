#!/usr/bin/env python3
"""
Test script to verify the refactoring works correctly.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        from auicp.smart_logic import collect_all_files, is_binary_file
        print("✓ smart_logic imports successful")
    except ImportError as e:
        print(f"✗ smart_logic import failed: {e}")
        return False
    
    try:
        from auicp.file_processor import process_files
        print("✓ file_processor imports successful")
    except ImportError as e:
        print(f"✗ file_processor import failed: {e}")
        return False
    
    try:
        from auicp.gui import show_file_selection_gui
        print("✓ gui imports successful")
    except ImportError as e:
        print(f"✗ gui import failed: {e}")
        return False
    
    try:
        from auicp.main import main
        print("✓ main imports successful")
    except ImportError as e:
        print(f"✗ main import failed: {e}")
        return False
    
    return True

def test_config_loading():
    """Test that the configuration loads correctly."""
    print("\nTesting configuration loading...")
    
    try:
        from auicp.smart_logic import config, CODE_EXTENSIONS, MAX_FILE_SIZE
        print("✓ Configuration loaded successfully")
        print(f"  - Found {len(CODE_EXTENSIONS)} code extensions")
        print(f"  - Max file size: {MAX_FILE_SIZE:,} bytes")
        print(f"  - Sample extensions: {list(CODE_EXTENSIONS)[:5]}")
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_file_collection():
    """Test basic file collection functionality."""
    print("\nTesting file collection...")
    
    try:
        from auicp.smart_logic import collect_all_files
        files = collect_all_files()
        print(f"✓ File collection successful - found {len(files)} items")
        
        # Show a few examples
        if files:
            print("  Sample items:")
            for i, (abs_path, rel_path, is_checked) in enumerate(files[:3]):
                print(f"    {i+1}. {rel_path} ({'✓' if is_checked else '✗'})")
        
        return True
    except Exception as e:
        print(f"✗ File collection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== AI Code Prep GUI Refactoring Test ===\n")
    
    tests = [
        test_imports,
        test_config_loading,
        test_file_collection
    ]
    
    passed = 0
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{len(tests)} passed ===")
    
    if passed == len(tests):
        print("🎉 All tests passed! The refactoring appears to be working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
