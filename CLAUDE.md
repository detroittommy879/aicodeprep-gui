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

### Real GUI screenshot + i18n audit loop

If you need to validate that translations are visible in the actual running GUI (not just unit tests), use:

- `uv run python scripts/gui_language_screenshot_loop.py --language es`
- `uv run python scripts/gui_language_screenshot_loop.py --languages es fr zh_CN`

This captures screenshots and writes a heuristic report of strings that stayed identical to English into `screenshots/test_captures/`.

#### Troubleshooting (when GUI tests hang)

- Prefer enabling auto-close for loop runs: set `AICODEPREP_AUTO_CLOSE=1`.
- If a test run leaves a stuck Qt/Python process (Windows): `taskkill /IM python.exe /F`
- If needed, run a single test first (tight loop) before full suite: `uv run pytest tests/test_i18n.py -q`

### Translations (i18n): .ts -> .qm compilation

- Translation files live in `aicodeprep_gui/i18n/translations/`.
- If you edit `.ts` files manually (translations “ready”), you must recompile `.qm`:
  - Compile all: `uv run python scripts/compile_translations.py`
  - Compile subset: `uv run python scripts/compile_translations.py es fr zh_CN`
  - Alternative: `uv run python scripts/generate_translations.py --compile-only`
- `scripts/generate_translations.py` supports:
  - default: update `.ts` via lupdate and compile `.qm`
  - `--compile-only`: compile existing `.ts` into `.qm` (does not touch `.ts`)
  - `--update-ts-only`: regenerate `.ts` from source (does not compile)

### Updating This Handoff

- If you discover something that would normally require the user to repeat instructions (env vars, flaky tests, platform quirks, one-off scripts), add it to this file and to `AGENTS.md`.
- Keep entries short and actionable (commands, file paths, env vars).

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

### Parallel MCP Server (`parallel-MCP/parallel-llm-mcp/`)

**Purpose**: Headless MCP server for multi-LLM workflows

**Technology Stack:**

- Python 3.8+
- FastMCP for MCP protocol
- Pydantic for validation
- Pytest for testing

**Key Files:**

- `src/parallel_llm_mcp/server.py` - MCP server implementation
- `src/parallel_llm_mcp/parallel.py` - Parallel LLM orchestration
- `src/parallel_llm_mcp/client.py` - Client for MCP interactions
- `tests/` - Test suite

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

### Parallel MCP Server

```bash
# Install dependencies
pip install fastmcp httpx pydantic

# Run tests
pytest

# Run with linting
pytest && black src/ tests/ && ruff check src/ tests/ && mypy src/

# Run MCP server
python -m parallel_llm_mcp
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

parallel-MCP/parallel-llm-mcp/
├── src/parallel_llm_mcp/
│   ├── server.py            # MCP server
│   ├── parallel.py          # LLM orchestration
│   └── client.py            # Client
└── tests/                   # Test suite
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
- `parallel-MCP/parallel-llm-mcp/tests/` for MCP server tests
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
- `MCP_FLOW_SERVER_PLAN.md` - Architecture for headless MCP server

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
5. Run MCP server tests with `pytest`

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
