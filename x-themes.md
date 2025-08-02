You are Cline, an expert Python and PySide6 engineer. Your task is to refactor the application's theming system from a hardcoded light/dark toggle into a flexible, data-driven architecture using JSON theme files. This will allow for adding new themes (both free and pro) and enable users to add their own custom themes.

### 📝 Core Concepts & Why We're Doing This

The current system in `apptheme.py` and `gui/settings/ui_settings.py` is rigid. By moving to a data-driven approach, we achieve several goals:

1.  **Extensibility**: We can add new themes simply by dropping a new `.json` file into a directory.
2.  **User Customization**: We can create a pro feature allowing users to paste their own theme JSON.
3.  **Clean Separation**: UI logic (`main_window.py`) will be decoupled from theme definitions. All theme logic will be centralized in a new `ThemeManager`.
4.  **Advanced Features**: The JSON format supports custom fonts (loaded at runtime from Google Fonts) and specific QSS overrides for fine-grained control.

The new data flow will be: **Theme JSON file -> `ThemeManager` -> Generated QSS Stylesheet -> Applied to App**.

---

### Phase 1: Create the Data Layer (Theme Files)

First, create the directory structure and the theme definition files.

1.  **Create a New Directory**: Create a new folder `aicodeprep_gui/themes/`. This will hold our packaged, default themes.
2.  **Define the Theme JSON Structure**: Create a new file, `aicodeprep_gui/themes/dracula-pro.json`, with the following content. This will serve as our template and a pro-gated example.

    ```json
    {
      "meta": {
        "name": "Dracula Pro",
        "version": "1.0",
        "author": "Zeno Rocha",
        "pro": true
      },
      "fonts": {
        "primary": {
          "family": "Fira Code",
          "source": "google",
          "size_modifier": 0
        }
      },
      "colors": {
        "window_bg": "#282a36",
        "base_bg": "#21222c",
        "alternate_base_bg": "#343746",
        "text_color": "#f8f8f2",
        "disabled_text_color": "#6272a4",
        "highlight_bg": "#44475a",
        "highlight_text": "#f8f8f2",
        "link_color": "#8be9fd",
        "button_bg": "#44475a",
        "button_text": "#f8f8f2",
        "border_color": "#191a21",
        "accent_color_1": "#50fa7b",
        "accent_color_2": "#ff79c6",
        "accent_color_3": "#bd93f9",
        "error_color": "#ff5555"
      },
      "qss_overrides": {
        "QGroupBox::title": "color: {{ accent_color_3 }};",
        "QPushButton:hover": "background-color: #6272a4;",
        "QTreeView::item:selected": "background-color: {{ highlight_bg }}; border: 1px solid {{ accent_color_1 }};",
        "FileSelectionGUI #vibe_label": "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4d324c, stop:1 #2d1d4c); color: #f8f8f2; padding: 0px; border-radius: 8px;"
      }
    }
    ```

3.  **Create Default Themes**: Now, create `aicodeprep_gui/themes/light.json` and `aicodeprep_gui/themes/dark.json`. Migrate the hardcoded colors from the `apply_light_palette` and `apply_dark_palette` functions in `aicodeprep_gui/apptheme.py` into these files, following the JSON structure above. Set `"pro": false` for both. For fonts, you can use system defaults (e.g., `"source": "system"` and `"family": "Segoe UI"`).

---

### Phase 2: Implement the `ThemeManager`

Create a new file `aicodeprep_gui/gui/theming.py`. This class will be the central controller for all theming logic.

```python
# In aicodeprep_gui/gui/theming.py

import os
import json
import logging
from PySide6 import QtCore, QtGui, QtWidgets
from importlib import resources

class ThemeManager(QtCore.QObject):
    theme_changed = QtCore.Signal(str) # Emits the generated stylesheet

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.themes = {}
        self.active_theme_name = "Light"
        # Use QStandardPaths for a robust, cross-platform cache location
        self.font_cache_dir = os.path.join(
            QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.CacheLocation),
            "aicodeprep-gui",
            "fonts"
        )
        os.makedirs(self.font_cache_dir, exist_ok=True)
        self.network_manager = QtNetwork.QNetworkAccessManager()
        self._discover_themes()

    def _discover_themes(self):
        # 1. Discover packaged themes using importlib.resources
        # 2. Discover user themes from a user-specific directory (e.g., ~/.config/aicodeprep-gui/themes)
        # 3. For each valid .json file, parse it and add it to self.themes dict, keyed by name.

    def get_available_themes(self) -> list[tuple[str, bool]]:
        """Returns a list of (theme_name, is_pro) tuples."""
        # This will be used to populate the UI combo box.

    def apply_theme(self, theme_name: str):
        # - Get theme data from self.themes.
        # - Call self._load_fonts().
        # - Call self._generate_stylesheet().
        # - Call self.app.setStyleSheet().
        # - Emit the theme_changed signal with the new stylesheet.

    def _load_fonts(self, font_config: dict):
        """
        For each font in the config:
        - If source is "google", construct the download URL.
        - Check if the font .ttf file is already in self.font_cache_dir.
        - If not, use self.network_manager to download the font zip, extract the TTF, and save it to the cache.
        - Use QtGui.QFontDatabase.addApplicationFont(font_path) to make it available to QSS.
        - Keep track of loaded fonts to avoid reloading.
        """

    def _generate_stylesheet(self, theme_data: dict) -> str:
        """
        This is the core of the styling.
        1.  Create a base QSS template string that styles the entire application using placeholders for colors (e.g., `QWidget { background-color: {window_bg}; color: {text_color}; }`).
        2.  Use `str.format(**theme_data['colors'])` to populate this base template.
        3.  Iterate through `theme_data['qss_overrides']`. For each override, replace any `{{ color_key }}` templates with the actual color value from `theme_data['colors']`.
        4.  Append all processed overrides to the main stylesheet string.
        5.  Return the final, complete QSS string.
        """

    def add_custom_theme(self, json_string: str) -> tuple[bool, str]:
        """
        Validates and saves a user-submitted theme.
        1.  Try `json.loads(json_string)`. Return (False, "Invalid JSON format.") on error.
        2.  Validate the structure. Check for required keys like `meta`, `name`, `colors`.
        3.  If valid, generate a filename (e.g., `user_my_custom_theme.json`) and save it to the user's theme directory.
        4.  Call `_discover_themes()` to refresh the list of available themes.
        5.  Return (True, "Theme saved successfully!").
        """
```

---

### Phase 3: Integrate `ThemeManager` into the UI

Modify `aicodeprep_gui/gui/main_window.py` and related settings files.

1.  **In `main_window.py`'s `__init__`**:

    - Instantiate the theme manager: `self.theme_manager = ThemeManager(self.app)`.
    - **Remove** the `self.dark_mode_box` `QCheckBox`.
    - In its place (e.g., in the "Options" group box), add a `QComboBox` called `self.theme_combo`.
    - Create a new menu, `view_menu = mb.addMenu("&View")`, and add a "Themes" submenu to it, populated with `QAction`s for each theme.
    - Populate the `QComboBox` and the `QAction`s by calling `self.theme_manager.get_available_themes()`.
    - In the population loop, check the `is_pro` flag. If a theme is pro and `pro.enabled` is `False`, disable the corresponding `QComboBox` item and `QAction` (`item.setEnabled(False)`).
    - Connect the `QComboBox.textActivated` signal and the `QAction.triggered` signal to a new slot, `self.on_theme_selected`.
    - In `on_theme_selected(self, theme_name)`, call `self.theme_manager.apply_theme(theme_name)`.
    - Save the active theme name to `QSettings` so it persists across sessions. On startup, apply the last used theme.

2.  **In `UISettingsManager` (`gui/settings/ui_settings.py`)**:

    - **Remove** the `_load_dark_mode_setting`, `_save_dark_mode_setting`, and `toggle_dark_mode` methods. This logic is now entirely handled by the `ThemeManager` and the theme selection in `main_window.py`. The `ThemeManager` will handle saving/loading the active theme name.

3.  **In `apptheme.py`**:
    - You can now **delete** the `apply_dark_palette` and `apply_light_palette` functions as their logic has been migrated into `light.json` and `dark.json`. Keep utility functions like `create_arrow_pixmap` if they are still needed for dynamic QSS generation.

---

### Phase 4: Implement the "Add Custom Theme" Pro Feature

1.  **Create a New Menu Action** in `main_window.py` under the `View -> Themes` menu: `add_theme_action = view_menu.addAction("Add Custom Theme...")`. This action should only be visible/enabled if `pro.enabled` is `True`. Connect its `triggered` signal to a new method `self.dialog_manager.open_add_theme_dialog()`.

2.  **Create the Dialog in `dialogs.py`**:
    - Create a new class `AddThemeDialog(QtWidgets.QDialog)`.
    - The dialog should contain a large `QPlainTextEdit` for pasting JSON, a `QPushButton("Save Theme")`, and a `QLabel` for status messages.
    - When the "Save Theme" button is clicked, get the text from the plain text edit and call `self.parent.theme_manager.add_custom_theme(json_text)`.
    - Display the success or error message from the return tuple in the status label.
    - On success, you should update the theme `QComboBox` in the main window to include the new theme and then close the dialog.

---

### Phase 5: Final Cleanup and Refactoring

1.  Search the entire project for any remaining calls to the old `toggle_dark_mode` or hardcoded palette functions and remove them.
2.  Update `pyproject.toml` to include the `aicodeprep_gui/themes/*.json` files in the package data.
    ```toml
    [tool.setuptools.package-data]
    aicodeprep_gui = ["data/default_config.toml", "images/*.png", "images/*.ico", "data/AICodePrep.workflow.zip", "themes/*.json"]
    ```
3.  Ensure the application starts up and correctly applies the default "Light" or "Dark" theme based on the last saved setting or system preference as a fallback.

This structured approach will result in a robust, maintainable, and feature-rich theming system. Proceed with these phases in order.

```

```
