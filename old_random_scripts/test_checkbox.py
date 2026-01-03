#!/usr/bin/env python3
"""
Simple test to check if checkboxes work in QTreeWidget
"""

import sys
from PySide6 import QtWidgets, QtCore
from auicp.apptheme import get_checkbox_style_dark, get_checkbox_style_light, apply_dark_palette

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Apply dark theme for testing
    apply_dark_palette(app)
    
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Checkbox Test")
    window.setGeometry(100, 100, 400, 300)
    
    central = QtWidgets.QWidget()
    window.setCentralWidget(central)
    layout = QtWidgets.QVBoxLayout(central)
    
    # Add a label
    label = QtWidgets.QLabel("Test checkbox functionality:")
    layout.addWidget(label)
    
    # Create tree widget
    tree = QtWidgets.QTreeWidget()
    tree.setHeaderLabels(["Item", "Type"])
    tree.setStyleSheet(get_checkbox_style_dark())
    
    # Add some test items
    for i in range(5):
        item = QtWidgets.QTreeWidgetItem(tree, [f"Item {i+1}", "Test"])
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)
    
    # Connect signal to test functionality
    def on_item_changed(item, column):
        if column == 0:
            state = "checked" if item.checkState(0) == QtCore.Qt.Checked else "unchecked"
            print(f"Item '{item.text(0)}' is now {state}")
    
    tree.itemChanged.connect(on_item_changed)
    layout.addWidget(tree)
    
    # Add toggle button
    def toggle_theme():
        current_style = tree.styleSheet()
        if "2b2b2b" in current_style:  # dark theme
            tree.setStyleSheet(get_checkbox_style_light())
            print("Switched to light theme")
        else:
            tree.setStyleSheet(get_checkbox_style_dark())
            print("Switched to dark theme")
    
    toggle_btn = QtWidgets.QPushButton("Toggle Theme")
    toggle_btn.clicked.connect(toggle_theme)
    layout.addWidget(toggle_btn)
    
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
