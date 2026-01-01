
---
**New File: `scripts/install-windows.bat`**
```bat
@echo off
setlocal

:: ============================================================================
:: aicodeprep-gui Installer for Windows
:: ============================================================================
:: This script automates the installation of aicodeprep-gui using pipx.
:: It checks for Python, installs pipx, and then installs the application.
:: It will create a log file in this directory.
:: ============================================================================

set "LOGFILE=install_log_windows.txt"
echo. > %LOGFILE%

call :log "--- Starting aicodeprep-gui Installer for Windows ---"
call :log "--- %date% %time% ---"
call :log ""

:: --- Step 1: Find Python ---
call :log "Step 1: Checking for Python..."
set "PYTHON_CMD="

:: Check for 'py' launcher first (modern standard)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    call :log "Found Python via the 'py' launcher."
) else (
    :: Fallback to 'python'
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
        call :log "Found Python via the 'python' command."
    ) else (
        :: Fallback to 'python3'
        python3 --version >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_CMD=python3"
            call :log "Found Python via the 'python3' command."
        )
    )
)

if not defined PYTHON_CMD (
    call :log "ERROR: Python is not installed or not found in your system's PATH."
    call :log "Please install the latest stable version of Python from:"
    call :log "https://www.python.org/downloads/windows/"
    call :log ""
    call :log "IMPORTANT: During installation, make sure to check the box that says"
    call :log "'Add Python to PATH'."
    goto :end_script
)

call :log "Python found! Using '%PYTHON_CMD%' for commands."
call :log ""

:: --- Step 2: Ensure Pip is available ---
call :log "Step 2: Checking for Pip..."
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Pip (Python's package installer) is not available."
    call :log "This is unusual. Your Python installation might be corrupted."
    call :log "Please try reinstalling Python from python.org."
    goto :end_script
)
call :log "Pip is available."
call :log ""

:: --- Step 3: Install/Upgrade Pipx ---
call :log "Step 3: Installing/upgrading pipx..."
call :log "pipx is a tool to install Python applications in isolated environments."
call :log "This is the recommended way to install tools like aicodeprep-gui."

%PYTHON_CMD% -m pip install --user --upgrade pipx >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Failed to install pipx. Please check the log file for details:"
    call :log "%LOGFILE%"
    goto :end_script
)
call :log "pipx installed successfully."
call :log ""

:: --- Step 4: Add Pipx to PATH ---
call :log "Step 4: Ensuring pipx is in your system's PATH..."
%PYTHON_CMD% -m pipx ensurepath >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    call :log "WARNING: 'pipx ensurepath' command failed. This might be okay."
    call :log "We will proceed, but if the 'aicp' command doesn't work later,"
    call :log "you may need to add the scripts path to your PATH environment variable manually."
) else (
    call :log "pipx paths are configured."
)
call :log ""

:: --- Step 5: Install aicodeprep-gui ---
call :log "Step 5: Installing aicodeprep-gui..."
call :log "This may take a minute or two..."
pipx install aicodeprep-gui >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    call :log "ERROR: Failed to install aicodeprep-gui with pipx."
    call :log "Trying to upgrade it in case it's an old version..."
    pipx upgrade aicodeprep-gui >> %LOGFILE% 2>&1
    if %errorlevel% neq 0 (
      call :log "ERROR: Upgrade also failed. Please check the log file for details:"
      call :log "%LOGFILE%"
      goto :end_script
    )
)

call :log ""
call :log "============================================================================"
call :log "  SUCCESS! aicodeprep-gui has been installed."
call :log "============================================================================"
call :log ""
call :log "  IMPORTANT: You MUST close this window and open a NEW Command"
call :log "  Prompt, PowerShell, or Terminal window for the changes to take effect."
call :log ""
call :log "  After opening a new terminal, you can run the app from any"
call :log "  folder by typing:"
call :log "  aicp"
call :log ""
call :log "============================================================================"
goto :end_script

:log
echo %~1
echo %~1 >> %LOGFILE%
exit /b

:end_script
call :log ""
call :log "Installation script finished. Press any key to close this window."
pause >nul
exit /b