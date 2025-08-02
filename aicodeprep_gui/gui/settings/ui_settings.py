import logging
import os
from PySide6 import QtCore, QtWidgets
# Removed unused imports: system_pref_is_dark, apply_dark_palette, apply_light_palette
# Removed unused imports: get_checkbox_style_dark, get_checkbox_style_light


class UISettingsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _load_panel_visibility(self):
        settings = QtCore.QSettings("aicodeprep-gui", "PanelVisibility")
        options_visible = settings.value("options_visible", True, type=bool)
        premium_visible = settings.value("premium_visible", False, type=bool)
        self.main_window.options_group_box.setChecked(options_visible)
        self.main_window.premium_group_box.setChecked(premium_visible)

    def _save_panel_visibility(self):
        settings = QtCore.QSettings("aicodeprep-gui", "PanelVisibility")
        settings.setValue("options_visible",
                          self.main_window.options_group_box.isChecked())
        settings.setValue("premium_visible",
                          self.main_window.premium_group_box.isChecked())

    def _load_prompt_options(self):
        settings = QtCore.QSettings("aicodeprep-gui", "PromptOptions")
        self.main_window.prompt_top_checkbox.setChecked(
            settings.value("prompt_to_top", True, type=bool))
        self.main_window.prompt_bottom_checkbox.setChecked(
            settings.value("prompt_to_bottom", True, type=bool))

    def _save_prompt_options(self):
        settings = QtCore.QSettings("aicodeprep-gui", "PromptOptions")
        settings.setValue(
            "prompt_to_top", self.main_window.prompt_top_checkbox.isChecked())
        settings.setValue("prompt_to_bottom",
                          self.main_window.prompt_bottom_checkbox.isChecked())

    def _save_format_choice(self, idx):
        fmt = self.main_window.format_combo.currentData()
        checked_relpaths = []
        for rel_path, item in self.main_window.path_to_item.items():
            if item.checkState(0) == QtCore.Qt.Checked:
                file_path_abs = item.data(0, QtCore.Qt.UserRole)
                if file_path_abs and os.path.isfile(file_path_abs):
                    checked_relpaths.append(rel_path)
        size = self.main_window.size()
        splitter_state = self.main_window.splitter.saveState()
        from .preferences import _write_prefs_file
        _write_prefs_file(checked_relpaths, window_size=(
            size.width(), size.height()), splitter_state=splitter_state, output_format=fmt)
