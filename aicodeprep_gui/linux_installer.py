import os
import shutil
import logging

NAUTILUS_SCRIPTS_DIR = os.path.expanduser("~/.local/share/nautilus/scripts")
SCRIPT_NAME = "Open with aicodeprep-gui"

# The shell script to be placed in the Nautilus scripts directory.
NAUTILUS_SCRIPT_CONTENT = """
#!/bin/bash

# Nautilus script for aicodeprep-gui.
# It processes the first selected directory.

# Find the command path. 'which' should work as this script runs in a user session.
CMD_PATH=$(which aicodeprep-gui)

if [ -z "$CMD_PATH" ]; then
    # Use zenity for a graphical error message if available
    if command -v zenity &> /dev/null; then
        zenity --error --width=300 --text="<b>aicodeprep-gui command not found.</b>\\n\\nPlease ensure it's installed and accessible from your terminal's PATH."
    fi
    exit 1
fi

# Nautilus provides selected paths as arguments.
TARGET_DIR="$1"

if [ -n "$TARGET_DIR" ] && [ -d "$TARGET_DIR" ]; then
    # Run the GUI, passing the selected directory.
    # Run in the background to not block Nautilus.
    "$CMD_PATH" "$TARGET_DIR" &
else
    if command -v zenity &> /dev/null; then
        zenity --info --text="Please select a directory to use this script."
    fi
fi
"""

def is_nautilus_installed():
    """Check if Nautilus file manager is likely installed."""
    return shutil.which('nautilus') is not None

def install_nautilus_script():
    """Installs the context menu script for the Nautilus file manager."""
    if not is_nautilus_installed():
        return False, "Nautilus file manager not found."

    try:
        os.makedirs(NAUTILUS_SCRIPTS_DIR, exist_ok=True)
        script_path = os.path.join(NAUTILUS_SCRIPTS_DIR, SCRIPT_NAME)
        
        with open(script_path, "w") as f:
            f.write(NAUTILUS_SCRIPT_CONTENT)
        
        # Make the script executable
        os.chmod(script_path, 0o755)

        msg = (f"Nautilus script '{SCRIPT_NAME}' installed successfully. "
               "Please restart Nautilus (nautilus -q) or log out and back in for it to appear.")
        logging.info(msg)
        return True, msg
    except Exception as e:
        msg = f"Failed to install Nautilus script: {e}"
        logging.error(msg)
        return False, msg

def uninstall_nautilus_script():
    """Uninstalls the context menu script for Nautilus."""
    script_path = os.path.join(NAUTILUS_SCRIPTS_DIR, SCRIPT_NAME)
    if os.path.exists(script_path):
        try:
            os.remove(script_path)
            msg = f"Nautilus script '{SCRIPT_NAME}' has been uninstalled."
            logging.info(msg)
            return True, msg
        except Exception as e:
            msg = f"Failed to uninstall Nautilus script: {e}"
            logging.error(msg)
            return False, msg
    else:
        msg = "Nautilus script not found (already uninstalled)."
        return True, msg
