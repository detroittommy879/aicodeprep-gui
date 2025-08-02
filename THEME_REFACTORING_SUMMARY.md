# Theme System Refactoring Summary

This document outlines the changes made to refactor the application's theming system from a hardcoded light/dark toggle to a flexible, data-driven architecture using JSON theme files.

## Objectives

The primary goals of this refactoring were:

1.  **Extensibility**: Enable easy addition of new themes by simply adding JSON files.
2.  **User Customization**: Lay the groundwork for a Pro feature allowing users to add custom themes.
3.  **Separation of Concerns**: Decouple UI logic from theme definitions, centralizing theme management.
4.  **Advanced Features**: Support for custom fonts (loaded from Google Fonts) and fine-grained QSS overrides via JSON.

## Phases of Implementation

The refactoring was carried out in five main phases:

### Phase 1: Create the Data Layer (Theme Files)

A new directory for theme definitions was created, and initial theme files were added.

- **New Directory**: `aicodeprep_gui/themes/`

  - This directory houses all packaged theme JSON files.

- **New Files**:
  - `aicodeprep_gui/themes/dracula-pro.json`: A template for a Pro-gated theme, demonstrating the full JSON structure including `meta`, `fonts`, `colors`, and `qss_overrides`.
  - `aicodeprep_gui/themes/light.json`: The default light theme. Colors were migrated from the old `apply_light_palette` function in `aicodeprep_gui/apptheme.py`.
  - `aicodeprep_gui/themes/dark.json`: The default dark theme. Colors were migrated from the old `apply_dark_palette` function in `aicodeprep_gui/apptheme.py`.

### Phase 2: Implement the `ThemeManager`

A central class for managing all theming logic was introduced.

- **New File**: `aicodeprep_gui/gui/theming.py`
  - Contains the `ThemeManager(QtCore.QObject)` class.
  - **Key Responsibilities**:
    - Discovering packaged and user themes.
    - Loading and caching custom fonts (e.g., from Google Fonts).
    - Generating QSS stylesheets dynamically from JSON theme data.
    - Applying themes to the application.
    - Providing a list of available themes.
    - Handling the addition of custom user-submitted themes.
  - **Key Signal**: `theme_changed = QtCore.Signal(str)`: Emitted when a theme is applied, allowing UI components to update if necessary.

### Phase 3: Integrate `ThemeManager` into the UI

The main application window and settings were updated to use the new `ThemeManager`.

- **Modified File**: `aicodeprep_gui/gui/main_window.py`

  - **Imports**: Added `from .theming import ThemeManager`.
  - **Initialization**: Instantiates `self.theme_manager = ThemeManager(self.app)` in `__init__`.
  - **UI Replacement**:
    - The old `self.dark_mode_box` (QCheckBox) was removed.
    - A new `self.theme_combo` (QComboBox) was added to the "Options" group box to allow theme selection.
  - **Menu Integration**:
    - A "Themes" submenu was added to the "View" menu (`view_menu`).
    - This submenu is populated with `QAction`s for each available theme, allowing selection from the menu as well.
  - **Pro Feature Gating**: Theme items in both the `QComboBox` and the "Themes" submenu are disabled if the theme is marked as `"pro": true` in its JSON and `pro.enabled` is `False`.
  - **Signal Handling**:
    - `self.theme_combo.textActivated` and theme `QAction.triggered` are connected to `self.on_theme_selected(theme_name)`.
    - `self.theme_manager.theme_changed` is connected to `self.on_theme_changed(stylesheet)` to update specific UI elements (like `QGroupBox` styles that use dynamic pixmaps).
  - **Persistence**: The active theme name is saved to/loaded from `QSettings` via the `ThemeManager`.

- **Modified File**: `aicodeprep_gui/gui/settings/ui_settings.py`
  - **Cleanup**: Removed methods and imports related to the old dark mode toggle (`_load_dark_mode_setting`, `_save_dark_mode_setting`, `toggle_dark_mode`, and imports for `apply_dark_palette`, `apply_light_palette`, `get_checkbox_style_dark`, `get_checkbox_style_light`). This logic is now fully handled by the `ThemeManager`.

### Phase 4: Implement the "Add Custom Theme" Pro Feature

A dialog and logic for Pro users to add their own themes was implemented.

- **Modified File**: `aicodeprep_gui/gui/components/dialogs.py`

  - **New Class**: `AddThemeDialog(QtWidgets.QDialog)`
    - Provides a `QPlainTextEdit` for users to paste JSON theme definitions.
    - Includes a "Save Theme" button and a status label for feedback.
    - Calls `self.theme_manager.add_custom_theme(json_text)` on save.
  - **DialogManager Integration**: The `DialogManager.open_add_theme_dialog()` method was updated to create and show `AddThemeDialog` if `pro.enabled` is true. It also handles refreshing the theme controls in the main window upon successful theme addition.

- **Modified File**: `aicodeprep_gui/gui/main_window.py`
  - An "Add Custom Theme..." `QAction` is added to the "View -> Themes" menu if `pro.enabled` is true. This action is connected to `self.dialog_manager.open_add_theme_dialog()`.

### Phase 5: Final Cleanup and Refactoring

Remaining old code was removed, and packaging was updated.

- **Modified File**: `aicodeprep_gui/apptheme.py`

  - **Deleted Functions**:
    - `apply_dark_palette(app)`
    - `apply_light_palette(app)`
    - `get_checkbox_style_dark()`
    - `get_checkbox_style_light()`
  - The `_checkbox_style(dark)` and related image loading logic remain, as they might be useful if the `ThemeManager` needs to generate checkbox-specific QSS using image paths, or for other components. However, the main QSS generation is now expected to cover checkbox styles.

- **Modified File**: `aicodeprep_gui/gui/settings/ui_settings.py`

  - **Removed Imports**: Cleaned up imports for `get_checkbox_style_dark` and `get_checkbox_style_light` as they are no longer used anywhere.

- **Modified File**: `pyproject.toml`
  - **Package Data**: The `[tool.setuptools.package-data]` section for `aicodeprep_gui` was updated to include `"themes/*.json"`. This ensures that all JSON files in the `themes` directory are packaged when the application is built (e.g., using `pyinstaller` or when creating a distributable wheel).

## Files Changed

| File Path                                    | Type of Change                                                                                              |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `aicodeprep_gui/themes/`                     | **New Directory**                                                                                           |
| `aicodeprep_gui/themes/dracula-pro.json`     | **New File** (Pro theme template)                                                                           |
| `aicodeprep_gui/themes/light.json`           | **New File** (Default light theme)                                                                          |
| `aicodeprep_gui/themes/dark.json`            | **New File** (Default dark theme)                                                                           |
| `aicodeprep_gui/gui/theming.py`              | **New File** (Core `ThemeManager` class)                                                                    |
| `aicodeprep_gui/gui/main_window.py`          | **Major Refactor** (Integrated `ThemeManager`, replaced UI elements, added theme selection logic and menus) |
| `aicodeprep_gui/gui/settings/ui_settings.py` | **Cleanup** (Removed old dark mode logic and unused imports)                                                |
| `aicodeprep_gui/gui/components/dialogs.py`   | **Enhancement** (Added `AddThemeDialog` class and updated `DialogManager`)                                  |
| `aicodeprep_gui/apptheme.py`                 | **Cleanup** (Removed obsolete palette and checkbox style functions)                                         |
| `pyproject.toml`                             | **Configuration Update** (Added `themes/*.json` to package data)                                            |

---

## Bug Fixing Phase: Guidance & Areas to Test

After such a significant refactoring, a dedicated bug-fixing phase is crucial. Here are key areas to focus on and potential issues to anticipate:

### 1. Theme Application and Visual Consistency

- **Test All Themes**: Systematically select each available theme (Light, Dark, Dracula Pro if accessible).
  - **Check**: Do all UI elements update correctly? (Window background, text colors, buttons, group boxes, tree widgets, menus, etc.)
  - **Check**: Are there any visual glitches or elements that seem to ignore the theme?
- **QSS Overrides**: Verify that any `qss_overrides` in the theme JSONs are being applied correctly.
  - **Example**: The `FileSelectionGUI #vibe_label` override in `dracula-pro.json`.
- **Dynamic Elements**: Elements styled outside the main QSS (like `QGroupBox` titles that use arrow pixmaps) need special attention.
  - The `on_theme_changed` slot in `main_window.py` calls `_update_groupbox_style`. Ensure this works correctly for all themes and that arrow pixmaps are visible and have the correct color.
- **Checkbox Styles**: Confirm that `QTreeWidget` checkboxes are styled correctly by the new QSS generated by `ThemeManager`. The old `_checkbox_style` function in `apptheme.py` is no longer directly used for global application styling.

### 2. Functionality and Interaction

- **Theme Persistence**:
  - Select a theme, close the application, and reopen it. Does the last selected theme load correctly?
  - Check the `QSettings` (e.g., in `~/.config/aicodeprep-gui.conf` on Linux or Registry on Windows) to ensure `activeThemeName` is being saved and loaded.
- **Pro Theme Gating**:
  - With `pro.enabled = false`, are Pro themes (like Dracula Pro) correctly disabled in the `QComboBox` and "Themes" menu?
  - Attempting to select a disabled Pro theme should show a warning message and revert the selection.
  - With `pro.enabled = true`, can Pro themes be selected and applied correctly?
- **"Add Custom Theme" Feature (Pro Only)**:
  - With `pro.enabled = true`, does the "Add Custom Theme..." dialog open?
  - **Valid JSON**: Paste a valid theme JSON and save. Does it appear in the theme list? Can it be selected and applied?
  - **Invalid JSON**: Paste invalid JSON (e.g., malformed, missing required keys like `meta.name` or `colors`). Does the dialog show an appropriate error message?
  - **User Theme Directory**: Verify that custom themes are saved to the correct user-specific directory (e.g., `~/.config/aicodeprep-gui/themes/` or equivalent) and that `ThemeManager` discovers them from there.
- **Font Loading (if implemented in `ThemeManager`)**:
  - If a theme specifies a Google Font (e.g., "Fira Code" in `dracula-pro.json`), does the `ThemeManager` correctly download, cache, and apply it?
  - Check network requests (if any) and the font cache directory.
  - Test on a system without an internet connection to see if it handles missing fonts gracefully (e.g., falls back to a default).

### 3. Performance and Stability

- **Theme Switching Speed**: Is there a noticeable lag when switching between themes? The `_generate_stylesheet` method should be efficient.
- **Memory Usage**: Monitor memory usage before and after switching themes multiple times. Ensure there are no memory leaks, especially related to QSS generation or font loading.
- **Error Handling**:
  - What happens if a theme JSON file is corrupted or unreadable? The `ThemeManager` should log an error and skip that theme, not crash.
  - What happens if a font download fails? The application should remain stable, possibly falling back to a default font.

### 4. Cross-Platform Consistency

- **Test on all supported OSes (Windows, macOS, Linux)**:
  - Theme rendering can sometimes vary slightly between platforms due to native style differences.
  - Pay close attention to `QStandardPaths` for cache and user theme directories to ensure they are correct and writable on each OS.
  - Font rendering can also differ.

### 5. Logging and Debugging

- **Enable Debug Logging**: Set `logging.DEBUG` to get detailed output from the `ThemeManager`.
  - Check logs for theme discovery, font loading, QSS generation, and any errors encountered.
  - This will be invaluable for tracking down issues.
- **Descriptive Errors**: As per the `.clinerules` custom instruction, ensure that any errors logged or shown to the user are descriptive enough to aid in debugging. For example, when a custom theme fails to save, the message should indicate _why_ (e.g., "Invalid JSON format", "Missing 'meta.name' key").

### Recommended Bug-Fixing Workflow

1.  **Smoke Test**: Launch the application. Does it start without crashing? Is the default theme applied correctly?
2.  **Systematic Theme Testing**: Go through each theme one by one. Visually inspect the UI and check key functionalities.
3.  **Feature-Specific Testing**:
    - Test theme persistence (close/open).
    - Test Pro theme gating (with Pro on/off).
    - Test the "Add Custom Theme" dialog with valid and invalid inputs.
4.  **Edge Case Testing**:
    - What if all theme JSON files are deleted?
    - What if the user's theme directory is not writable?
    - What if a theme JSON is missing the `colors` section?
5.  **Cross-Platform Test Run**: If possible, run the application on different operating systems.
6.  **Log Review**: After testing sessions, review the logs for any warnings or errors that might have been missed visually.

By methodically working through these areas, you can identify and resolve issues introduced during the refactoring, ensuring a stable and polished theming system.
