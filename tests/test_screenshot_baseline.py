"""
Baseline screenshot tests for Phase 0.

These tests verify the screenshot system works before implementing i18n/a11y.
"""
import pytest
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore


@pytest.fixture(scope="function")
def qapp():
    """Fixture to ensure QApplication instance is available and cleaned up."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app
    # Process events to ensure cleanup
    QtWidgets.QApplication.processEvents()
    QtCore.QTimer.singleShot(0, lambda: None)
    QtWidgets.QApplication.processEvents()


class TestScreenshotBaseline:
    """Baseline tests for screenshot system functionality."""

    def test_capture_main_window(self):
        """Verify screenshot system works - should FAIL initially."""
        from aicodeprep_gui.utils.screenshot_helper import capture_window_screenshot
        from PySide6.QtWidgets import QApplication, QMainWindow

        app = QApplication.instance() or QApplication([])
        window = QMainWindow()
        window.setWindowTitle("Test Window")
        window.resize(800, 600)

        screenshot_path = capture_window_screenshot(window)

        assert screenshot_path is not None, "Screenshot path should not be None"
        assert os.path.exists(
            screenshot_path), f"Screenshot file should exist at {screenshot_path}"
        assert Path(screenshot_path).stat(
        ).st_size > 0, "Screenshot file should not be empty"

        # Cleanup
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

    def test_ui_renders_without_errors(self):
        """Baseline test - current UI should render without errors."""
        # This will test that we can launch the app in test mode
        from tests.test_helpers.screenshot_tester import ScreenshotTester

        tester = ScreenshotTester()
        try:
            screenshot_path = tester.launch_and_capture()

            assert screenshot_path is not None, "Should capture main window screenshot"
            assert os.path.exists(
                screenshot_path), "Screenshot file should exist"
        finally:
            # Always cleanup even if test fails
            tester.cleanup()
        from aicodeprep_gui.utils.screenshot_helper import get_screenshot_directory

        screenshot_dir = get_screenshot_directory()

        assert screenshot_dir is not None, "Screenshot directory path should be returned"
        # Directory might not exist yet, but path should be valid
        assert isinstance(screenshot_dir, (str, Path)
                          ), "Screenshot directory should be a path"
