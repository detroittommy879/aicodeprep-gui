"""
Pytest configuration for aicodeprep-gui tests.

Handles QApplication lifecycle and cleanup for Qt-based tests.
"""
from PySide6 import QtWidgets
import pytest
import os
import sys

# Enable test mode before any imports
os.environ['AICODEPREP_TEST_MODE'] = '1'
os.environ['AICODEPREP_NO_METRICS'] = '1'
os.environ['AICODEPREP_NO_UPDATES'] = '1'


@pytest.fixture(scope="session")
def qapp_session():
    """
    Session-wide QApplication fixture.

    Creates a single QApplication instance for all tests in the session.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # Configure app for testing
    app.setQuitOnLastWindowClosed(False)

    yield app

    # Cleanup at end of session
    try:
        # Close all windows. Avoid deleteLater() here; PySide can crash the
        # interpreter on Windows if Python references outlive the C++ object.
        for widget in app.topLevelWidgets():
            widget.close()

        # Process events
        app.processEvents()
    except Exception:
        pass


@pytest.fixture(scope="function", autouse=True)
def qapp_cleanup(qapp_session):
    """
    Automatic cleanup after each test function.

    Ensures all windows are closed and events processed between tests.
    """
    yield

    # Cleanup after test
    try:
        # Close any remaining windows without forcibly deleting Qt objects.
        for widget in qapp_session.topLevelWidgets():
            if widget.isVisible():
                widget.close()

        # Do not force processEvents() here; some PySide builds crash during
        # teardown while worker threads are still unwinding.
    except Exception:
        pass


def pytest_configure(config):
    """Configure pytest for Qt testing."""
    # Disable Qt warnings during tests
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
