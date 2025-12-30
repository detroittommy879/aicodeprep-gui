import logging
import os
from PySide6 import QtCore, QtWidgets
from aicodeprep_gui.apptheme import (
    system_pref_is_dark, apply_dark_palette, apply_light_palette,
    get_checkbox_style_dark, get_checkbox_style_light
)


class UISettingsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _load_dark_mode_setting(self) -> bool:
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "Appearance")
            if settings.contains("dark_mode"):
                return settings.value("dark_mode", type=bool)
            else:
                dark = system_pref_is_dark()
                settings.setValue("dark_mode", dark)
                return dark
        except Exception as e:
            logging.error(f"Failed to load dark mode setting: {e}")
            return system_pref_is_dark()

    def _save_dark_mode_setting(self):
        try:
            settings = QtCore.QSettings("aicodeprep-gui", "Appearance")
            settings.setValue("dark_mode", self.main_window.is_dark_mode)
        except Exception as e:
            logging.error(f"Failed to save dark mode setting: {e}")

    def toggle_dark_mode(self, state):
        self.main_window.is_dark_mode = bool(state)
        if self.main_window.is_dark_mode:
            apply_dark_palette(self.main_window.app)
        else:
            apply_light_palette(self.main_window.app)

        # Best Practice for Your App (aicodeprep GUI)
        # UI font stack for multilingual users
        font_stack = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", "Noto Sans Arabic", Arial, sans-serif'
        self.main_window.setStyleSheet(f"font-family: {font_stack};")

        base_style = """
            QTreeView, QTreeWidget {
                outline: 2; /* Remove focus rectangle */
            }
        """
        checkbox_style = get_checkbox_style_dark(
        ) if self.main_window.is_dark_mode else get_checkbox_style_light()
        self.main_window.tree_widget.setStyleSheet(base_style + checkbox_style)

        # Set vibe_label style based on theme
        if self.main_window.is_dark_mode:
            self.main_window.vibe_label.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #353535, stop:0.33 #90ee90, stop:0.67 #ffa500, stop:1 #353535); "
                "color: #ffffff; padding: 0px 0px 0px 0px; border-radius: 8px;"
            )
        else:
            self.main_window.vibe_label.setStyleSheet(
                "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f8f900, stop:0.33 #20c020, stop:0.67 #ff8c00, stop:1 #f8f900); "
                "color: #000000; padding: 0px 0px 0px 0px; border-radius: 8px;"
            )
        for child in self.main_window.findChildren(QtWidgets.QLabel):
            if getattr(child, "objectName", lambda: "")() == "preset_explanation":
                child.setStyleSheet(
                    f"font-size: {10 + self.main_window.font_size_multiplier}px; color: {'#bbbbbb' if self.main_window.is_dark_mode else '#444444'};"
                )
        if self.main_window.text_label.text():
            self.main_window.text_label.setStyleSheet(
                f"font-size: {20 + self.main_window.font_size_multiplier}px; color: {'#00c3ff' if self.main_window.is_dark_mode else '#0078d4'}; font-weight: bold;"
            )

        self.main_window._update_groupbox_style(
            self.main_window.options_group_box)
        self.main_window._update_groupbox_style(
            self.main_window.premium_group_box)
        # Reapply gradient to central widget after theme change
        self.main_window.apply_gradient_to_central()

        self._save_dark_mode_setting()

        # Removed preview window refresh logic

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

        # Collect pro features state
        pro_features = {}
        if hasattr(self.main_window, 'preview_toggle'):
            pro_features['preview_window_enabled'] = self.main_window.preview_toggle.isChecked(
            )

        from .preferences import _write_prefs_file
        _write_prefs_file(checked_relpaths, window_size=(size.width(), size.height(
        )), splitter_state=splitter_state, output_format=fmt, pro_features=pro_features)
