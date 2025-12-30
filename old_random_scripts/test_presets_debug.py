#!/usr/bin/env python3

import sys
import os
import logging

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from PySide6 import QtWidgets, QtCore
from auicp.gui import GlobalPresetManager, FileSelectionGUI

def test_global_preset_manager():
    print("=== Testing GlobalPresetManager ===")
    
    # Test the global preset manager directly
    manager = GlobalPresetManager()
    print(f"Settings object: {manager.settings}")
    
    if manager.settings:
        print("QSettings initialized successfully")
        presets = manager.get_all_presets()
        print(f"Found {len(presets)} presets: {[p[0] for p in presets]}")
        for label, text in presets:
            print(f"  - {label}: {text[:50]}...")
    else:
        print("QSettings failed to initialize")

def test_gui_creation():
    print("\n=== Testing GUI Creation ===")
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    
    # Create a minimal file list for testing
    test_files = [
        (os.path.abspath(__file__), os.path.basename(__file__), True),
        (os.path.abspath("README.md"), "README.md", False) if os.path.exists("README.md") else (os.path.abspath(__file__), "test_file2.py", False)
    ]
    
    print(f"Creating GUI with test files: {[f[1] for f in test_files]}")
    
    try:
        gui = FileSelectionGUI(test_files)
        print("GUI created successfully")
        print(f"Preset flow layout widget count: {gui.preset_flow_layout.count()}")
        
        # Check what widgets are in the layout
        for i in range(gui.preset_flow_layout.count()):
            item = gui.preset_flow_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                print(f"  Widget {i}: {type(widget).__name__} - {widget.text() if hasattr(widget, 'text') else 'No text'}")
        
        gui.show()
        return gui
    except Exception as e:
        print(f"Error creating GUI: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_global_preset_manager()
    gui = test_gui_creation()
    
    if gui:
        print("\nGUI created successfully. Close the window to continue...")
        # Don't run the event loop, just show the window briefly
        QtCore.QTimer.singleShot(100, lambda: print("Timer fired - GUI should be visible"))
    else:
        print("Failed to create GUI")
