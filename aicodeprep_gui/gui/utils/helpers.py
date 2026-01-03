import os
import sys
import platform
import ctypes
import logging
from datetime import datetime, date
from PySide6 import QtWidgets, QtCore, QtGui, QtNetwork
from importlib import resources


class WindowHelpers:
    def __init__(self, main_window):
        self.main_window = main_window

    def open_settings_folder(self):
        folder_path = os.getcwd()
        if sys.platform.startswith("win"):
            os.startfile(folder_path)
        elif sys.platform.startswith("darwin"):
            import subprocess
            subprocess.Popen(["open", folder_path])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", folder_path])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].isLocalFile() and os.path.isdir(event.mimeData().urls()[0].toLocalFile()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        folder_path = event.mimeData().urls()[0].toLocalFile()
        os.chdir(folder_path)
        from aicodeprep_gui.smart_logic import collect_all_files
        self.main_window.new_gui = self.main_window.__class__(
            collect_all_files())
        self.main_window.new_gui.show()
        self.main_window.close()

    def showEvent(self, event):
        super(self.main_window.__class__, self.main_window).showEvent(event)
        if getattr(self.main_window, "initial_show_event", False):
            QtCore.QTimer.singleShot(0, self.main_window._start_update_check)
            self.main_window.initial_show_event = False

    def closeEvent(self, event):
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "UserIdentity")
            has_voted = settings.value(
                "has_voted_on_features_v2", False, type=bool)
            if getattr(self.main_window, "app_open_count", 0) >= 5 and not has_voted:
                from aicodeprep_gui.gui.components.dialogs import VoteDialog
                dlg = VoteDialog(self.main_window.user_uuid,
                                 self.main_window.network_manager, parent=self.main_window)
                dlg.exec()
                settings.setValue("has_voted_on_features_v2", True)
        except Exception as e:
            logging.error(f"Error showing VoteDialog: {e}")

        try:
            if self.main_window.update_thread and self.main_window.update_thread.isRunning():
                print("[gui] Stopping update check thread before closing...")
                self.main_window.update_thread.quit()
                if not self.main_window.update_thread.wait(3000):
                    print("[gui] Force terminating update check thread...")
                    self.main_window.update_thread.terminate()
                    self.main_window.update_thread.wait()
        except RuntimeError:
            print("[gui] Update thread already cleaned up by Qt")

        if self.main_window.remember_checkbox and self.main_window.remember_checkbox.isChecked():
            self.main_window.save_prefs()
        if self.main_window.action != 'process':
            self.main_window.action = 'quit'
            self.main_window._send_metric_event("quit")
        super(self.main_window.__class__, self.main_window).closeEvent(event)
