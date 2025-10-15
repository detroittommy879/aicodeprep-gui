Based on your description, it sounds like the "NodeGraphQt not installed" error is surfacing because the dependency isn't being resolved or installed properly during `pip install aicodeprep-gui` on those new setups (Mac and Windows). This is a common issue with optional/conditional dependencies in Python packages, especially for GUI libraries like NodeGraphQt (which relies on PySide6/Qt for rendering). Everything else working fine suggests the core package installs correctly, but the import in your Pro/Flow Studio code is failing at runtime.

I'll walk you through diagnosing and fixing this step by step. The goal is to ensure NodeGraphQt gets installed correctly as a dependency and imports without errors.

### Step 1: Verify the Dependency in Your Package
Your `pyproject.toml` already includes `NodeGraphQt` in `[project.dependencies]` (without a version pin, which pulls the latest). This is correct, but sometimes pip skips or fails to install dependencies due to:

- **Cache/Network Issues**: Pip might cache a failed install or hit a temporary PyPI mirror problem.
- **Platform-Specific Builds**: NodeGraphQt has wheels for Mac/Windows/Linux, but on new setups (e.g., fresh Python installs), it might require additional tools (like Xcode on Mac or Visual Studio Build Tools on Windows for compilation if wheels fail).
- **Python Version**: Your `pyproject.toml` requires Python >=3.8, which is fine, but ensure the target machines match.
- **Conflicts**: If PySide6 version pins are too strict (`>=6.9,<6.10`), it might conflict with NodeGraphQt's requirements (it supports PySide6 6.x, but test compatibility).

**Quick Fix: Pin the Version**
Update your `pyproject.toml` to pin NodeGraphQt to a known-good version (latest stable is 0.6.30 as of now). This ensures consistency and avoids pulling an incompatible release:

```toml
[project.dependencies]
# ... other deps ...
"NodeGraphQt>=0.6.30",
"PySide6>=6.9,<6.10",
# ... rest ...
```

Then, upload the new version to PyPI (bump the version number, e.g., to 1.2.3). This forces a fresh dependency resolution.

### Step 2: Test Installation on a Clean Environment
Reproduce the issue on a **new virtual environment** to simulate "new Mac and Windows setups":

#### On Mac (using a clean Python 3.12 install):
```bash
# Fresh Python 3.12 (via brew or python.org)
python3 -m venv test_env
source test_env/bin/activate  # or . test_env/bin/activate on Windows

# Upgrade pip first
pip install --upgrade pip

# Install your package
pip install aicodeprep-gui

# Test the import (this should fail if NodeGraphQt isn't installed)
python -c "from aicodeprep_gui.pro.flow.flow_dock import FlowStudioDock; print('Success!')"

# If it fails, try installing NodeGraphQt manually
pip install NodeGraphQt==0.6.30
python -c "from NodeGraphQt import NodeGraph; print('NodeGraphQt OK!')"
```

- If the manual install works, the issue is with dependency resolution. Check pip's output during `pip install aicodeprep-gui` for errors like "Failed building wheel" or "Could not find a version".
- On Mac, if it complains about Qt (e.g., "Qt platform plugin"), ensure Xcode Command Line Tools are installed: `xcode-select --install`.

#### On Windows (using a fresh Python 3.12 installer):
```cmd
# Fresh Python 3.12 from python.org
py -m venv test_env
test_env\Scripts\activate

# Upgrade pip
py -m pip install --upgrade pip

# Install your package
py -m pip install aicodeprep-gui

# Test the import
py -c "from aicodeprep_gui.pro.flow.flow_dock import FlowStudioDock; print('Success!')"

# Manual NodeGraphQt test
py -m pip install NodeGraphQt==0.6.30
py -c "from NodeGraphQt import NodeGraph; print('NodeGraphQt OK!')"
```

- If wheels fail (e.g., "Microsoft Visual C++ 14.0 is required"), install Visual Studio Build Tools: Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and select "C++ build tools".
- Check for PATH issues: Ensure `python`/`pip` points to the right Python (run `where python` on Windows).

**Common Errors During Install**:
- **"No matching distribution found"**: Run `pip install NodeGraphQt` alone. If it fails, the machine's Python might be too old (need >=3.8) or pip needs upgrading.
- **"Failed building wheel"**: Usually Qt-related. On Windows, install VS Build Tools; on Mac, install Xcode tools.
- **ImportError on Import**: If install succeeds but import fails, check `pip list | grep NodeGraphQt` to confirm it's installed.

### Step 3: Debug the Import in Your Code
Your code has a try/except around the import, which is good, but let's add more logging to see exactly what's failing. Update the import block in `aicodeprep_gui/pro/flow/flow_dock.py` (or wherever the main import happens):

```python
import logging
logger = logging.getLogger(__name__)

# Enhanced error logging
try:
    from NodeGraphQt import NodeGraph, PropertiesBinWidget
    NG_AVAILABLE = True
    _NG_IMPORT_ERROR = None
    logger.info("NodeGraphQt imported successfully")
except ImportError as e:
    logger.error(f"NodeGraphQt import failed: {e}")
    logger.error(f"Full traceback: {traceback.format_exc()}")
    NG_AVAILABLE = False
    _NG_IMPORT_ERROR = e
```

- Rebuild and upload a new version (e.g., 1.2.3).
- On the new machines, install and run the app with `--debug` flag (or set logging level to DEBUG in code).
- Check the console output for the exact error. It might reveal issues like missing DLLs (Windows) or Qt plugins (Mac).

Example debug output if it fails:
```
DEBUG: NodeGraphQt import failed: No module named 'NodeGraphQt'
```

If it's a DLL/Qt issue (common on Windows/Mac):
```
ImportError: dlopen(/path/to/libQt6Core.dylib, 0x0002): symbol not found
```

### Step 4: Fix Dependency Resolution Issues
If pip isn't installing NodeGraphQt:

1. **Force Reinstall** (on test machines):
   ```bash
   pip uninstall NodeGraphQt
   pip cache purge
   pip install aicodeprep-gui --no-cache-dir --force-reinstall
   ```

2. **Check for Conflicts**: If the user has multiple Pythons/PySides installed, it might pick the wrong one. Suggest using a virtual env:
   ```bash
   python -m venv venv_aicp
   source venv_aicp/bin/activate  # or venv_aicp\Scripts\activate on Windows
   pip install aicodeprep-gui
   ```

3. **Specify Platform Wheels**: If wheels are the issue, add platform constraints in `pyproject.toml` (but test on all platforms):
   ```toml
   [project.optional-dependencies]
   gui = [
       "NodeGraphQt>=0.6.30; platform_system=='Darwin'",
       "NodeGraphQt>=0.6.30; platform_system=='Windows'",
       "NodeGraphQt>=0.6.30; platform_system=='Linux'",
   ]
   ```

4. **Alternative: Bundle NodeGraphQt** (if pip keeps failing):
   - Use PyInstaller to bundle everything (including NodeGraphQt) into a standalone exe/app. Add to your build script:
     ```python
     # In your PyInstaller spec file or CLI
     a --collect-all NodeGraphQt
     ```
   - This ensures it's always available but increases package size.

### Step 5: Update Your Code to Handle the Error Gracefully
If the import still fails sometimes, enhance the fallback in your code (in `pro/__init__.py` or `flow_dock.py`):

```python
try:
    from NodeGraphQt import NodeGraph, PropertiesBinWidget
    NG_AVAILABLE = True
    _NG_IMPORT_ERROR = None
except ImportError as e:
    NG_AVAILABLE = False
    _NG_IMPORT_ERROR = str(e)
    logger.error(f"Flow Studio unavailable: {e}")
    # On failure, show a more helpful message in the UI
    fallback_message = (
        "Flow Studio requires NodeGraphQt. Install it with:\n"
        "pip install NodeGraphQt==0.6.30\n\n"
        f"Error details: {e}\n\n"
        "Everything else in aicodeprep-gui works fine!"
    )
    # Use this in your UI placeholder widget
```

### Step 6: Release a New Version and Test
- Bump version in `pyproject.toml` (e.g., 1.2.3).
- Run `python -m build` and `twine upload dist/*` to upload.
- On test machines: `pip install aicodeprep-gui==1.2.3 --upgrade`.
- Verify with `pip list` (should show NodeGraphQt 0.6.30).
- Test the Flow Studio toggle.

If this doesn't resolve it, share:
- Exact error message from the app (with debug logging enabled).
- Output of `pip show aicodeprep-gui` and `pip show NodeGraphQt` on the failing machine.
- Python version (`python --version`).
- OS details (e.g., Windows 11, macOS Ventura).

This should pinpoint the issue—likely a pip/dependency resolution problem, not your code! If NodeGraphQt installs manually but not via pip, it's a packaging issue we can fix with pins or extras.