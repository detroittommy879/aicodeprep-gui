import logging
from PySide6 import QtWidgets, QtCore
from aicodeprep_gui.gui.settings.presets import global_preset_manager

class PresetButtonManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _load_global_presets(self):
        try:
            presets = global_preset_manager.get_all_presets()
            for label, text in presets:
                self._add_preset_button(label, text, from_global=True)
        except Exception as e: 
            logging.error(f"Failed to load global presets: {e}")

    def _add_preset_button(self, label, text, from_local=False, from_global=False):
        btn = QtWidgets.QPushButton(label)
        btn.setFixedHeight(22)
        btn.clicked.connect(lambda _=None, t=text: self._apply_preset(t))
        if from_global:
            btn.setToolTip(f"Global preset: {label}")
        else:
            btn.setToolTip(f"Preset: {label}")
        insert_index = self.main_window.preset_strip.count() - 1 
        self.main_window.preset_strip.insertWidget(insert_index, btn)

    def _delete_preset(self, label, button, from_global):
        reply = QtWidgets.QMessageBox.question(self.main_window, "Delete Preset", f"Are you sure you want to delete the preset '{label}'?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if from_global:
                if not global_preset_manager.delete_preset(label): 
                    QtWidgets.QMessageBox.warning(self.main_window, "Error", f"Failed to delete global preset '{label}'")
                    return
            else: 
                self.main_window.presets = [(l, t) for l, t in self.main_window.presets if l != label]
            self.main_window.preset_strip.removeWidget(button)
            button.deleteLater()
            logging.info(f"Deleted preset: {label}")

    def _apply_preset(self, preset_text):
        current = self.main_window.prompt_textbox.toPlainText()
        self.main_window.prompt_textbox.setPlainText((current.rstrip() + "\n\n" if current else "") + preset_text)
