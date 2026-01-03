"""
Screenshot-based testing helper for UI verification.

This module provides a ScreenshotTester class that can launch the application
in test mode, capture screenshots, and verify UI rendering for i18n and a11y.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui.utils.screenshot_helper import (
    capture_window_screenshot,
    get_text_color_contrast
)


logger = logging.getLogger(__name__)


class ScreenshotTester:
    """Helper class for screenshot-based UI testing."""

    def __init__(self):
        """Initialize the screenshot tester."""
        self.app = None
        self.main_window = None
        self.screenshots = []
        self.auto_close_timer = None

    def launch_and_capture(self, test_files: Optional[List[str]] = None) -> str:
        """
        Launch the application in test mode and capture a screenshot.

        Args:
            test_files: Optional list of test files to load

        Returns:
            str: Path to the captured screenshot
        """
        try:
            # Create QApplication if it doesn't exist
            self.app = QtWidgets.QApplication.instance()
            if self.app is None:
                self.app = QtWidgets.QApplication(sys.argv)

            # Import and create main window
            from aicodeprep_gui.gui.main_window import FileSelectionGUI

            # Use test files or empty list
            files = test_files or []
            self.main_window = FileSelectionGUI(files)

            # Show and process events to ensure rendering
            self.main_window.show()
            QtWidgets.QApplication.processEvents()

            # Give window time to fully render
            QtCore.QTimer.singleShot(100, lambda: None)
            QtWidgets.QApplication.processEvents()

            # Set up auto-close timer if enabled
            if os.environ.get('AICODEPREP_AUTO_CLOSE') == '1':
                logger.info("Auto-close enabled: window will close in 10 seconds")
                self.auto_close_timer = QtCore.QTimer()
                self.auto_close_timer.timeout.connect(self._auto_close)
                self.auto_close_timer.setSingleShot(True)
                self.auto_close_timer.start(10000)  # 10 seconds

            # Capture screenshot
            screenshot_path = capture_window_screenshot(
                self.main_window,
                filename_prefix="test_main_window"
            )

            self.screenshots.append(screenshot_path)
            logger.info(f"Test screenshot captured: {screenshot_path}")

            return screenshot_path

        except Exception as e:
            logger.error(f"Error launching and capturing: {e}")
            raise

    def verify_text_rendering(self, expected_texts: List[str]) -> bool:
        """
        Verify that expected text strings are rendered in the UI.

        This is useful for testing translations.

        Args:
            expected_texts: List of text strings to verify

        Returns:
            bool: True if all texts are found
        """
        if not self.main_window:
            raise RuntimeError(
                "Main window not launched. Call launch_and_capture first.")

        # Search through all widgets for text
        found_texts = set()

        def search_widget(widget):
            """Recursively search widget hierarchy for text."""
            # Check various text properties
            if hasattr(widget, 'text') and callable(widget.text):
                text = widget.text()
                if text:
                    found_texts.add(text)

            if hasattr(widget, 'windowTitle') and callable(widget.windowTitle):
                text = widget.windowTitle()
                if text:
                    found_texts.add(text)

            # Recurse to children
            for child in widget.findChildren(QtWidgets.QWidget):
                search_widget(child)

        search_widget(self.main_window)

        # Check if all expected texts were found
        missing_texts = []
        for expected in expected_texts:
            if expected not in found_texts:
                missing_texts.append(expected)

        if missing_texts:
            logger.warning(f"Missing expected texts: {missing_texts}")
            return False

        return True

    def check_contrast_ratios(self) -> dict:
        """
        Check color contrast ratios for WCAG compliance.

        Returns:
            dict: Contrast ratio information for all text widgets
        """
        if not self.main_window:
            raise RuntimeError(
                "Main window not launched. Call launch_and_capture first.")

        results = {
            "total_widgets": 0,
            "compliant_aa": 0,
            "non_compliant": 0,
            "details": []
        }

        # Find all widgets with text
        text_widgets = []
        text_widgets.extend(self.main_window.findChildren(QtWidgets.QLabel))
        text_widgets.extend(
            self.main_window.findChildren(QtWidgets.QPushButton))
        text_widgets.extend(self.main_window.findChildren(QtWidgets.QCheckBox))

        for widget in text_widgets:
            try:
                contrast_info = get_text_color_contrast(widget)
                results["total_widgets"] += 1

                if contrast_info["wcag_aa_normal"]:
                    results["compliant_aa"] += 1
                else:
                    results["non_compliant"] += 1
                    results["details"].append({
                        "widget_type": type(widget).__name__,
                        "contrast_ratio": contrast_info["contrast_ratio"],
                        "compliant": False
                    })
            except Exception as e:
                logger.warning(f"Could not check contrast for {widget}: {e}")

        return results

    def _auto_close(self):
        """Internal method to auto-close the window after timer expires."""
        logger.info("Auto-close timer expired, closing window...")
        self.cleanup()
        # Exit the application event loop if running
        if self.app:
            self.app.quit()

    def cleanup(self):
        """Clean up test resources."""
        # Stop auto-close timer if active
        if self.auto_close_timer:
            self.auto_close_timer.stop()
            self.auto_close_timer = None

        if self.main_window:
            try:
                # Force close without confirmation
                self.main_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                self.main_window.close()
                self.main_window.deleteLater()
            except Exception as e:
                logger.warning(f"Error closing main window: {e}")
            finally:
                self.main_window = None

        # Process events to ensure cleanup
        if self.app:
            QtWidgets.QApplication.processEvents()
            # Give time for cleanup
            QtCore.QTimer.singleShot(100, lambda: None)
            QtWidgets.QApplication.processEvents()
