Of course. Refactoring a large file like `gui.py` is a great way to improve maintainability and make it easier to add new features.

Here is a detailed plan to refactor `gui.py` into a more organized structure, followed by a prompt for Cline to execute the plan.

---

## Refactoring Plan for `aicodeprep-gui`

The primary goal is to break down the monolithic `gui.py` file into logical, feature-based modules. We will introduce a new `ui` and `config` folder within the `aicodeprep_gui` package to house these new modules. The pro features will remain in their own `pro` directory, which is a good pattern to follow.

### New Directory Structure

The new structure inside `aicodeprep_gui/` will look like this:

```
aicodeprep_gui/
├── config/
│   ├── __init__.py
│   ├── preferences.py   # Handles .aicodeprep-gui file I/O
│   └── presets.py       # Manages global button presets (GlobalPresetManager)
├── data/
│   └── ... (existing files)
├── images/
│   └── ... (existing files)
├── pro/
│   └── ... (existing files, no changes here)
├── ui/
│   ├── __init__.py
│   ├── dialogs.py       # Contains all pop-up dialogs (Installers, Vote, About, etc.)
│   └── widgets/
│       ├── __init__.py
│       └── flow_layout.py # The FlowLayout class
├── workers/
│   ├── __init__.py
│   └── update_worker.py # The UpdateCheckWorker QObject
├── __init__.py
├── apptheme.py
├── file_processor.py
├── linux_installer.py
├── macos_installer.py
├── main.py              # The application entry point (will be modified)
├── main_window.py       # The refactored main application window class
├── smart_logic.py
├── update_checker.py
└── windows_registry.py
```

### Step-by-Step Refactoring Details

1.  **`gui.py` -> `main_window.py`**: The main `FileSelectionGUI` class will be moved from `gui.py` to a new `aicodeprep_gui/main_window.py` file and renamed to `MainWindow`. Many of its constituent classes and helper functions will be moved out.

2.  **Configuration Logic -> `config/`**:

    - **`config/preferences.py`**: The file I/O functions for `.aicodeprep-gui` (`_prefs_path`, `_write_prefs_file`, `_read_prefs_file`) will move from `gui.py` to this new file. The `AICODEPREP_GUI_VERSION` constant will also move here.
    - **`config/presets.py`**: The `GlobalPresetManager` class and its global instance, along with `DEFAULT_PRESETS`, will move from `gui.py` to this new file.

3.  **UI Components -> `ui/`**:

    - **`ui/widgets/flow_layout.py`**: The `FlowLayout` class will be extracted into its own file. This makes it a reusable, self-contained widget.
    - **`ui/dialogs.py`**: All the dialog classes currently defined inside `FileSelectionGUI` or `gui.py` will be moved here. This includes:
      - `RegistryManagerDialog` (and its helper `open_registry_manager`)
      - `MacInstallerDialog` (and its helper `open_mac_installer`)
      - `LinuxInstallerDialog` (and its helper `open_linux_installer`)
      - `FeedbackDialog` (used by `open_complain_dialog`)
      - `VoteDialog`
      - The helper methods `open_about_dialog`, `open_links_dialog`, and `open_complain_dialog` will also be moved here, modified to be standalone functions that can be called from the main window.

4.  **Background Workers -> `workers/`**:

    - **`workers/update_worker.py`**: The `UpdateCheckWorker` class will be moved here. It's a self-contained background task runner.

5.  **Updating the Entry Point**:
    - **`main.py`**: The `main` function will be updated to import `MainWindow` from `aicodeprep_gui.main_window` instead of `FileSelectionGUI` from `gui.py`. The helper function `show_file_selection_gui` will be moved from `gui.py` into `main.py`.
    - The now-empty `gui.py` file will be deleted.

### Summary of Changes

- **Create Folders**: `aicodeprep_gui/config`, `aicodeprep_gui/ui`, `aicodeprep_gui/ui/widgets`, `aicodeprep_gui/workers`.
- **Create Files**: `config/__init__.py`, `config/preferences.py`, `config/presets.py`, `ui/__init__.py`, `ui/dialogs.py`, `ui/widgets/__init__.py`, `ui/widgets/flow_layout.py`, `workers/__init__.py`, `workers/update_worker.py`, `main_window.py`.
- **Modify Files**: `main.py`.
- **Delete File**: `gui.py`.
- **No Changes to**: `pro/`, `smart_logic.py`, `file_processor.py`, `apptheme.py`, installer scripts.

This plan isolates concerns, makes the code easier to navigate, and prepares a clean structure for adding more features (especially pro features) without cluttering the main window logic.

---

## Prompt for Cline

Hello Cline,

I need to refactor the `aicodeprep-gui` application to improve its structure and maintainability. Your task is to break down the monolithic `gui.py` file into several smaller, logically organized modules within new subdirectories. The application's functionality must remain identical after your changes. I will handle the testing later.

Please follow this detailed plan precisely. Create all new directories and files, move the specified code, and update the necessary imports.

### High-Level Plan

1.  **Deconstruct `gui.py`**: Extract helper classes, dialogs, and utility functions into new, dedicated modules.
2.  **Organize Modules**: Place the new modules into a logical folder structure: `config/`, `ui/`, `workers/`.
3.  **Rename and Refactor**: Rename `gui.py` to `main_window.py` and update it to import the functionality you extracted.
4.  **Update Entry Point**: Modify `main.py` to use the new `main_window.py`.
5.  **Cleanup**: Delete the original `gui.py` file after its contents have been moved.

### New Directory Structure

Create the following new directories and empty `__init__.py` files:

- `aicodeprep_gui/config/` (and `__init__.py`)
- `aicodeprep_gui/ui/` (and `__init__.py`)
- `aicodeprep_gui/ui/widgets/` (and `__init__.py`)
- `aicodeprep_gui/workers/` (and `__init__.py`)

### Step-by-Step Instructions

**1. Create `aicodeprep_gui/config/preferences.py`**

- Create this new file.
- Move the following functions from `gui.py` into it: `_prefs_path`, `_write_prefs_file`, `_read_prefs_file`.
- Move the `AICODEPREP_GUI_VERSION` constant from `gui.py` into it.
- Ensure the file has the necessary imports: `os`, `sys`, `logging`, `json`, `base64`.

**2. Create `aicodeprep_gui/config/presets.py`**

- Create this new file.
- Move the `GlobalPresetManager` class, its instance `global_preset_manager`, and the `DEFAULT_PRESETS` list from `gui.py` into it.
- Add the required imports: `logging`, `PySide6.QtCore`.

**3. Create `aicodeprep_gui/ui/widgets/flow_layout.py`**

- Create this new file.
- Move the `FlowLayout` class from `gui.py` into it.
- Add the required imports: `PySide6.QtWidgets`, `PySide6.QtCore`.

**4. Create `aicodeprep_gui/workers/update_worker.py`**

- Create this new file.
- Move the `UpdateCheckWorker` class from `gui.py` into it.
- Add the required imports: `PySide6.QtCore` and `aicodeprep_gui.update_checker`.

**5. Create `aicodeprep_gui/ui/dialogs.py`**

- Create this new file.
- Move the `RegistryManagerDialog`, `MacInstallerDialog`, `LinuxInstallerDialog`, `FeedbackDialog` (from within `open_complain_dialog`), and `VoteDialog` classes from `gui.py` into it.
- Move the helper functions `open_registry_manager`, `open_mac_installer`, `open_linux_installer`, `open_links_dialog`, `open_complain_dialog`, and `open_about_dialog` from `gui.py` into this file. You will need to modify them slightly so they can be called with the main window instance as a `parent` argument.
- Ensure this file has all necessary imports, such as `os`, `sys`, `platform`, `logging`, `json`, `datetime`, `requests`, `PySide6.QtWidgets`, `PySide6.QtCore`, `PySide6.QtGui`, and the local installer modules (`aicodeprep_gui.windows_registry`, etc.).

**6. Refactor `gui.py` into `aicodeprep_gui/main_window.py`**

- Rename `aicodeprep_gui/gui.py` to `aicodeprep_gui/main_window.py`.
- In `main_window.py`, rename the class `FileSelectionGUI` to `MainWindow`.
- **Remove** all the code you moved in the previous steps from this file.
- **Add** the following imports to the top of `main_window.py` to replace the code you removed:
  ```python
  from aicodeprep_gui.config.preferences import _read_prefs_file, _write_prefs_file, AICODEPREP_GUI_VERSION
  from aicodeprep_gui.config.presets import global_preset_manager
  from aicodeprep_gui.ui.widgets.flow_layout import FlowLayout
  from aicodeprep_gui.workers.update_worker import UpdateCheckWorker
  from aicodeprep_gui.ui.dialogs import (
      open_registry_manager, open_mac_installer, open_linux_installer,
      open_links_dialog, open_about_dialog, open_complain_dialog,
      VoteDialog
  )
  ```
- In the `MainWindow` class, update the calls to the moved dialog functions. For example, `self.open_about_dialog` becomes `open_about_dialog(self)`. Do this for all the dialog-opening functions.
- Remove the `show_file_selection_gui` function from the bottom of the file.

**7. Update `aicodeprep_gui/main.py` (The Entry Point)**

- In `aicodeprep_gui/main.py`, find the line `from aicodeprep_gui.gui import show_file_selection_gui`.
- **Replace it** with these lines:
  ```python
  from aicodeprep_gui.main_window import MainWindow
  from PySide6 import QtWidgets
  ```
- Add a new function `show_main_window` to `main.py` that was previously `show_file_selection_gui` in `gui.py`:
  ```python
  def show_main_window(files):
      app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
      gui = MainWindow(files)
      gui.show()
      app.exec()
      return gui.action, gui.get_selected_files()
  ```
- In the `main()` function of `main.py`, find the line `action, _ = show_file_selection_gui(all_files_with_flags)`.
- Change it to `action, _ = show_main_window(all_files_with_flags)`.

**8. Final Cleanup**

- After all the refactoring, if a `gui.py` file still exists, rename it gui_bkup.py
  Execute these steps to complete the refactoring.
