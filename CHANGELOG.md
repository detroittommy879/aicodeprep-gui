# 📦 Changelog

---

## [1.2.3] - 2025-10-15

Added Flow Studio

## [1.2.0] - 2025-08-26

### ✨ New Features

- **Syntax Highlighting in Preview Window**: Added syntax highlighting for the file preview window (Pro feature). Supports a wide range of programming languages with proper color schemes for both light and dark modes.
- **Font Weight Control**: Added a slider in the Pro features section to adjust the font weight in the preview window, providing better readability customization.
- **Improved Workflow**: The application now remains open after generating context, allowing for iterative refinement of file selections and prompts without having to relaunch the application.

### 🔄 Changed

- **Generate Context Behavior**: Clicking "GENERATE CONTEXT!" no longer quits the application, providing a more seamless workflow for making adjustments and regenerating context as needed.
- **Preview Window Enhancements**: Improved the preview window with better font handling, syntax highlighting capabilities, and theme synchronization.

### 🛠️ Technical Improvements

- **Syntax Highlighting Implementation**: Integrated Pygments library for robust syntax highlighting in the preview window.
- **UI Responsiveness**: Enhanced the application's responsiveness when generating and managing large code contexts.
- **Font Management**: Added Font Size slider for users who wanted bigger fonts

## [1.0.6] - 2025-07-01

### 🐛 Fixed

- **macOS Finder Integration**: Updated Quick Action installation method to extract the workflow ZIP to the Desktop for manual installation, resolving permission and compatibility issues.
- **Update Checker**: Improved thread cleanup and signal handling to prevent rare crashes during background checks.
- **GUI Stability**: Fixed minor issues with resource path handling in themes, telemetry pings, and menu item rendering.
- **Installer Scripts**: Enhanced error handling and logging in macOS/Windows/Linux installers for better user feedback.
- **General Bug Fixes**: Addressed various edge cases in file processing, prompt saving, and cross-platform compatibility.

### 🔄 Changed

- **Version Bump**: Internal version updated to 1.0.6 with minor optimizations for faster startup and reduced memory usage.

## [1.0.3] - 2025-06-22

### ✨ New Features

- **Native OS Context Menu Installers:**
  - Added a `File` menu option to easily install a right-click context menu for your operating system's file manager.
  - **Windows:** "Install Right-Click Menu" dialog with options for custom menu text and enabling/disabling the classic (full) context menu for Windows 11.
  - **macOS:** "Install Finder Quick Action" to add an "Open with aicodeprep-gui" action to Finder.
  - **Linux:** "Install File Manager Action" for automated installation of a Nautilus (GNOME/Cinnamon) script, with manual instructions for other file managers.
- **Automatic Update Checker:**
  - The application now non-intrusively checks for new versions on PyPI upon startup.
  - If an update is available, a dialog will appear offering a one-click upgrade option.
- **"About" Dialog:**
  - Added a new "Help" -> "About" menu that displays the current version, update status, and how long the app has been installed.

### 🔄 Changed

- **Improved Documentation:**
  - Complete overhaul of `README.md` with a more professional tone, clearer installation instructions (recommending `pipx`), and better feature descriptions.
- **Windows Integration:**
  - The application now sets a Windows AppUserModelID for a proper, consistent taskbar icon.

### 🛠️ Technical Improvements

- **New Dependencies:** Added `requests` and `packaging` to support the new update checker.
- **New Modules:** Added `windows_registry.py`, `macos_installer.py`, `linux_installer.py`, and `update_checker.py` to modularize the new installer and update-checking logic.
- **Anonymous Telemetry:** A basic, one-way anonymous ping is sent on startup to help estimate the number of active users. This sends no personal data or code. See `PRIVACY.md` for details.

## [1.0.0] - 2025-06-20

### 🎉 Major Release - Production Ready

#### ✨ New Features

- **Enhanced Global Preset System:**

  - Global preset management using QSettings for cross-project persistence
  - Default presets: "Debug", "Security check", "Best Practices", "Please review for"
  - New ✚ and 🗑️ buttons for easy preset creation and deletion
  - Presets automatically available across all project folders
  - Improved preset UI with scrollable horizontal layout

- **Improved File Tree Experience:**

  - Enhanced tree building logic with better performance
  - Smart auto-expansion of folders containing checked files
  - Better visual feedback with hover effects on checkboxes
  - Cleaner, more intuitive folder navigation
  - Improved checkbox styling using permanent image files

- **Enhanced Output Options:**

  - Choose between XML `<code>` tags or Markdown `###` formatting via dropdown
  - Optional prompt/question text appended to output
  - Intelligent file processing with better error handling
  - Support for custom prompts with preset integration

- **Robust Configuration System:**
  - Mature TOML configuration with comprehensive default settings
  - User overrides via `aicodeprep-gui.toml` in project directories
  - `.gitignore`-style pattern matching using pathspec library
  - Extensive default exclusion patterns for common build artifacts

#### 🔄 Changed

- **Performance Improvements:**

  - Optimized file tree population with lazy loading
  - Faster initial startup times
  - Reduced memory usage during file scanning
  - More responsive UI interactions

- **User Experience Enhancements:**

  - Improved menu bar with File and Edit menus
  - Better error messages and descriptive logging
  - Enhanced drag-and-drop folder support
  - Cleaner visual design with better spacing and fonts

- **File Handling:**
  - Better binary file detection and exclusion
  - Improved relative path handling
  - Enhanced file size limits and validation
  - More robust error handling for file operations

#### 🛠️ Technical Improvements

- **Code Architecture:**

  - Comprehensive refactoring for maintainability
  - Better separation of concerns between modules
  - Improved error handling throughout the application
  - Enhanced logging with descriptive error messages

- **Dependencies:**
  - Streamlined dependency list: PySide6, toml, pathspec
  - Removed unused dependencies for cleaner installation
  - Better cross-platform compatibility

---

## [0.9.8] - 2025-06-18

### 🚀 Major Refactoring: TOML Configuration & Lazy Loading

#### ✨ New Features

- **TOML Configuration System:**

  - Replaced custom Markdown configuration with industry-standard TOML format
  - New `default_config.toml` file with comprehensive configuration options
  - Support for user-specific configuration via `aicodeprep-gui.toml` in working directory
  - `.gitignore`-style pattern matching using `pathspec` library for robust file exclusion

- **Lazy Loading File Tree:**

  - Implemented lazy loading for excluded directories (like `node_modules`, `venv`, etc.)
  - Extremely fast initial startup by avoiding scanning large excluded directories
  - On-demand expansion of any directory for fine-grained file selection
  - Users can now manually expand and select specific files from previously excluded directories

- **Enhanced Pattern Matching:**
  - All file and directory exclusion now uses `.gitignore`-style patterns
  - More powerful and standardized exclusion rules
  - Unified inclusion/exclusion lists for better organization

#### 🔄 Changed

- **Dependencies:**

  - Added `toml` for configuration parsing
  - Added `pathspec` for `.gitignore`-style pattern matching
  - Removed `tiktoken` dependency (no longer used)

- **Configuration Format:**

  - Migrated from `config.md` to `default_config.toml`
  - More structured and maintainable configuration system
  - Better support for complex exclusion patterns

- **Performance Improvements:**
  - Significantly faster startup times due to lazy loading
  - Reduced memory usage during initial file scanning
  - More responsive UI when working with large codebases

#### 🛠️ Technical Improvements

- **Code Architecture:**

  - Complete rewrite of `smart_logic.py` for better performance and maintainability
  - Improved GUI tree building logic with lazy loading support
  - Enhanced checkbox styling using Unicode characters instead of temporary files
  - Better error handling and descriptive error messages for debugging

- **File Processing:**
  - More efficient directory traversal with intelligent pruning
  - Better binary file detection and handling
  - Improved pathspec-based filtering throughout the application

---

## [0.9.7] - 2025-04-28

### ✨ New Features

- **Output Format Selection:**

  - Added dropdown menu to select output format for `fullcode.txt`
  - Options: "XML <code>" (uses `<code>...</code>` tags) or "Markdown ###" (uses `### File Path` ... `### END File Path`)

- **Prompt Presets:**

  - Users can create, save, and quickly apply preset text snippets to the LLM prompt box
  - Added "Edit" → "New Preset..." menu option and "✚" button for easy creation
  - Presets saved per-folder in `.aicodeprep` preferences file

- **Enhanced Configuration System:**

  - Default configuration loaded from `aicodeprep_gui_c/data/config.md`
  - User-specific overrides via `aicodeprep_config.md` file in working directory

- **UI & UX Improvements:**

  - Native QMainWindow menu bar ("File" → "Quit", "Edit" → "New Preset...")
  - Binary files automatically detected, greyed out, and made unselectable
  - Improved checkbox styling with programmatically generated checkmark images
  - Vertical splitter state now saved and restored via `.aicodeprep` file
  - Application style set to "Fusion" for consistent rendering

- **File & Directory Handling:**
  - Enhanced logic to skip excluded directories during initial file collection
  - Files and folders starting with dots (e.g., `.vscode`, `.idea`) skipped by default
  - Glob-style pattern matching for exclusions via `fnmatch`

### 🔄 Changed

- **Token Counting:**

  - Simplified character-based approximation (`total_chars / 4`)
  - Removed direct runtime dependency on `tiktoken` for GUI token counting

- **Preferences File:**
  - `.aicodeprep` now stores splitter state and prompt presets
  - Enhanced preference management system

### 🐛 Fixed

- Binary files can no longer be accidentally selected
- More robust directory exclusion logic

---

## [0.9.6] - 2025-05-27

### ✨ New Features

- **Dark Mode Support:**
  - Automatic theme detection based on system preferences
  - Manual dark/light mode toggle in top-right corner
  - Carefully designed dark theme palette for optimal readability

### 🔄 Changed

- **PySide6 Migration:**
  - Upgraded from PyQt5 to PySide6 for improved performance
  - Better Qt6 features and future-proofing
  - Simplified dependencies

---

## [0.9.5] - 2025-01-24

### 🎉 Added

- **macOS Support:**
  - Native macOS app bundle
  - Finder workflow integration for right-click Quick Actions
  - Tested on macOS Ventura 13.4+ (M1+)

---

## [0.5.0] - 2024-11-14

### 🎉 Added

- **Windows GUI Version:**
  - Cross-platform Qt-based GUI application
  - Right-click context menu integration for Windows Explorer
  - Enhanced file selection with granular inclusion/exclusion
  - DPI awareness for high-resolution displays

### ✨ New Features

- Interactive file selection before code preparation
- Checkbox-based file inclusion/exclusion
- Scalable UI with multiple theme options
- Windows Explorer context menu integration

### 🔄 Changed

- Enhanced configuration options
- Improved logging and error handling

---

## [0.2.2] - 2024-11-02

### 🛠️ Improvements

- Minor tweaks and bug fixes
- Performance optimizations

---

## [0.2.0] - 2024-02-11

### 🔧 Configuration Overhaul

- Moved all hard-coded options to `default_config.yaml` file

### 🎉 Added

- **New Configuration Options:**
  - `exclude_extensions` for global file type exclusion
  - `exclude_patterns` for pattern-based exclusions (e.g., `.min.js`)
  - `include_dirs` for explicit directory inclusion
  - Enhanced priority system for inclusion/exclusion rules
  - Better support for user configuration overrides

### 🔄 Changed

- **Improved Processing Logic:**
  - Clear priority rules for file inclusion/exclusion:
    1. Explicitly included files (highest priority)
    2. Explicitly excluded files
    3. Excluded extensions
    4. Code extensions (lowest priority)
  - Enhanced directory processing with priority-based logic
  - Updated exclusion patterns based on real-world usage
