#!/usr/bin/env python3
"""
Debug script to test the GUI functionality.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

def debug_file_collection():
    """Debug the file collection process."""
    print("=== Debugging File Collection ===\n")
    
    try:
        from auicp.smart_logic import collect_all_files, is_binary_file
        files = collect_all_files()
        
        print(f"Total files collected: {len(files)}")
        print("\nFirst 10 files:")
        
        for i, (abs_path, rel_path, is_checked) in enumerate(files[:10]):
            is_binary = is_binary_file(abs_path) if os.path.isfile(abs_path) else False
            file_type = "DIR" if os.path.isdir(abs_path) else ("BIN" if is_binary else "TEXT")
            check_status = "✓" if is_checked else "✗"
            
            print(f"  {i+1:2d}. {check_status} [{file_type:4s}] {rel_path}")
        
        # Count by type
        text_files = sum(1 for abs_path, _, _ in files if os.path.isfile(abs_path) and not is_binary_file(abs_path))
        binary_files = sum(1 for abs_path, _, _ in files if os.path.isfile(abs_path) and is_binary_file(abs_path))
        directories = sum(1 for abs_path, _, _ in files if os.path.isdir(abs_path))
        checked_count = sum(1 for _, _, is_checked in files if is_checked)
        
        print(f"\nSummary:")
        print(f"  Text files: {text_files}")
        print(f"  Binary files: {binary_files}")
        print(f"  Directories: {directories}")
        print(f"  Initially checked: {checked_count}")
        
        return files
        
    except Exception as e:
        print(f"Error in file collection: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_minimal_gui():
    """Test minimal GUI functionality."""
    print("\n=== Testing Minimal GUI ===\n")
    
    try:
        from PySide6 import QtWidgets, QtCore
        from auicp.gui import FileSelectionGUI
        
        # Create a minimal test
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        
        # Create test files list
        test_files = [
            (os.path.abspath("test_refactor.py"), "test_refactor.py", True),
            (os.path.abspath("pyproject.toml"), "pyproject.toml", True),
            (os.path.abspath("README.md"), "README.md", False),
        ]
        
        print("Creating GUI with test files...")
        gui = FileSelectionGUI(test_files)
        
        print("GUI created successfully!")
        print("You should see:")
        print("- A file tree with 3 test files")
        print("- test_refactor.py and pyproject.toml should be checked")
        print("- README.md should be unchecked")
        print("- Checkboxes should be clickable and show checkmarks when selected")
        
        gui.show()
        
        # Don't start the event loop automatically
        print("\nGUI window should be visible now.")
        print("Test the checkboxes and close the window when done.")
        
        return True
        
    except Exception as e:
        print(f"Error creating GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debugging tests."""
    print("AI Code Prep GUI - Debug Mode\n")
    
    # Test 1: File collection
    files = debug_file_collection()
    
    if not files:
        print("❌ File collection failed. Cannot proceed with GUI test.")
        return False
    
    # Test 2: Minimal GUI
    if not test_minimal_gui():
        print("❌ GUI creation failed.")
        return False
    
    print("\n✅ Debug tests completed.")
    print("If you can see the GUI window and interact with checkboxes, the refactoring is working!")
    
    return True

if __name__ == "__main__":
    main()
