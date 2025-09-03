# AI Agent Prompt: Wrap User-Facing Strings with Translation Markers

## Task Overview

You are an AI agent tasked with implementing internationalization in the AI Code Prep GUI application by wrapping all user-facing strings with appropriate translation markers.

## Your Mission

Wrap all user-facing strings in the application code with `self.tr()` method calls so they can be extracted for translation.

## Key Files to Modify

1. `aicodeprep_gui/gui/main_window.py` - Main application window
2. `aicodeprep_gui/gui/components/dialogs.py` - All dialog components
3. `aicodeprep_gui/gui/components/installer_dialogs.py` - Installation dialogs
4. `aicodeprep_gui/gui/components/preset_buttons.py` - Preset button components
5. `aicodeprep_gui/main.py` - Main application entry point

## Translation Guidelines

### Basic String Wrapping

- Wrap all literal strings that users will see with `self.tr()`
- Example: `self.setWindowTitle("aicodeprep-gui - File Selection")`
  becomes: `self.setWindowTitle(self.tr("aicodeprep-gui - File Selection"))`

### Menu Items and Actions

- All menu text, action labels, and tooltips need translation
- Example: `quit_act = QtGui.QAction("&Quit", self)`
  becomes: `quit_act = QtGui.QAction(self.tr("&Quit"), self)`

### Dynamic Strings

- For strings with variables, use `self.tr()` with `.arg()` method
- Example: `self.token_label.setText(f"Estimated tokens: {total_tokens:,}")`
  becomes: `self.token_label.setText(self.tr("Estimated tokens: %L1").arg(total_tokens))`

### String Formatting

- Use Qt's translation formatting: `%1`, `%2`, `%L1` (for localized numbers)
- Placeholders will be replaced in the translated strings

## What NOT to Translate

- Internal variable names
- File paths and technical identifiers
- Debug strings or developer comments
- String keys used for programmatic purposes

Here is a comprehensive list of every user-facing string that needs to be set up for translation.

### 1. `aicodeprep_gui/gui/components/dialogs.py`

- **Class `ShareDialog`**

  - `SHARE_TEXT` constant (near line 159): `"I'm using aicodeprep-gui to easily prepare my code for LLMs. It's a huge time-saver! Check it out:"`
  - `__init__` method:
    - Line 167: `self.setWindowTitle("Share AI Code Prep")`
    - Line 173: `QtWidgets.QLabel("Enjoying this tool? Share it!")`

STOP HERE to let me test the app to make sure its working --------------------

    - Line 184: `QtWidgets.QLabel("If you find this tool useful, please consider sharing it with others. It's the best way to support its development and help fellow developers!")`
    - Line 190: `QtWidgets.QGroupBox("Copy the link")`
    - Line 194: `QtWidgets.QPushButton("Copy")`
    - Line 199: `QtWidgets.QGroupBox("One-click sharing")`
    - Line 203: `QtWidgets.QPushButton("Share on 𝕏 (Twitter)")`
    - Line 207: `QtWidgets.QPushButton("Share on Reddit")`

- `copy_link` method:
  - Line 218: `self.copy_button.setText("Copied!")`
- `reset_copy_button` method:
  - Line 223: `self.copy_button.setText("Copy")`
- `share_on_reddit` method:

  - Line 233: The title string `"Check out aicodeprep-gui for AI developers"`.

- **Class `DialogManager`**

  - `open_links_dialog` method:
    - Line 247: `dialog.setWindowTitle("Help / Links and Guides")`
    - Line 251: `QtWidgets.QLabel("Helpful Links & Guides")`
    - Line 258: `QtWidgets.QGroupBox("Click a link to open in your browser")`
    - The visible text in the `QLabel` HTML links (e.g., `"GLM-4.5"`, `"AI Coding on a Budget"`, etc.).
  - `_handle_bug_report_reply` method:
    - Line 289, in `QMessageBox.information`: The title `"Thank you"` and the message `"Your feedback/complaint was submitted successfully."`.
    - Line 293, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"Submission failed: "`.
    - Line 296, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"Could not process feedback response: "`.
  - `_handle_email_submit_reply` method:
    - Line 304, in `QMessageBox.information`: The title `"Thank you"` and the message `"Your email was submitted successfully."`.
    - Line 308, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"Submission failed: "`.
    - Line 311, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"Could not process email response: "`.
  - `open_complain_dialog` method (within nested `FeedbackDialog`):
    - Line 318: `self.setWindowTitle("Send Ideas, bugs, thoughts!")`
    - Line 321: `QtWidgets.QLabel("Your Email (required):")`
    - Line 324: `self.email_input.setPlaceholderText("you@example.com (required)")`
    - Line 327: `QtWidgets.QLabel("Message (required):")`
    - Line 330: `self.msg_input.setPlaceholderText("Describe your idea, bug, or thought here... (required)")`
  - `open_complain_dialog` method (continued):
    - Line 349, in `QMessageBox.warning`: The title `"Error"` and the message `"Email and message are both required."`.
    - Line 377, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"Could not submit feedback: "`.
  - `open_about_dialog` method:
    - The visible text within the `html` string (near line 386): `"aicodeprep-gui"`, `"Installed version: "`, `"Installed "`, `" days ago."`, `"GitHub Sponsors"`, `"AI Code Prep Homepage"`.
    - Line 400: `dlg.setWindowTitle("About aicodeprep-gui")`
  - `add_new_preset_dialog` method:
    - Line 408, in `QInputDialog.getText`: The title `"New preset"` and the label `"Button label:"`.
    - Line 414: `dlg.setWindowTitle("Preset text")`
    - Line 417: `QtWidgets.QLabel("Enter the preset text:")`
    - Line 432, in `QMessageBox.warning`: The title `"Error"` and the message `"Preset text cannot be empty."`.
    - Line 439: The `error_msg` string `"Failed to save preset '{lbl.strip()}'. Check settings permissions and disk space."`
    - Line 441, in `QMessageBox.warning`: The title `"Error"`.
    - Line 445: The `error_msg` string `"Failed to import preset settings module: {e}. Module path may be incorrect."`
    - Line 447, in `QMessageBox.critical`: The title `"Import Error"`.
    - Line 450: The `error_msg` string `"Unexpected error while adding preset: {e}"`
    - Line 452, in `QMessageBox.critical`: The title `"Error"`.
  - `delete_preset_dialog` method:
    - Line 461, in `QMessageBox.information`: The title `"No Presets"` and the message `"There are no presets to delete."`.
    - Line 467, in `QInputDialog.getItem`: The title `"Delete Preset"` and the label `"Select a preset to delete:"`.
    - Line 486: The `error_msg` string `"Could not find the corresponding button for preset '{label_to_delete}'. The UI might be out of sync with stored presets."`
    - Line 488, in `QMessageBox.warning`: The title `"Error"`.
    - Line 492: The `error_msg` string `"Failed to import preset settings module: {e}. Module path may be incorrect."`
    - Line 494, in `QMessageBox.critical`: The title `"Import Error"`.
    - Line 497: The `error_msg` string `"Unexpected error while deleting preset: {e}"`
    - Line 499, in `QMessageBox.critical`: The title `"Error"`.

- **Class `ActivateProDialog`**
  - `setup_ui` method:
    - Line 522: `self.setWindowTitle("Activate Pro License")`
    - Line 524: `QtWidgets.QLabel("Enter your Gumroad license key to activate Pro features:")`
    - Line 527: The visible text in the HTML link: `"Buy a Lifetime Pro License"`.
    - Line 531: `self.license_key_input.setPlaceholderText("XXXX-XXXX-XXXX")`
    - Line 535: `QtWidgets.QPushButton("Activate")`
    - Line 538: `QtWidgets.QPushButton("Cancel")`
  - `on_activate` method:
    - Line 544, in `QMessageBox.warning`: The title `"Error"` and the message `"Please enter a license key."`.
    - Line 548, in `QMessageBox.critical`: The title `"Error"` and the message `"Product IDs are not set."`.
    - Line 551: `self.status_label.setText("Verifying license…")`
  - `send_request` method:
    - Line 577: `self.status_label.setText("Invalid license key for all product IDs.")`
  - `on_reply` method:
    - Line 591, in `QMessageBox.warning`: The title `"Activation Limit Exceeded"` and the message `"License key has been activated {uses} times. Only 2 activations are allowed. Please purchase a new license for additional installs."`.
    - Line 615, in `QMessageBox.warning`: The title `"Warning"` and the message prefix `"Activated but failed to save license information: "`.
    - Line 618, in `QMessageBox.information`: The title `"Success"` and the message `"License verified! Please restart the app to enter Pro mode."`.
    - Line 628: `self.status_label.setText("Trying alternative product ID...")`
    - Line 635: The default `err_msg` string `"Invalid or refunded license key."`.
    - Line 637, in `QMessageBox.warning`: The title `"Activation Failed"`.
    - Line 649: The `status_label` text prefix `"Network error ({err}). Retrying in {delay//1000}s…"`.
    - Line 655: `self.status_label.setText("Trying alternative product ID...")`
    - Line 661, in `QMessageBox.critical`: The title `"Error"` and the message `"Could not reach the license server after multiple attempts.\nPlease try again later or contact support."`.

### 2. `aicodeprep_gui/gui/components/installer_dialogs.py`

- **Class `RegistryManagerDialog`**

  - `__init__` method:
    - Line 12: `self.setWindowTitle("Windows Context Menu Manager")`
    - Line 17: The `info_text` HTML string.
    - Line 25: `QtWidgets.QLabel("Custom menu text:")`
    - Line 29: `self.menu_text_input.setPlaceholderText("Open with aicodeprep-gui")`
    - Line 30: `self.menu_text_input.setText("Open with aicodeprep-gui")`
    - Line 31: `self.menu_text_input.setToolTip("Enter the text that will appear in the right-click context menu")`
    - Line 36: `QtWidgets.QCheckBox("Enable Classic Right-Click Menu (for Windows 11)")`
    - Line 39: `classic_help.setToolTip("Restores the full right-click menu in Windows 11, so you don't have to click 'Show more options' to see this app's menu item.")`
    - Line 47: `self.status_label.setText("Ready.")`
    - Line 50: `QtWidgets.QPushButton("Install Right-Click Menu")`
    - Line 54: `QtWidgets.QPushButton("Uninstall Right-Click Menu")`
  - `_run_action` method:
    - Line 81, in `QMessageBox.information`: The title `"Success"`.
    - Line 83, in `QMessageBox.warning`: The title `"Error"`.
    - Line 104, in `QMessageBox.critical`: The title `"Error"` and the message `"Windows registry module not available."`.
    - Line 107, in `QMessageBox.critical`: The title `"Error"` and the message prefix `"An error occurred: "`.

- **Class `MacInstallerDialog`**

  - `__init__` method:
    - Line 121: `self.setWindowTitle("macOS Quick Action Manager")`
    - Line 125: The `info_text` HTML string.
    - Line 133: `QtWidgets.QPushButton("Install Quick Action")`
    - Line 136: `QtWidgets.QPushButton("Uninstall Quick Action")`
  - `run_install` & `run_uninstall` methods:
    - In both methods, the `QMessageBox` titles `"Success"`, `"Error"`, and messages `"macOS installer module not available."` and `"An error occurred: {e}"` need translation.

- **Class `LinuxInstallerDialog`**
  - `__init__` method:
    - Line 177: `self.setWindowTitle("Linux File Manager Integration")`
    - Line 183: `self.tabs.addTab(..., "Automated Setup")`
    - Line 186: `QtWidgets.QLabel("This tool can attempt to install a context menu script for your file manager.")`
    - Line 191: `QtWidgets.QGroupBox("Nautilus (GNOME, Cinnamon, etc.)")`
    - Line 195: `QtWidgets.QPushButton("Install Nautilus Script")`
    - Line 198: `QtWidgets.QPushButton("Uninstall Nautilus Script")`
    - Line 209: `self.nautilus_group.setToolTip("Nautilus file manager not detected in your system's PATH.")`
    - Line 212: `self.nautilus_group.setToolTip("Linux installer module not available.")`
    - Line 216: `self.tabs.addTab(..., "Manual Instructions")`
    - Line 219: The `manual_text` string for the `QLabel`.
    - Line 229: The fallback string `"# Linux installer module not available"`.
  - `run_install_nautilus` & `run_uninstall_nautilus` methods:
    - In both methods, the `QMessageBox` titles `"Success"`, `"Error"`, and messages `"Linux installer module not available."` and `"An error occurred: {e}"` need translation.

### 3. `aicodeprep_gui/gui/components/multi_state_level_delegate.py`

- Line 4: The `ImportError` message: `"MultiStateLevelDelegate has moved to aicodeprep_gui/pro/multi_state_level_delegate.py"`

### 4. `aicodeprep_gui/gui/components/preset_buttons.py`

- **Class `PresetButtonManager`**
  - `_add_preset_button` method:
    - Line 20: The tooltip prefix `"Global preset: "`.
    - Line 22: The tooltip prefix `"Preset: "`.
  - `_delete_preset` method:
    - Line 26, in `QMessageBox.question`: The title `"Delete Preset"` and the message `"Are you sure you want to delete the preset '{label}'?"`.
    - Line 29, in `QMessageBox.warning`: The title `"Error"` and the message `"Failed to delete global preset '{label}'"`.

### 5. `aicodeprep_gui/gui/settings/preferences.py`

- **Class `PreferencesManager`**
  - `load_from_prefs_button_clicked` method:
    - Line 223: The `setText` message prefix `"Loaded selection from "`.
    - Line 226: The `setText` message `"No preferences file found (.aicodeprep-gui)"`.

### 6. `aicodeprep_gui/gui/settings/presets.py`

- `DEFAULT_PRESETS` list (near line 6): Each string in the tuples needs to be translated.
  - `("Debug", "Can you help me debug this code?")`
  - `("Security check", "Can you analyze this code for any security issues?")`
  - `("Agent Prompt", "Write a prompt for my AI coding agent...")`
  - `("Best Practices", "Please analyze this code for: Error handling...")`
  - `("Please review for", "Code quality and adherence to best practices...")`
  - `("Cline, Roo Code Prompt", "Write a prompt for Cline, an AI coding agent...")`

### 7. `aicodeprep_gui/gui/main_window.py`

- **Class `FileSelectionGUI`**
  - `__init__` method:
    - Line 144: `self.setWindowTitle("aicodeprep-gui - File Selection")`
    - Menu items: `"&File"`, `"Install Right-Click Menu..."`, `"Install Finder Quick Action..."`, `"Install File Manager Action..."`, `"&Quit"`, `"&Edit"`, `"&New Preset…`, `"Open Settings Folder…`, `"&Help"`, `"Help / Links and Guides"`, `"&About"`, `"Send Ideas, bugs, thoughts!"`, `"Activate Pro…`.
    - Line 293: `"XML <code>"`, `"Markdown ###"` in `addItems`.
    - Line 302: `QtWidgets.QLabel("&Output format:")`
    - Line 305: `QtWidgets.QCheckBox("Dark mode")`
    - Line 309: `QtWidgets.QLabel("Estimated tokens: 0")`
    - Line 312: `QtWidgets.QLabel("AI Code Prep GUI")`
    - Line 339: The long HTML string for `info_label`.
    - Line 349: `QtWidgets.QLabel("Prompt Preset Buttons:")`
    - Line 365: `add_preset_btn.setToolTip("New Preset…")`
    - Line 370: `delete_preset_btn.setToolTip("Delete a preset…")`
    - Line 378: `QtWidgets.QLabel("Presets help you save more time and will be saved for later use")`
    - Line 389: `self.tree_widget.setHeaderLabels(["File/Folder", "Skeleton Level"])`
    - Line 414: `QtWidgets.QLabel("Optional prompt/question for LLM (will be appended to the end):")`
    - Line 418: `self.prompt_textbox.setPlaceholderText("Type your question or prompt here (optional)…")`
    - Line 422: `QtWidgets.QPushButton("Clear")`
    - Line 423: `self.clear_prompt_btn.setToolTip("Clear the prompt box")`
    - Line 501: `QtWidgets.QCheckBox("Remember checked files for this folder, window size information")`
    - Line 505: `QtWidgets.QCheckBox("Add prompt/question to top")`
    - Line 507: `QtWidgets.QCheckBox("Add prompt/question to bottom")`
    - Line 516: `QtWidgets.QGroupBox("Options")`
    - Line 532: `remember_help.setToolTip("Saves which files are included in the context for this folder, so you don't have to keep doing it over and over")`
    - Line 544: `QtWidgets.QLabel("Font Size:")`
    - Line 566: `QtWidgets.QLabel("Pro Features")`
    - Line 571: The link text `Buy Pro Lifetime License`.
    - Line 584: `QtWidgets.QCheckBox("Enable file preview window")`
    - Line 587: `preview_help.setToolTip("Shows a docked window on the right that previews file contents when you select them in the tree")`
    - Line 598: `QtWidgets.QCheckBox("Enable syntax highlighting in preview")`
    - Line 601: `syntax_highlight_help.setToolTip("Apply syntax highlighting to code in the preview window")`
    - Line 625: `QtWidgets.QLabel("Font Weight:")`
    - Line 633: `font_weight_help.setToolTip("Adjust font weight for preview window")`
    - Line 646: The checkbox text `"Add prompt/question to top - Adding to top AND bottom often gets better responses from AI models"`.
    - Line 647: The checkbox text `"Add prompt/question to bottom - Adding to top AND bottom often gets better responses from AI models"`.
    - Line 653: The tooltip for `prompt_top_help`.
    - Line 664: The tooltip for `prompt_bottom_help`.
    - Line 690: `self.preview_toggle.setToolTip("Show docked preview of selected files")`
    - Line 703: `self.syntax_highlight_toggle.setToolTip("Apply syntax highlighting to code in the preview window")`
    - Line 708: `self.preview_toggle.setToolTip("Enable file preview window (Pro Feature)")`
    - Line 713: `self.syntax_highlight_toggle.setToolTip("Enable syntax highlighting (Pro Feature)")`
    - Line 724: `QtWidgets.QCheckBox("Enable Context Compression Modes - does not work yet, still experimenting!")`
    - Line 727 & 734: The tooltip `"Show a second column that marks skeleton level per item"`.
    - Line 738: `self.pro_level_toggle.setToolTip("Pro Feature")`
    - Line 751: `QtWidgets.QPushButton("GENERATE CONTEXT!")`
    - Line 755: `QtWidgets.QPushButton("Select All")`
    - Line 759: `QtWidgets.QPushButton("Deselect All")`
    - Line 763: `QtWidgets.QPushButton("Load preferences")`
    - Line 767: `QtWidgets.QPushButton("Quit")`
  - `process_selected` method:
    - Line 1262: The message `"Large content ({content_size_mb:.1f}MB) may exceed clipboard limits. Saved to fullcode.txt."`
    - Line 1271: The message `"Warning: Clipboard copy may have failed. Content saved to fullcode.txt"`
    - Line 1278: The message `"Copied to clipboard and fullcode.txt"`
    - Line 1285: The message prefix `"Clipboard error: {str(e)}. Content saved to fullcode.txt"`
  - `update_token_counter` method:
    - Line 1313: The message prefix `"Estimated tokens: "`.

### 8. `aicodeprep_gui/pro/multi_state_level_delegate.py`

- `LEVEL_LABELS` list (near line 15):
  - `"   "`
  - `"path/to/fileName.only"`
  - `"Skeleton (partial)"`
  - `"Full File Contents"`

### 9. `aicodeprep_gui/pro/preview_window.py`

- **Class `FilePreviewDock`**
  - `__init__` method:
    - Line 11: The window title `"File Preview"`.
  - `set_dark_mode` method:
    - Line 68: The message prefix `"Theme update error: "`.
  - `preview_file` method:
    - Line 92: The message suffix `"\n\n... [Content truncated]"`.
    - Line 98: The status label prefix `"Preview: "`.
    - Line 104: The status label prefix `"Preview: "` and suffix `"(plain text)"`.
    - Line 107: The message prefix `"Error loading file: "`.
    - Line 108: `self.status_label.setText("Error")`
  - `show_binary_warning` method:
    - Line 113: The multi-line message `"[Binary file - contents not shown]\n\nFile: {os.path.basename(file_path)}\nSize: {os.path.getsize(file_path):,} bytes"`.
    - Line 117: `self.status_label.setText("Binary file")`
  - `clear_preview` method:
    - Line 122: `self.status_label.setText("Select a file to preview")`

### 10. `aicodeprep_gui/linux_installer.py`

- `SCRIPT_NAME` constant (near line 6): `"Open with aicodeprep-gui"`
- `NAUTILUS_SCRIPT_CONTENT` constant (near line 9): The `zenity` error message strings need translation.
  - `"<b>aicodeprep-gui command not found.</b>\\n\\nPlease ensure it's installed and accessible from your terminal's PATH."`
  - `"Please select a directory to use this script."`
- `install_nautilus_script` & `uninstall_nautilus_script` methods: All returned message strings (e.g., `"Nautilus file manager not found."`, `"Nautilus script ... installed successfully..."`, `"Nautilus script not found (already uninstalled)."`) need to be translated.

### 11. `aicodeprep_gui/macos_installer.py`

- `install_quick_action` & `uninstall_quick_action` methods: All returned message strings (e.g., `"The installer ... has been placed on your Desktop..."`, `"Error: Could not find the installer..."`, `"Quick Action ... has been uninstalled."`) need to be translated.

### 12. `aicodeprep_gui/main.py`

- `main` function:
  - Line 19: The console message `"All aicodeprep-gui user settings deleted."`.
  - `argparse` descriptions and help messages (near lines 45-59): all `description` and `help` string values.
  - Line 79-80: The console messages `"Pro feature --skipui: Please enable Pro mode."` and `"Check out https://wuu73.org/aicp for more info."`.
  - Line 187: The console message `"Running privileged action: Install context menu..."`.
  - Line 193: The console message `"Running privileged action: Remove context menu..."`.
  - Line 241: The console message `"Buy my cat a treat, comments, ideas for improvement appreciated: "`.

### 13. `aicodeprep_gui/windows_registry.py`

- All functions: All returned message strings (e.g., `"Classic context menu enabled."`, `"This feature is only for Windows."`, `"UAC prompt initiated. The application will close."`, `"Administrator rights required."`, `"Context menu installed successfully..."`) and `print()` statements need to be translated.
