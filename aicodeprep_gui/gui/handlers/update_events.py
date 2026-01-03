import json
import logging
import os
from datetime import datetime
from PySide6 import QtCore
from aicodeprep_gui import update_checker


class UpdateCheckWorker(QtCore.QObject):
    """A worker that runs in a separate thread to check for updates without blocking the GUI."""
    finished = QtCore.Signal(
        str)  # Emits message string or empty string if no update

    def run(self):
        """Fetches update info and emits the result."""
        # Skip update checks in test mode
        if os.environ.get('AICODEPREP_TEST_MODE') == '1' or os.environ.get('AICODEPREP_NO_UPDATES') == '1':
            logging.debug("Test mode: skipping update check")
            self.finished.emit("")
            return

        message = update_checker.get_update_info()
        self.finished.emit(message or "")
