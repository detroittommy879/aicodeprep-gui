Please refactor the large gui.py file into a modular structure. I will provide very detailed instructions with code examples to ensure this is done correctly. The goal is to split the ~1000 line file into logical, maintainable components while preserving ALL functionality exactly as it currently works.

## IMPORTANT: Read the entire prompt before starting!

## Step 1: Create the new directory structure

Create these new directories and empty files (just create empty files for now):

```
aicodeprep_gui/gui/__init__.py
aicodeprep_gui/gui/main_window.py
aicodeprep_gui/gui/components/__init__.py
aicodeprep_gui/gui/components/layouts.py
aicodeprep_gui/gui/components/dialogs.py
aicodeprep_gui/gui/components/tree_widget.py
aicodeprep_gui/gui/components/preset_buttons.py
aicodeprep_gui/gui/settings/__init__.py
aicodeprep_gui/gui/settings/presets.py
aicodeprep_gui/gui/settings/preferences.py
aicodeprep_gui/gui/settings/ui_settings.py
aicodeprep_gui/gui/handlers/__init__.py
aicodeprep_gui/gui/handlers/update_events.py
aicodeprep_gui/gui/handlers/file_events.py
aicodeprep_gui/gui/handlers/ui_events.py
aicodeprep_gui/gui/utils/__init__.py
aicodeprep_gui/gui/utils/metrics.py
aicodeprep_gui/gui/utils/helpers.py
```

## Step 2: Extract specific components (DO THESE IN ORDER)

### A. Create `aicodeprep_gui/gui/components/layouts.py`

Copy the ENTIRE FlowLayout class from gui.py (starts around line 100) and put it in this file:

```python
from PySide6 import QtWidgets, QtCore

class FlowLayout(QtWidgets.QLayout):
    # COPY THE ENTIRE FlowLayout CLASS HERE - all methods including:
    # __init__, __del__, addItem, horizontalSpacing, verticalSpacing,
    # count, itemAt, takeAt, insertWidget, insertItem, removeWidget,
    # expandingDirections, hasHeightForWidth, heightForWidth,
    # setGeometry, sizeHint, minimumSize, doLayout, smartSpacing
```

### B. Create `aicodeprep_gui/gui/settings/presets.py`

Extract preset-related code:

```python
import logging
from PySide6 import QtCore

# Copy these constants from gui.py:
AICODEPREP_GUI_VERSION = "1.0"

DEFAULT_PRESETS = [
    ("Debug", "Can you help me debug this code?"),
    ("Security check", "Can you analyze this code for any security issues?"),
    ("Best Practices", "Please analyze this code for: Error handling, Edge cases, Performance optimization, Best practices, Please do not unnecessarily remove any comments or code. Generate the code with clear comments explaining the logic."),
    ("Please review for", "Code quality and adherence to best practices, Potential bugs or edge cases, Performance optimizations, Readability and maintainability, Security concerns. Suggest improvements and explain your reasoning for each suggestion"),
    ("Cline, Roo Code Prompt", "Write a prompt for Cline, an AI coding agent, to make the necessary changes. Enclose the entire Cline prompt in one single code tag for easy copy and paste.")
]

class GlobalPresetManager:
    # COPY THE ENTIRE GlobalPresetManager CLASS from gui.py
    # Including all methods: __init__, _ensure_default_presets, get_all_presets, add_preset, delete_preset

# Create the global instance
global_preset_manager = GlobalPresetManager()
```

### C. Create `aicodeprep_gui/gui/handlers/update_events.py`

```python
import json
import logging
from datetime import datetime
from PySide6 import QtCore
from aicodeprep_gui import update_checker

class UpdateCheckWorker(QtCore.QObject):
    # COPY THE ENTIRE UpdateCheckWorker CLASS from gui.py
    # This includes the finished signal and run method
```

### D. Create `aicodeprep_gui/gui/components/dialogs.py`

Extract ALL dialog-related code:

```python
import os
import sys
import json
import logging
import requests
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui import __version__

class VoteDialog(QtWidgets.QDialog):
    # COPY THE ENTIRE VoteDialog class from gui.py
    # This includes FEATURE_IDEAS, VOTE_OPTIONS, __init__, _make_vote_handler, submit_votes

class DialogManager:
    def __init__(self, parent_window):
        self.parent = parent_window

    def open_links_dialog(self):
        # COPY the open_links_dialog method from FileSelectionGUI class

    def open_complain_dialog(self):
        # COPY the open_complain_dialog method from FileSelectionGUI class

    def open_about_dialog(self):
        # COPY the open_about_dialog method from FileSelectionGUI class

    def add_new_preset_dialog(self):
        # COPY the add_new_preset_dialog method from FileSelectionGUI class

    def delete_preset_dialog(self):
        # COPY the delete_preset_dialog method from FileSelectionGUI class
```

### E. Create `aicodeprep_gui/gui/settings/preferences.py`

```python
import os
import logging
import base64
from PySide6 import QtCore

# Version for .aicodeprep-gui file format
AICODEPREP_GUI_VERSION = "1.0"

def _prefs_path():
    # COPY the _prefs_path function from gui.py exactly

def _write_prefs_file(checked_relpaths, window_size=None, splitter_state=None, output_format=None):
    # COPY the _write_prefs_file function from gui.py exactly

def _read_prefs_file():
    # COPY the _read_prefs_file function from gui.py exactly

class PreferencesManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.checked_files_from_prefs = set()
        self.window_size_from_prefs = None
        self.splitter_state_from_prefs = None
        self.output_format_from_prefs = "xml"
        self.prefs_loaded = False

    def load_prefs_if_exists(self):
        # COPY the load_prefs_if_exists method from FileSelectionGUI

    def save_prefs(self):
        # COPY the save_prefs method from FileSelectionGUI

    def load_from_prefs_button_clicked(self):
        # COPY the load_from_prefs_button_clicked method from FileSelectionGUI
```

### F. Create `aicodeprep_gui/gui/settings/ui_settings.py`

```python
import logging
from PySide6 import QtCore
from aicodeprep_gui.apptheme import (
    system_pref_is_dark, apply_dark_palette, apply_light_palette,
    get_checkbox_style_dark, get_checkbox_style_light
)

class UISettingsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _load_dark_mode_setting(self):
        # COPY the _load_dark_mode_setting method from FileSelectionGUI

    def _save_dark_mode_setting(self):
        # COPY the _save_dark_mode_setting method from FileSelectionGUI

    def toggle_dark_mode(self, state):
        # COPY the toggle_dark_mode method from FileSelectionGUI

    def _load_panel_visibility(self):
        # COPY the _load_panel_visibility method from FileSelectionGUI

    def _save_panel_visibility(self):
        # COPY the _save_panel_visibility method from FileSelectionGUI

    def _load_prompt_options(self):
        # COPY the _load_prompt_options method from FileSelectionGUI

    def _save_prompt_options(self):
        # COPY the _save_prompt_options method from FileSelectionGUI

    def _save_format_choice(self, idx):
        # COPY the _save_format_choice method from FileSelectionGUI
```

### G. Create `aicodeprep_gui/gui/components/tree_widget.py`

```python
import os
import logging
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui import smart_logic

class FileTreeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def on_item_expanded(self, item):
        # COPY the on_item_expanded method from FileSelectionGUI

    def handle_item_changed(self, item, column):
        # COPY the handle_item_changed method from FileSelectionGUI

    def expand_parents_of_item(self, item):
        # COPY the expand_parents_of_item method from FileSelectionGUI

    def get_selected_files(self):
        # COPY the get_selected_files method from FileSelectionGUI

    def select_all(self):
        # COPY the select_all method from FileSelectionGUI

    def deselect_all(self):
        # COPY the deselect_all method from FileSelectionGUI

    def _expand_folders_for_paths(self, checked_paths):
        # COPY the _expand_folders_for_paths method from FileSelectionGUI

    def auto_expand_common_folders(self):
        # COPY the auto_expand_common_folders method from FileSelectionGUI
```

### H. Create `aicodeprep_gui/gui/utils/metrics.py`

```python
import json
import logging
from datetime import datetime
from PySide6 import QtNetwork, QtCore

class MetricsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _send_metric_event(self, event_type, token_count=None):
        # COPY the _send_metric_event method from FileSelectionGUI exactly
```

### I. Create `aicodeprep_gui/gui/components/preset_buttons.py`

```python
import logging
from PySide6 import QtWidgets, QtCore
from aicodeprep_gui.gui.settings.presets import global_preset_manager

class PresetButtonManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _load_global_presets(self):
        # COPY the _load_global_presets method from FileSelectionGUI

    def _add_preset_button(self, label, text, from_local=False, from_global=False):
        # COPY the _add_preset_button method from FileSelectionGUI

    def _delete_preset(self, label, button, from_global):
        # COPY the _delete_preset method from FileSelectionGUI

    def _apply_preset(self, preset_text):
        # COPY the _apply_preset method from FileSelectionGUI
```

### J. Create `aicodeprep_gui/gui/utils/helpers.py`

```python
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
        # COPY the open_settings_folder method from FileSelectionGUI

    def dragEnterEvent(self, event):
        # COPY the dragEnterEvent method from FileSelectionGUI

    def dropEvent(self, event):
        # COPY the dropEvent method from FileSelectionGUI

    def showEvent(self, event):
        # COPY the showEvent method from FileSelectionGUI

    def closeEvent(self, event):
        # COPY the closeEvent method from FileSelectionGUI
```

## Step 3: Create the main window class

### Create `aicodeprep_gui/gui/main_window.py`

This is the BIG ONE. You need to:

1. Start with ALL the imports from the original gui.py
2. Add imports for all the new component classes you just created
3. Create a new FileSelectionGUI class that uses all the components

Here's the structure:

```python
# COPY ALL IMPORTS from the original gui.py at the top

# ADD these new imports:
from .components.layouts import FlowLayout
from .components.dialogs import DialogManager, VoteDialog
from .components.tree_widget import FileTreeManager
from .components.preset_buttons import PresetButtonManager
from .settings.presets import global_preset_manager
from .settings.preferences import PreferencesManager
from .settings.ui_settings import UISettingsManager
from .handlers.update_events import UpdateCheckWorker
from .utils.metrics import MetricsManager
from .utils.helpers import WindowHelpers

class FileSelectionGUI(QtWidgets.QMainWindow):
    def __init__(self, files):
        super().__init__()

        # Initialize component managers FIRST
        self.dialog_manager = DialogManager(self)
        self.preferences_manager = PreferencesManager(self)
        self.ui_settings_manager = UISettingsManager(self)
        self.tree_manager = FileTreeManager(self)
        self.preset_manager = PresetButtonManager(self)
        self.metrics_manager = MetricsManager(self)
        self.window_helpers = WindowHelpers(self)

        # COPY the rest of the __init__ method from the original FileSelectionGUI
        # BUT replace method calls with calls to the appropriate manager:
        #
        # OLD: self.load_prefs_if_exists()
        # NEW: self.preferences_manager.load_prefs_if_exists()
        #
        # OLD: self._load_dark_mode_setting()
        # NEW: self.ui_settings_manager._load_dark_mode_setting()
        #
        # etc.

    # Delegate methods to managers:
    def load_prefs_if_exists(self):
        return self.preferences_manager.load_prefs_if_exists()

    def save_prefs(self):
        return self.preferences_manager.save_prefs()

    def toggle_dark_mode(self, state):
        return self.ui_settings_manager.toggle_dark_mode(state)

    def on_item_expanded(self, item):
        return self.tree_manager.on_item_expanded(item)

    def handle_item_changed(self, item, column):
        return self.tree_manager.handle_item_changed(item, column)

    def get_selected_files(self):
        return self.tree_manager.get_selected_files()

    def select_all(self):
        return self.tree_manager.select_all()

    def deselect_all(self):
        return self.tree_manager.deselect_all()

    def open_links_dialog(self):
        return self.dialog_manager.open_links_dialog()

    def open_about_dialog(self):
        return self.dialog_manager.open_about_dialog()

    def open_complain_dialog(self):
        return self.dialog_manager.open_complain_dialog()

    def add_new_preset_dialog(self):
        return self.dialog_manager.add_new_preset_dialog()

    def delete_preset_dialog(self):
        return self.dialog_manager.delete_preset_dialog()

    def _send_metric_event(self, event_type, token_count=None):
        return self.metrics_manager._send_metric_event(event_type, token_count)

    def open_settings_folder(self):
        return self.window_helpers.open_settings_folder()

    def dragEnterEvent(self, event):
        return self.window_helpers.dragEnterEvent(event)

    def dropEvent(self, event):
        return self.window_helpers.dropEvent(event)

    def showEvent(self, event):
        return self.window_helpers.showEvent(event)

    def closeEvent(self, event):
        return self.window_helpers.closeEvent(event)

    # COPY ALL OTHER METHODS that are NOT moved to managers:
    # - process_selected
    # - quit_without_processing
    # - update_token_counter
    # - toggle_preview_window (if pro features)
    # - update_file_preview (if pro features)
    # - _generate_arrow_pixmaps
    # - _update_groupbox_style
    # - _start_update_check
    # - on_update_check_finished
    # etc.
```

IMPORTANT: In the **init** method, find EVERY method call that starts with `self.` and check if you moved that method to a manager. If so, change it to call the manager instead.

For example:

- `self.load_prefs_if_exists()` becomes `self.preferences_manager.load_prefs_if_exists()`
- `self._load_dark_mode_setting()` becomes `self.ui_settings_manager._load_dark_mode_setting()`

## Step 4: Create the main gui module

### Create `aicodeprep_gui/gui/__init__.py`

```python
from .main_window import FileSelectionGUI
from .handlers.update_events import UpdateCheckWorker

def show_file_selection_gui(files):
    # COPY the show_file_selection_gui function from gui.py exactly
    pass

# Re-export for backwards compatibility
__all__ = ['FileSelectionGUI', 'show_file_selection_gui', 'UpdateCheckWorker']
```

## Step 5: Update component **init**.py files

### `aicodeprep_gui/gui/components/__init__.py`

```python
from .layouts import FlowLayout
from .dialogs import DialogManager, VoteDialog
from .tree_widget import FileTreeManager
from .preset_buttons import PresetButtonManager

__all__ = ['FlowLayout', 'DialogManager', 'VoteDialog', 'FileTreeManager', 'PresetButtonManager']
```

### `aicodeprep_gui/gui/settings/__init__.py`

```python
from .presets import GlobalPresetManager, global_preset_manager
from .preferences import PreferencesManager
from .ui_settings import UISettingsManager

__all__ = ['GlobalPresetManager', 'global_preset_manager', 'PreferencesManager', 'UISettingsManager']
```

### `aicodeprep_gui/gui/handlers/__init__.py`

```python
from .update_events import UpdateCheckWorker

__all__ = ['UpdateCheckWorker']
```

### `aicodeprep_gui/gui/utils/__init__.py`

```python
from .metrics import MetricsManager
from .helpers import WindowHelpers

__all__ = ['MetricsManager', 'WindowHelpers']
```

## Step 6: CRITICAL - Fix all the self references

When you copy methods from FileSelectionGUI to the manager classes, you need to change `self.` references:

**In manager classes, change:**

- `self.tree_widget` to `self.main_window.tree_widget`
- `self.prompt_textbox` to `self.main_window.prompt_textbox`
- `self.is_dark_mode` to `self.main_window.is_dark_mode`
- `self.app` to `self.main_window.app`
- etc.

**Every `self.` that refers to a GUI widget or attribute needs to become `self.main_window.`**

## Step 7: Update signal connections

In the main_window.py `__init__` method, find all the signal connections like:

```python
self.tree_widget.itemExpanded.connect(self.on_item_expanded)
```

Change them to:

```python
self.tree_widget.itemExpanded.connect(self.tree_manager.on_item_expanded)
```

## CRITICAL CHECKS before you're done:

1. Make sure EVERY method from the original FileSelectionGUI class is either:

   - Moved to a manager class, OR
   - Still present in the new FileSelectionGUI class, OR
   - Available as a delegation method in the new FileSelectionGUI class

2. Make sure ALL imports are preserved

3. Make sure ALL constants and global variables are moved to appropriate files

4. Make sure the `show_file_selection_gui` function is preserved exactly

5. Double-check that all `self.` references in manager classes point to `self.main_window.` where needed

The final result should be that `from aicodeprep_gui.gui import FileSelectionGUI` still works exactly the same as before.

```

```
