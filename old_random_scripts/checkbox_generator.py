#!/usr/bin/env python3
"""
Checkbox Image Generator

This script creates custom checkbox images for Qt applications.
You can modify the colors, sizes, and styles to create different variations.

Usage: python checkbox_generator.py
"""

import sys
import os
from PySide6 import QtWidgets, QtGui, QtCore

class CheckboxGenerator:
    def __init__(self):
        """Initialize the checkbox generator with customizable parameters."""
        
        # Customizable parameters - modify these to change the appearance
        self.size = 16  # Checkbox size (width and height)
        self.border_width = 2  # Border thickness
        self.border_radius = 2  # Corner rounding
        
        # Light theme colors
        self.light_border_color = "#aaaaaa"        # Gray border for unchecked
        self.light_bg_color = "#ffffff"            # White background
        self.light_checked_border = "#0078D4"      # Blue border for checked
        self.light_checkmark_color = "#0078D4"     # Blue checkmark
        
        # Dark theme colors
        self.dark_border_color = "#aaaaaa"         # Gray border for unchecked
        self.dark_bg_color = "#2b2b2b"             # Dark background
        self.dark_checked_border = "#0078D4"       # Blue border for checked
        self.dark_checkmark_color = "#0078D4"      # Blue checkmark
        
        # Output directory
        self.output_dir = "images"
    
    def create_unchecked_checkbox(self, dark_theme=False):
        """Create an unchecked checkbox (just border and background)."""
        pixmap = QtGui.QPixmap(self.size, self.size)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Choose colors based on theme
        if dark_theme:
            border_color = self.dark_border_color
            bg_color = self.dark_bg_color
        else:
            border_color = self.light_border_color
            bg_color = self.light_bg_color
        
        # Draw border and background
        pen = QtGui.QPen(QtGui.QColor(border_color))
        pen.setWidth(self.border_width)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(bg_color)))
        
        # Calculate inner rectangle (accounting for border width)
        margin = self.border_width
        inner_size = self.size - (2 * margin)
        painter.drawRoundedRect(margin, margin, inner_size, inner_size, 
                              self.border_radius, self.border_radius)
        
        painter.end()
        return pixmap
    
    def create_checked_checkbox(self, dark_theme=False):
        """Create a checked checkbox (border, background, and checkmark)."""
        pixmap = QtGui.QPixmap(self.size, self.size)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Choose colors based on theme
        if dark_theme:
            border_color = self.dark_checked_border
            bg_color = self.dark_bg_color
            checkmark_color = self.dark_checkmark_color
        else:
            border_color = self.light_checked_border
            bg_color = self.light_bg_color
            checkmark_color = self.light_checkmark_color
        
        # Draw border and background
        pen = QtGui.QPen(QtGui.QColor(border_color))
        pen.setWidth(self.border_width)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(bg_color)))
        
        # Calculate inner rectangle (accounting for border width)
        margin = self.border_width
        inner_size = self.size - (2 * margin)
        painter.drawRoundedRect(margin, margin, inner_size, inner_size, 
                              self.border_radius, self.border_radius)
        
        # Draw checkmark
        pen = QtGui.QPen(QtGui.QColor(checkmark_color))
        pen.setWidth(self.border_width)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        
        # Checkmark coordinates (adjust these to change checkmark shape)
        # These work well for a 16x16 checkbox
        check_start_x = int(self.size * 0.3)    # 5 for 16px
        check_start_y = int(self.size * 0.5)    # 8 for 16px
        check_mid_x = int(self.size * 0.45)     # 7 for 16px
        check_mid_y = int(self.size * 0.65)     # 10 for 16px
        check_end_x = int(self.size * 0.7)      # 11 for 16px
        check_end_y = int(self.size * 0.35)     # 6 for 16px
        
        painter.drawLine(check_start_x, check_start_y, check_mid_x, check_mid_y)
        painter.drawLine(check_mid_x, check_mid_y, check_end_x, check_end_y)
        
        painter.end()
        return pixmap
    
    def save_all_variations(self):
        """Generate and save all checkbox variations."""
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate all four variations
        variations = [
            ("checkbox_unchecked.png", False, False),         # Light unchecked
            ("checkbox_checked.png", False, True),            # Light checked
            ("checkbox_unchecked_dark.png", True, False),     # Dark unchecked
            ("checkbox_checked_dark.png", True, True),        # Dark checked
        ]
        
        created_files = []
        
        for filename, dark_theme, checked in variations:
            if checked:
                pixmap = self.create_checked_checkbox(dark_theme)
            else:
                pixmap = self.create_unchecked_checkbox(dark_theme)
            
            filepath = os.path.join(self.output_dir, filename)
            pixmap.save(filepath)
            created_files.append(filepath)
            print(f"Created: {filepath}")
        
        return created_files

def main():
    """Main function to generate checkbox images."""
    app = QtWidgets.QApplication(sys.argv)
    
    generator = CheckboxGenerator()
    
    print("Checkbox Image Generator")
    print("=" * 30)
    print(f"Size: {generator.size}x{generator.size} pixels")
    print(f"Border width: {generator.border_width}px")
    print(f"Border radius: {generator.border_radius}px")
    print(f"Output directory: {generator.output_dir}")
    print()
    
    created_files = generator.save_all_variations()
    
    print()
    print("All checkbox images created successfully!")
    print(f"Files created: {len(created_files)}")
    
    # Tips for customization
    print()
    print("Customization Tips:")
    print("- Modify colors in CheckboxGenerator.__init__()")
    print("- Change size, border_width, or border_radius")
    print("- Adjust checkmark coordinates in create_checked_checkbox()")
    print("- Try different QtGui.QBrush patterns for backgrounds")
    print("- Use QtGui.QGradient for gradient effects")

if __name__ == "__main__":
    main()
