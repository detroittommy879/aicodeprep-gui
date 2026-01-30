# AGENTS.md

This file is a durable handoff for any agent working in this repo.

- Always use `uv` for Python commands in this repo.
- Prefer updating both this file and CLAUDE.md when you learn something that a future agent would otherwise need the user to repeat.

## Maintaining This File

- If you discover a new “gotcha” (env var needed, a test that hangs, a required compile step, a script location), add it here.
- Keep notes command-first and loop-friendly (so the next agent can run/verify quickly).

## Agent Operational Notes

### Package manager / running

- Run app: `uv run aicodeprep-gui`
- Run tests: `uv run pytest`

### GUI automation for agents (screenshots, loops, no manual closing)

This repo includes custom test infrastructure that allows agents to open the GUI, take screenshots, and reliably close windows during tests.

Key pieces:

- Environment variables used for tests:
  - `AICODEPREP_TEST_MODE=1` (set by pytest config)
  - `AICODEPREP_NO_METRICS=1` (set by pytest config)
  - `AICODEPREP_NO_UPDATES=1` (set by pytest config)
  - `AICODEPREP_AUTO_CLOSE=1` (optional; auto-closes test windows after ~10 seconds)

- Pytest configuration:
  - `tests/conftest.py` sets test-mode env vars early and handles Qt window cleanup between tests.

- Screenshot helpers:
  - `aicodeprep_gui/utils/screenshot_helper.py`
    - Screenshot output dir: `screenshots/test_captures/`
    - Useful functions: `capture_window_screenshot`, `capture_widget_screenshot`, `compare_screenshots`, `get_text_color_contrast`

- UI launch + screenshot harness:
  - `tests/test_helpers/screenshot_tester.py`
    - `ScreenshotTester.launch_and_capture()` opens the main window, processes events, optionally starts an auto-close timer, then captures a screenshot.

- Baseline screenshot test:
  - `uv run pytest tests/test_screenshot_baseline.py -v`

### Internationalization (i18n) and Accessibility (a11y)

**For all translation, language, and accessibility work, see [AGENTS_intl.md](AGENTS_intl.md)**

That file contains detailed workflows for:

- Adding/updating translations (`.ts` -> `.qm` compilation)
- Testing language switching with screenshots
- Adding new UI elements that need translation
- Troubleshooting translation issues
- Accessibility implementation guidance

Consult AGENTS_intl.md when you need to:

- Wrap new UI strings in `self.tr()`
- Complete translations for a language
- Test visual appearance across locales
- Work on keyboard navigation or screen reader support

## CLAUDE.md (Reference Copy)

The content below mirrors CLAUDE.md. If you update CLAUDE.md with new agent-relevant information, consider updating this section too.

---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Quick Start (Read This First)

### Package Manager / Running Python

- Always use `uv` for Python commands in this repo.
- Examples:
  - Run app: `uv run aicodeprep-gui`
  - Run tests: `uv run pytest`
  - Run one test: `uv run pytest tests/test_i18n.py -q`

### GUI Test Automation (No Manual Window Closing)

This repo includes custom helpers so agents can open/close the GUI repeatedly, take screenshots, and verify i18n/a11y without needing a human to babysit windows.

- Test mode env vars (set by tests automatically in `tests/conftest.py`):
  - `AICODEPREP_TEST_MODE=1` (disables features that make tests flaky)
  - `AICODEPREP_NO_METRICS=1`
  - `AICODEPREP_NO_UPDATES=1`
- Optional auto-close for screenshot loops:
  - `AICODEPREP_AUTO_CLOSE=1` (see `tests/test_helpers/screenshot_tester.py`; closes after ~10s)
- Screenshot helpers:
  - `aicodeprep_gui/utils/screenshot_helper.py` saves to `screenshots/test_captures/`
  - `tests/test_helpers/screenshot_tester.py` provides `ScreenshotTester.launch_and_capture()`
- Baseline screenshot test:
  - `uv run pytest tests/test_screenshot_baseline.py -v`

### Translations (i18n): .ts -> .qm compilation

**For detailed i18n workflows, see [AGENTS_intl.md](AGENTS_intl.md)**

Quick reference:

- Translation files: `aicodeprep_gui/i18n/translations/`
- Complete translations: Japanese (ja), Hindi (hi) - use as templates
- Compile after editing: `uv run python scripts/compile_translations.py`
- Test language: `uv run aicodeprep-gui --language es`

## Project Overview

This repository contains **aicodeprep-gui**, a smart GUI application for context engineering - preparing and sharing project code with AI models. The tool allows users to select, filter, and bundle code files for LLM analysis, solving the problem of manually copying code into AI chatbots.

### Core Philosophy

"You know your code best" - Instead of letting IDE agents guess which files are relevant, this tool puts users in control with a smart, intuitive UI.

## Architecture

### Main Application (`aicodeprep_gui/`)

**Technology Stack:**

- Python 3.8+
- PySide6 for cross-platform GUI (Windows, macOS, Linux)
- TOML for configuration
- NodeGraphQt for Flow Studio (Pro feature)
- LiteLLM for LLM integration

**Key Components:**

1. **Entry Point** (`aicodeprep_gui/main.py`):
   - CLI argument parsing
   - Headless mode support (`--skipui`)
   - Configuration directory setup (`~/.aicodeprep-gui/`)

2. **GUI Module** (`aicodeprep_gui/gui/`):
   - `main_window.py` - Main GUI window (87KB+)
   - `components/` - UI components
   - `handlers/` - Event handlers
   - `settings/` - Configuration UI
   - `utils/` - GUI utilities

3. **Pro Features** (`aicodeprep_gui/pro/`):
   - `flow/` - Flow Studio for multi-LLM workflows
   - `llm/` - LLM integration
   - `syntax_highlighter.py` - Code syntax highlighting
   - `preview_window.py` - File preview with syntax highlighting

4. **Configuration** (`aicodeprep_gui/config.py`):
   - Manages `~/.aicodeprep-gui/` directory
   - API key storage (`api-keys.toml`)
   - Flow templates management
   - Copy built-in flows on startup

5. **Core Logic**:
   - `file_processor.py` - File collection and processing
   - `smart_logic.py` - Intelligent file selection
   - `apptheme.py` - UI theming and styling

### Flow Studio (Pro Feature)

The Flow Studio enables "Send to 5 LLMs" functionality using a visual node-based interface:

- **Template Location**: `aicodeprep_gui/data/flow_*.json`
- **Flow Templates**:
  - `flow.json` - Default flow
  - `flow_best_of_3.json` - Best-of-3 configuration
- **Node Types**: LLM nodes, aggregation nodes, I/O nodes
- **Dynamic Slots**: Configurable 1-10 candidate slots (see `BESTOFN_COMPLETE_SOLUTION.md`)
- **Execution Engine**: Async parallel LLM orchestration

## Common Commands

### Main Application

```bash
# Install (see README.md for platform-specific instructions)
pipx install aicodeprep-gui

# Run GUI in current directory
aicp

# Run GUI in specific directory
aicp /path/to/project

# Run with no clipboard copy
aicp --no-copy

# Skip UI (Pro feature, headless mode)
aicp --skipui "your prompt here"

# Debug mode
aicp --debug

# Show help
aicp --help

# Delete user settings
aicp --delset
```

### Development

```bash
# Install for development
pip install -e .

# Run tests (if pytest is configured)
python -m pytest

# Build distribution
python -m build

# Install with Pro features enabled
aicp --pro
```

## Configuration

### User Configuration Directory

`~/.aicodeprep-gui/`

**Files:**

- `api-keys.toml` - API keys for LLM providers
- `flows/` - Flow templates (copied from `aicodeprep_gui/data/`)
- QSettings for UI preferences

### Project Configuration

Create `aicodeprep-gui.toml` in project root:

```toml
max_file_size = 2000000
code_extensions = [".py", ".js", ".ts", ".html", ".css", ".rs"]
exclude_patterns = ["build/", "dist/", "*.log", "temp_*", "cache/"]
default_include_patterns = ["README.md", "main.py", "docs/architecture.md"]
```

### Default Configuration

See `aicodeprep_gui/data/default_config.toml` for all settings.

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8
- **GUI**: Use PySide6 patterns, respect dark/light mode themes
- **Pro Features**: Check `pro.enabled` before showing Pro-only UI

### Pro Feature Development

1. Feature goes in `aicodeprep_gui/pro/`
2. Expose via `aicodeprep_gui/pro/__init__.py`
3. Connect in `gui/main_window.py` under "Premium Features" panel
4. Check `pro.enabled` before enabling feature
5. See `.clinerules` for detailed patterns

### Flow Studio Development

- Flow templates use NodeGraphQt JSON format
- Templates stored in `aicodeprep_gui/data/flow_*.json`
- Node types: `llm`, `aggregate`, `input`, `output`
- Dynamic slots implemented via `num_candidates` property (1-10 range)

### Platform-Specific Code

- **Windows**: Registry manipulation in `windows_registry.py`
- **macOS**: Quick Actions in `macos_installer.py`
- **Linux**: Nautilus scripts in `linux_installer.py`

## Key Features

### Free Features

- Smart file selection with `.gitignore`-style patterns
- Cross-platform GUI (PySide6)
- Token counter
- Prompt presets
- Right-click context menu integration
- Per-project state persistence

### Pro Features

- File preview with syntax highlighting (Pygments)
- Font customization
- Flow Studio (visual multi-LLM workflows)
- Headless mode (`--skipui`)
- Context compression (planned)

## File Structure

```
aicodeprep_gui/
├── __init__.py
├── main.py                  # Entry point, CLI parsing
├── config.py                # Config directory management
├── file_processor.py        # File collection
├── smart_logic.py           # Intelligent selection
├── apptheme.py              # UI theming
├── gui/
│   ├── main_window.py       # Main GUI
│   ├── components/          # UI widgets
│   ├── handlers/            # Event handlers
│   ├── settings/            # Settings UI
│   └── utils/               # GUI utilities
├── pro/                     # Pro features
│   ├── flow/                # Flow Studio
│   ├── llm/                 # LLM integration
│   ├── syntax_highlighter.py
│   └── preview_window.py
└── data/
    ├── default_config.toml
    ├── flow.json            # Default flow template
    ├── flow_best_of_3.json  # Best-of-3 template
    └── AICodePrep.workflow  # macOS Quick Action
```

## Build & Distribution

### Executables

Pre-built executables available via Pro package:

- Windows: `INSTALLER_Windows.bat`
- macOS: `INSTALLER_MacOS.sh`
- Linux: `INSTALLER_Linux.sh`

### Package Management

- **Main app**: `pipx install aicodeprep-gui`
- **Dependencies**: See `pyproject.toml`
- **Python**: 3.8+ (PySide6 requirement)

## Testing

### Test Files Found

- `test_*.py` files in root directory
- Use `pytest` for Python tests

### Manual Testing

```bash
# Test GUI functionality
aicp --debug /path/to/test/project

# Test Pro features
aicp --pro --skipui "test prompt"

# Test Flow Studio
aicp --pro
# Then use Flow Studio interface
```

## Important Documentation

### Core Documentation

- `README.md` - Installation and usage guide
- `CHANGELOG.md` - Version history and features
- `INSTRUCTIONS.md` - Detailed installation instructions
- `SUSTAINABLE-LICENSE` - License terms

### Flow Studio Documentation

- `BESTOFN_COMPLETE_SOLUTION.md` - Dynamic slots implementation
- `BESTOFN_QUICK_REFERENCE.md` - Quick reference guide
- `BESTOFN_VISUAL_GUIDE.md` - Visual walkthrough

### Development Notes

- `.clinerules` - PySide6 patterns and Pro feature development
- Various `FLOW_*.md` files - Implementation notes and fixes

## Workflow Tips

### Daily Usage

1. Right-click project folder → "Open with aicodeprep-gui"
2. Review auto-selected files (based on `.gitignore`)
3. Check/uncheck files as needed
4. Select or write a prompt
5. Click "GENERATE CONTEXT!"
6. Paste into AI chat interface

### Pro Workflow

1. Use Flow Studio for complex multi-LLM tasks
2. Save flow templates for reuse
3. Use headless mode for automation (`--skipui`)
4. Leverage syntax highlighting in preview window

### Development

1. Install with `pip install -e .` for development
2. Use `aicp --debug` for debugging
3. Check `.aicodeprep-gui` for user settings
4. Modify templates in `data/flow_*.json`

## Dependencies

### Core Dependencies (from pyproject.toml)

- PySide6>=6.9,<6.10 - GUI framework
- toml - Configuration parsing
- NodeGraphQt - Flow Studio
- pathspec - Pattern matching
- requests - Network operations
- packaging - Version handling
- Pygments>=2.18.0 - Syntax highlighting
- litellm>=1.40.0 - LLM provider integration
- setuptools>=65.0.0 - Python 3.12+ compatibility

### Development Dependencies

- pytest>=7.0.0 - Testing
- black, ruff, mypy - Linting and type checking
- pyinstaller>=6.0.0 - Building executables
