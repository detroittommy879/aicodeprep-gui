"""Utility modules for aicodeprep-gui."""
from .screenshot_helper import (
    capture_window_screenshot,
    capture_widget_screenshot,
    compare_screenshots,
    get_screenshot_directory,
    get_text_color_contrast
)

__all__ = [
    'capture_window_screenshot',
    'capture_widget_screenshot',
    'compare_screenshots',
    'get_screenshot_directory',
    'get_text_color_contrast'
]
