"""
Screenshot utility module for AI-driven UI verification.

This module provides functions to capture screenshots of Qt windows and widgets
for automated testing and AI-assisted verification of internationalization and
accessibility features.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import QRect


logger = logging.getLogger(__name__)


def get_screenshot_directory() -> Path:
    """
    Get the directory where screenshots should be saved.

    Creates the directory if it doesn't exist.

    Returns:
        Path object pointing to the screenshot directory
    """
    # Use project root / screenshots directory
    project_root = Path(__file__).parent.parent.parent
    screenshot_dir = project_root / "screenshots" / "test_captures"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    return screenshot_dir


def capture_window_screenshot(window: QtWidgets.QWidget,
                              filename_prefix: str = "window") -> str:
    """
    Capture a screenshot of a Qt window.

    Args:
        window: The QWidget/QMainWindow to capture
        filename_prefix: Prefix for the screenshot filename

    Returns:
        str: Path to the saved screenshot file

    Raises:
        RuntimeError: If screenshot capture fails
    """
    try:
        # Ensure window is visible and rendered
        window.show()
        QtWidgets.QApplication.processEvents()

        # Grab the window pixmap
        pixmap = window.grab()

        if pixmap.isNull():
            raise RuntimeError(
                "Failed to capture window screenshot - pixmap is null")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = get_screenshot_directory()
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = screenshot_dir / filename

        # Save the screenshot
        success = pixmap.save(str(filepath))

        if not success:
            raise RuntimeError(f"Failed to save screenshot to {filepath}")

        logger.info(f"Screenshot saved to: {filepath}")
        return str(filepath)

    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        raise


def capture_widget_screenshot(widget: QtWidgets.QWidget,
                              filename_prefix: str = "widget") -> str:
    """
    Capture a screenshot of a specific widget.

    Args:
        widget: The QWidget to capture
        filename_prefix: Prefix for the screenshot filename

    Returns:
        str: Path to the saved screenshot file
    """
    try:
        # Ensure widget is visible and rendered
        widget.show()
        QtWidgets.QApplication.processEvents()

        # Grab the widget pixmap
        pixmap = widget.grab()

        if pixmap.isNull():
            raise RuntimeError(
                "Failed to capture widget screenshot - pixmap is null")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = get_screenshot_directory()
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = screenshot_dir / filename

        # Save the screenshot
        success = pixmap.save(str(filepath))

        if not success:
            raise RuntimeError(f"Failed to save screenshot to {filepath}")

        logger.info(f"Widget screenshot saved to: {filepath}")
        return str(filepath)

    except Exception as e:
        logger.error(f"Error capturing widget screenshot: {e}")
        raise


def compare_screenshots(path1: str, path2: str) -> Dict[str, any]:
    """
    Compare two screenshots and return difference metrics.

    This is useful for detecting visual regressions when testing
    different languages or accessibility settings.

    Args:
        path1: Path to first screenshot
        path2: Path to second screenshot

    Returns:
        dict: Dictionary containing comparison metrics:
            - identical: bool - True if images are pixel-perfect identical
            - diff_percentage: float - Percentage of different pixels
            - dimensions_match: bool - True if images have same dimensions
    """
    try:
        image1 = QtGui.QImage(path1)
        image2 = QtGui.QImage(path2)

        if image1.isNull() or image2.isNull():
            raise RuntimeError(
                "Failed to load one or both images for comparison")

        # Check if dimensions match
        dimensions_match = (image1.size() == image2.size())

        if not dimensions_match:
            return {
                "identical": False,
                "diff_percentage": 100.0,
                "dimensions_match": False,
                "size1": (image1.width(), image1.height()),
                "size2": (image2.width(), image2.height())
            }

        # Compare pixels
        width = image1.width()
        height = image1.height()
        total_pixels = width * height
        different_pixels = 0

        for y in range(height):
            for x in range(width):
                if image1.pixel(x, y) != image2.pixel(x, y):
                    different_pixels += 1

        diff_percentage = (different_pixels / total_pixels) * 100
        identical = (different_pixels == 0)

        logger.info(f"Screenshot comparison: {diff_percentage:.2f}% different")

        return {
            "identical": identical,
            "diff_percentage": diff_percentage,
            "dimensions_match": True,
            "different_pixels": different_pixels,
            "total_pixels": total_pixels
        }

    except Exception as e:
        logger.error(f"Error comparing screenshots: {e}")
        raise


def get_text_color_contrast(widget: QtWidgets.QWidget) -> Dict[str, float]:
    """
    Calculate color contrast ratios for text in a widget.

    This helps verify WCAG AA compliance (4.5:1 for normal text, 3:1 for large).

    Args:
        widget: The widget to analyze

    Returns:
        dict: Dictionary with contrast ratio information
    """
    try:
        # Get widget's palette
        palette = widget.palette()

        # Get foreground and background colors
        fg_color = palette.color(QtGui.QPalette.WindowText)
        bg_color = palette.color(QtGui.QPalette.Window)

        # Calculate relative luminance
        def get_relative_luminance(color: QtGui.QColor) -> float:
            """Calculate relative luminance as per WCAG formula."""
            def adjust_channel(channel):
                channel = channel / 255.0
                if channel <= 0.03928:
                    return channel / 12.92
                else:
                    return ((channel + 0.055) / 1.055) ** 2.4

            r = adjust_channel(color.red())
            g = adjust_channel(color.green())
            b = adjust_channel(color.blue())

            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        # Calculate contrast ratio
        l1 = get_relative_luminance(fg_color)
        l2 = get_relative_luminance(bg_color)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        contrast_ratio = (lighter + 0.05) / (darker + 0.05)

        # Check WCAG compliance
        wcag_aa_normal = contrast_ratio >= 4.5
        wcag_aa_large = contrast_ratio >= 3.0
        wcag_aaa_normal = contrast_ratio >= 7.0

        return {
            "contrast_ratio": contrast_ratio,
            "wcag_aa_normal": wcag_aa_normal,
            "wcag_aa_large": wcag_aa_large,
            "wcag_aaa_normal": wcag_aaa_normal,
            "foreground_color": fg_color.name(),
            "background_color": bg_color.name()
        }

    except Exception as e:
        logger.error(f"Error calculating contrast ratio: {e}")
        raise
