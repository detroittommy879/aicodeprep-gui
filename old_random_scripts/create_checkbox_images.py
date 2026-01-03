#!/usr/bin/env python3
"""
Script to create permanent checkbox image files
"""

import sys
import os
from PySide6 import QtWidgets, QtGui, QtCore

def create_permanent_checkbox_images():
    """Create permanent checkbox image files in the project directory."""
    app = QtWidgets.QApplication(sys.argv)
    
    # Create directory for images
    images_dir = os.path.join("auicp", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Create unchecked checkbox (just border)
    unchecked_pixmap = QtGui.QPixmap(16, 16)
    unchecked_pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(unchecked_pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    # Draw border
    pen = QtGui.QPen(QtGui.QColor("#aaaaaa"))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
    painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
    painter.end()
    
    unchecked_path = os.path.join(images_dir, "checkbox_unchecked.png")
    unchecked_pixmap.save(unchecked_path)
    print(f"Created: {unchecked_path}")
    
    # Create checked checkbox (border + checkmark)
    checked_pixmap = QtGui.QPixmap(16, 16)
    checked_pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(checked_pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    # Draw border and background
    pen = QtGui.QPen(QtGui.QColor("#0078D4"))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(QtGui.QColor("#ffffff")))
    painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
    
    # Draw checkmark
    pen = QtGui.QPen(QtGui.QColor("#0078D4"))
    pen.setWidth(2)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(5, 8, 7, 10)
    painter.drawLine(7, 10, 11, 6)
    painter.end()
    
    checked_path = os.path.join(images_dir, "checkbox_checked.png")
    checked_pixmap.save(checked_path)
    print(f"Created: {checked_path}")
    
    # Create dark theme versions
    # Dark unchecked
    dark_unchecked_pixmap = QtGui.QPixmap(16, 16)
    dark_unchecked_pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(dark_unchecked_pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    pen = QtGui.QPen(QtGui.QColor("#aaaaaa"))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(QtGui.QColor("#2b2b2b")))
    painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
    painter.end()
    
    dark_unchecked_path = os.path.join(images_dir, "checkbox_unchecked_dark.png")
    dark_unchecked_pixmap.save(dark_unchecked_path)
    print(f"Created: {dark_unchecked_path}")
    
    # Dark checked
    dark_checked_pixmap = QtGui.QPixmap(16, 16)
    dark_checked_pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(dark_checked_pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    
    pen = QtGui.QPen(QtGui.QColor("#0078D4"))
    pen.setWidth(2)
    painter.setPen(pen)
    painter.setBrush(QtGui.QBrush(QtGui.QColor("#2b2b2b")))
    painter.drawRoundedRect(2, 2, 12, 12, 2, 2)
    
    pen = QtGui.QPen(QtGui.QColor("#0078D4"))
    pen.setWidth(2)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(5, 8, 7, 10)
    painter.drawLine(7, 10, 11, 6)
    painter.end()
    
    dark_checked_path = os.path.join(images_dir, "checkbox_checked_dark.png")
    dark_checked_pixmap.save(dark_checked_path)
    print(f"Created: {dark_checked_path}")
    
    return unchecked_path, checked_path, dark_unchecked_path, dark_checked_path

if __name__ == "__main__":
    paths = create_permanent_checkbox_images()
    print("\nAll checkbox images created successfully!")
    print("Light theme files:", paths[:2])
    print("Dark theme files:", paths[2:])
