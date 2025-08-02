# In aicodeprep_gui/gui/theming.py

import os
import json
import logging
import zipfile
import shutil
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply
from importlib import resources

# Placeholder for pro.enabled, should be imported or passed appropriately
# For now, we'll assume it's available globally or via the app instance.
# This will need to be properly integrated later.
try:
    from aicodeprep_gui import pro
except ImportError:
    # Fallback if pro module is not available (e.g., during initial development or non-pro builds)
    class ProMock:
        enabled = False
    pro = ProMock()


class ThemeManager(QtCore.QObject):
    # Emits the generated stylesheet and theme data
    theme_changed = QtCore.Signal(str, dict)

    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()
        self.app = app
        self.themes = {}  # Stores theme data: {theme_name: theme_data}
        self.active_theme_name = "Light"  # Default theme
        self.loaded_fonts = {}  # Cache for loaded font IDs: {font_family_key: font_id}

        # Use QStandardPaths for a robust, cross-platform cache location
        self.font_cache_dir = os.path.join(
            QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.CacheLocation),
            "aicodeprep-gui",
            "fonts"
        )
        os.makedirs(self.font_cache_dir, exist_ok=True)

        self.network_manager = QtNetwork.QNetworkAccessManager(self)
        self.network_manager.finished.connect(self._font_download_finished)

        # User-specific theme directory
        self.user_theme_dir = os.path.join(
            QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.ConfigLocation),
            "aicodeprep-gui",
            "themes"
        )
        os.makedirs(self.user_theme_dir, exist_ok=True)

        self.settings = QtCore.QSettings("AICodePrepGUI", "AppSettings")
        self._discover_themes()
        initial_theme_name = self.get_initial_theme_to_apply()
        QtCore.QTimer.singleShot(
            0, lambda: self.apply_theme(initial_theme_name))

    def _discover_themes(self):
        """Discovers all available themes from packaged and user directories."""
        self.themes.clear()
        logging.info("Discovering themes...")

        # 1. Discover packaged themes using importlib.resources
        try:
            packaged_theme_files = resources.files(
                'aicodeprep_gui.themes').iterdir()
            for item in packaged_theme_files:
                if item.is_file() and item.name.endswith('.json'):
                    try:
                        with resources.as_file(item) as path:
                            theme_data = self._load_theme_from_file(str(path))
                            if theme_data:
                                theme_name = theme_data.get(
                                    "meta", {}).get("name", item.name[:-5])
                                self.themes[theme_name] = theme_data
                                logging.info(
                                    f"Loaded packaged theme: {theme_name}")
                    except Exception as e:
                        logging.error(
                            f"Failed to load packaged theme {item.name}: {e}")
        except Exception as e:
            logging.error(f"Could not access packaged themes: {e}")

        # 2. Discover user themes from user-specific directory
        try:
            for filename in os.listdir(self.user_theme_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.user_theme_dir, filename)
                    theme_data = self._load_theme_from_file(filepath)
                    if theme_data:
                        theme_name = theme_data.get(
                            "meta", {}).get("name", filename[:-5])
                        # User themes can override packaged ones if names clash
                        self.themes[theme_name] = theme_data
                        logging.info(f"Loaded user theme: {theme_name}")
        except Exception as e:
            logging.error(f"Could not access user themes directory: {e}")

        if not self.themes:
            logging.warning(
                "No themes were discovered. Application might not render correctly.")
            # Fallback to a very basic internal theme if no JSON themes are found
            self.themes["Default Light"] = self._get_fallback_light_theme()
            self.themes["Default Dark"] = self._get_fallback_dark_theme()

        # Ensure the active theme is still available, otherwise reset to default
        if self.active_theme_name not in self.themes:
            self.active_theme_name = "Light"  # Or "Dark", or first available
            if self.active_theme_name not in self.themes and self.themes:
                self.active_theme_name = next(iter(self.themes))

    def _load_theme_from_file(self, filepath: str) -> dict | None:
        """Loads and validates a theme from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)

            # Basic validation
            if not isinstance(theme_data, dict) or \
               "meta" not in theme_data or \
               "name" not in theme_data["meta"] or \
               "colors" not in theme_data:
                logging.error(f"Invalid theme structure in {filepath}")
                return None

            # Ensure all required color keys are present, fill with defaults if not
            default_colors = {
                "window_bg": "#F0F0F0", "base_bg": "#FFFFFF", "alternate_base_bg": "#E9E9E9",
                "text_color": "#000000", "disabled_text_color": "#808080", "highlight_bg": "#2A82DA",
                "highlight_text": "#FFFFFF", "link_color": "#0000FF", "button_bg": "#F0F0F0",
                "button_text": "#000000", "border_color": "#CCCCCC", "accent_color_1": "#2A82DA",
                "accent_color_2": "#0078D4", "accent_color_3": "#6A3EA1", "error_color": "#FF5555"
            }
            theme_colors = theme_data.get("colors", {})
            for key, value in default_colors.items():
                if key not in theme_colors:
                    theme_colors[key] = value
                    logging.warning(
                        f"Color '{key}' missing in {filepath}, using default: {value}")
            theme_data["colors"] = theme_colors

            if "fonts" not in theme_data:
                theme_data["fonts"] = {"primary": {
                    "family": "Segoe UI", "source": "system", "size_modifier": 0}}
            if "qss_overrides" not in theme_data:
                theme_data["qss_overrides"] = {}

            return theme_data
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in theme file {filepath}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading theme file {filepath}: {e}")
            return None

    def _get_fallback_light_theme(self) -> dict:
        # Basic light theme structure
        return {
            "meta": {"name": "Default Light", "version": "1.0", "author": "System", "pro": False},
            "fonts": {"primary": {"family": "Segoe UI", "source": "system", "size_modifier": 0}},
            "colors": {
                "window_bg": "#F0F0F0", "base_bg": "#FFFFFF", "alternate_base_bg": "#E9E9E9",
                "text_color": "#000000", "disabled_text_color": "#808080", "highlight_bg": "#2A82DA",
                "highlight_text": "#FFFFFF", "link_color": "#0000FF", "button_bg": "#F0F0F0",
                "button_text": "#000000", "border_color": "#CCCCCC", "accent_color_1": "#2A82DA",
                "accent_color_2": "#0078D4", "accent_color_3": "#6A3EA1", "error_color": "#FF5555"
            },
            "qss_overrides": {}
        }

    def _get_fallback_dark_theme(self) -> dict:
        # Basic dark theme structure
        return {
            "meta": {"name": "Default Dark", "version": "1.0", "author": "System", "pro": False},
            "fonts": {"primary": {"family": "Segoe UI", "source": "system", "size_modifier": 0}},
            "colors": {
                "window_bg": "#353535", "base_bg": "#2A2A2A", "alternate_base_bg": "#424242",
                "text_color": "#FFFFFF", "disabled_text_color": "#808080", "highlight_bg": "#2A82DA",
                "highlight_text": "#FFFFFF", "link_color": "#2A82DA", "button_bg": "#353535",
                "button_text": "#FFFFFF", "border_color": "#555555", "accent_color_1": "#2A82DA",
                "accent_color_2": "#BD93F9", "accent_color_3": "#50FA7B", "error_color": "#FF5555"
            },
            "qss_overrides": {}
        }

    def get_available_themes(self) -> list[tuple[str, bool]]:
        """Returns a list of (theme_name, is_pro) tuples."""
        available = []
        for name, data in self.themes.items():
            is_pro_theme = data.get("meta", {}).get("pro", False)
            available.append((name, is_pro_theme))
        return sorted(available)  # Sort alphabetically by name

    def apply_theme(self, theme_name: str):
        if theme_name not in self.themes:
            logging.error(f"Theme '{theme_name}' not found.")
            return

        theme_data = self.themes[theme_name]
        is_pro_theme = theme_data.get("meta", {}).get("pro", False)

        if is_pro_theme and not pro.enabled:
            logging.warning(
                f"Theme '{theme_name}' is a Pro theme. Pro mode is not enabled.")
            # Optionally, revert to a default theme or notify the user via UI
            # For now, we just log and don't apply.
            # self.apply_theme(self.active_theme_name) # Revert to previous
            return

        logging.info(f"Applying theme: {theme_name}")
        self.active_theme_name = theme_name
        self.settings.setValue("activeThemeName", self.active_theme_name)

        # Load fonts specified in the theme
        self._load_fonts(theme_data.get("fonts", {}))

        # Generate and apply the stylesheet
        stylesheet = self._generate_stylesheet(theme_data)
        self.app.setStyleSheet(stylesheet)

        # Emit the new stylesheet and theme data
        self.theme_changed.emit(stylesheet, theme_data)
        logging.info(f"Theme '{theme_name}' applied successfully.")

    def _load_fonts(self, font_config: dict):
        """
        Loads fonts specified in the theme configuration.
        Supports 'system' and 'google' sources.
        """
        for font_role, font_details in font_config.items():
            family = font_details.get("family")
            source = font_details.get("source")
            # size_modifier = font_details.get("size_modifier", 0) # For future use

            if source == "google":
                logging.info(
                    f"Skipping web font download for '{family}' (Google Fonts temporarily disabled).")
                continue

            if not family or not source:
                continue

            font_key = f"{family}_{source}"  # Unique key for caching

            if font_key in self.loaded_fonts:
                # Font already loaded or attempted
                if self.loaded_fonts[font_key] == -1:
                    logging.warning(
                        f"Font {family} (source: {source}) previously failed to load. Skipping.")
                continue

            # Mark as loading/failed by default
            self.loaded_fonts[font_key] = -1

            if source == "system":
                # System fonts don't need explicit loading, Qt handles them.
                # We just need to ensure the family name is correct for QSS.
                # Mark as "handled" (not loaded by ID, but available)
                self.loaded_fonts[font_key] = 0
                logging.info(f"Using system font: {family}")

            elif source == "google":
                # (Google font logic is currently disabled)
                pass

            else:
                logging.warning(
                    f"Unknown font source '{source}' for font '{family}'.")

    def _download_google_font(self, font_name: str, destination_path: str) -> bool:
        """
        Download a Google Font to the specified path.
        Handles CSS parsing, font URL extraction, and binary file download.
        """
        # (Google font logic is currently disabled)
        return False

    def _font_download_finished(self, reply: QNetworkReply):
        """Handles the completion of a font file download."""
        reply.deleteLater()

    def _generate_stylesheet(self, theme_data: dict) -> str:
        """
        Generates the QSS for general theming.
        NOTE: Checkbox indicator styling has been REMOVED from here
        and is now handled directly in the main window.
        """
        colors = theme_data.get("colors", {})
        fonts = theme_data.get("fonts", {})
        qss_overrides = theme_data.get("qss_overrides", {})

        base_qss = f"""
        QWidget {{
            background-color: {colors.get('window_bg')};
            color: {colors.get('text_color')};
            font-family: {fonts.get('primary', {}).get('family', 'Segoe UI')};
        }}

        /* --- Main Window and Dialogs --- */
        QMainWindow, QDialog {{
            background-color: {colors.get('window_bg')};
        }}

        /* --- Menus --- */
        QMenuBar {{
            background-color: {colors.get('window_bg')};
            color: {colors.get('text_color')};
        }}
        QMenuBar::item:selected {{
            background-color: {colors.get('highlight_bg')};
            color: {colors.get('highlight_text')};
        }}
        QMenu {{
            background-color: {colors.get('base_bg')};
            color: {colors.get('text_color')};
            border: 1px solid {colors.get('border_color')};
        }}
        QMenu::item:selected {{
            background-color: {colors.get('highlight_bg')};
            color: {colors.get('highlight_text')};
        }}
        QMenu::separator {{
            height: 1px;
            background: {colors.get('border_color')};
            margin: 4px 0px;
        }}

        /* --- Buttons --- */
        QPushButton {{
            background-color: {colors.get('button_bg')};
            color: {colors.get('button_text')};
            border: 1px solid {colors.get('border_color')};
            padding: 5px 10px;
            border-radius: 3px;
        }}
        QPushButton:hover {{
            background-color: {colors.get('accent_color_1')};
            color: {colors.get('highlight_text')};
            border-color: {colors.get('accent_color_1')};
        }}
        QPushButton:pressed {{
            background-color: {colors.get('accent_color_2')};
        }}
        QPushButton:disabled {{
            background-color: {colors.get('alternate_base_bg')};
            color: {colors.get('disabled_text_color')};
            border-color: {colors.get('border_color')};
        }}

        /* --- Inputs and Combos --- */
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox, QDateEdit {{
            background-color: {colors.get('base_bg')};
            color: {colors.get('text_color')};
            border: 1px solid {colors.get('border_color')};
            padding: 4px;
            border-radius: 3px;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
             border: 1px solid {colors.get('accent_color_1')};
        }}
        QComboBox QAbstractItemView {{
            background-color: {colors.get('base_bg')};
            color: {colors.get('text_color')};
            selection-background-color: {colors.get('highlight_bg')};
            selection-color: {colors.get('highlight_text')};
            border: 1px solid {colors.get('border_color')};
        }}


        /* --- Other Widgets --- */
        QSplitter::handle {{ background-color: {colors.get('border_color')}; }}
        QSplitter::handle:hover {{ background-color: {colors.get('accent_color_1')}; }}
        QSplitter::handle:vertical {{ height: 1px; }}
        QSplitter::handle:horizontal {{ width: 1px; }}

        QToolTip {{
            background-color: {colors.get('alternate_base_bg')};
            color: {colors.get('text_color')};
            border: 1px solid {colors.get('border_color')};
            padding: 4px;
        }}

        QScrollBar:vertical {{
            border: none;
            background: {colors.get('base_bg')};
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {colors.get('disabled_text_color')};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {colors.get('accent_color_1')};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

        QStatusBar {{
            background-color: {colors.get('window_bg')};
        }}
        """

        processed_overrides = []
        for selector, rule in qss_overrides.items():
            try:
                processed_rule = rule.format(**colors)
                processed_overrides.append(
                    f"{selector} {{ {processed_rule} }}")
            except KeyError as e:
                logging.warning(
                    f"Color key '{e}' not found for QSS override: {selector}")
            except Exception as e:
                logging.error(
                    f"Error processing QSS override for {selector}: {e}")

        final_stylesheet = base_qss + "\n" + "\n".join(processed_overrides)
        return final_stylesheet.strip()

    def add_custom_theme(self, json_string: str) -> tuple[bool, str]:
        """
        Validates and saves a user-submitted theme.
        """
        try:
            theme_data = json.loads(json_string)
        except json.JSONDecodeError:
            return False, "Invalid JSON format."

        # Validate structure
        if not isinstance(theme_data, dict) or \
           "meta" not in theme_data or \
           "name" not in theme_data["meta"] or \
           "colors" not in theme_data:
            return False, "Invalid theme structure. Missing 'meta.name' or 'colors'."

        theme_name = theme_data["meta"]["name"]
        if not theme_name:
            return False, "Theme name in 'meta.name' cannot be empty."

        # Sanitize theme_name for use as a filename
        safe_theme_name = "".join(c if c.isalnum() or c in (
            ' ', '.', '_') else '_' for c in theme_name).rstrip()
        filename = f"user_{safe_theme_name}.json"
        filepath = os.path.join(self.user_theme_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4)

            self._discover_themes()  # Refresh theme list
            return True, f"Theme '{theme_name}' saved successfully!"
        except Exception as e:
            logging.error(f"Failed to save custom theme '{theme_name}': {e}")
            return False, f"Error saving theme: {e}"

    def get_initial_theme_to_apply(self) -> str:
        """Determines the initial theme to apply based on settings or system preference."""
        from aicodeprep_gui.apptheme import system_pref_is_dark

        saved_theme = self.settings.value("activeThemeName", "Light")

        if saved_theme in self.themes:
            theme_data = self.themes[saved_theme]
            is_pro_theme = theme_data.get("meta", {}).get("pro", False)
            if is_pro_theme and not pro.enabled:
                logging.info(
                    f"Saved theme '{saved_theme}' is Pro, but Pro mode is off. Defaulting.")
                for name, data in self.themes.items():
                    if not data.get("meta", {}).get("pro", False):
                        return name
                return "Light"
            return saved_theme
        else:
            if system_pref_is_dark():
                if "Dark" in self.themes and not (self.themes["Dark"].get("meta", {}).get("pro", False) and not pro.enabled):
                    return "Dark"
            return "Light"
