import json
import logging
from datetime import datetime
from PySide6 import QtCore
from aicodeprep_gui import update_checker

class UpdateCheckWorker(QtCore.QObject):
    """A worker that runs in a separate thread to check for updates without blocking the GUI."""
    finished = QtCore.Signal(str)  # Emits message string or empty string if no update

    def run(self):
        """Fetches update info and emits the result."""
        message = update_checker.get_update_info()
        self.finished.emit(message or "")
