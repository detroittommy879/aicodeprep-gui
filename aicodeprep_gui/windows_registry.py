import sys
import os
import winreg
import ctypes
import shutil
import logging

def enable_classic_context_menu():
    """
    Enables the classic right-click context menu on Windows 11 by creating the required registry key.
    """
    try:
        key_path = r"Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
        logging.info("Classic context menu enabled (Windows 11).")
        return True, "Classic context menu enabled."
    except Exception as e:
        logging.error(f"Failed to enable classic context menu: {e}")
        return False, f"Failed to enable classic context menu: {e}"

def disable_classic_context_menu():
    """
    Disables the classic right-click context menu on Windows 11 by deleting the registry key.
    """
    try:
        key_path = r"Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
        # Optionally, try to delete parent key if empty
        parent_key_path = r"Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, parent_key_path)
        except OSError:
            pass
        logging.info("Classic context menu disabled (Windows 11).")
        return True, "Classic context menu disabled."
    except FileNotFoundError:
        return True, "Classic context menu key not found (already default)."
    except Exception as e:
        logging.error(f"Failed to disable classic context menu: {e}")
        return False, f"Failed to disable classic context menu: {e}"

def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.error(f"Failed to check admin status: {e}")
        return False

def run_as_admin(action, menu_text=None, enable_classic_menu=None):
    """
    Re-launches the script with admin rights to perform a specific action.
    'action' can be 'install' or 'remove'.
    'menu_text' is optional custom text for the context menu (only used with 'install').
    'enable_classic_menu' is an optional boolean to control classic menu (only used with 'install').
    """
    if sys.platform != 'win32' and sys.platform != 'Windows':
        return False, "This feature is only for Windows."

    verb = "runas"
    executable = sys.executable  # The python interpreter

    # Use -m to run the main module
    script_entry_point = "aicodeprep_gui.main"

    if action == 'install':
        params = f'-m {script_entry_point} --install-context-menu-privileged'
        if menu_text and menu_text.strip():
            # Escape quotes and pass the menu text as an argument
            escaped_text = menu_text.replace('"', '\\"')
            params += f' --menu-text "{escaped_text}"'
        if enable_classic_menu is False:
            params += ' --disable-classic-menu'
    elif action == 'remove':
        params = f'-m {script_entry_point} --remove-context-menu-privileged'
    else:
        return False, "Invalid action."

    try:
        ret = ctypes.windll.shell32.ShellExecuteW(None, verb, executable, params, None, 1)
        if ret > 32:
            return True, "UAC prompt initiated. The application will close."
        else:
            return False, "UAC prompt was cancelled or failed."
    except Exception as e:
        logging.error(f"Failed to elevate privileges: {e}")
        return False, f"An error occurred while trying to elevate: {e}"

def get_registry_command():
    """
    Constructs the command to be written into the registry.
    Uses pythonw.exe to avoid a console window flashing on execution.
    """
    python_exe = sys.executable
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")

    script_path = shutil.which('aicodeprep-gui')
    if not script_path:
        logging.error("Could not find 'aicodeprep-gui' script in system PATH.")
        return None

    # The command to be stored in the registry. Explorer replaces %V with the directory path.
    return f'"{pythonw_exe}" "{script_path}" "%V"'

def install_context_menu(menu_text=None, enable_classic_menu=True):
    """Adds the context menu item to the Windows Registry. Assumes admin rights."""
    if not is_admin():
        logging.error("Install function called without admin rights.")
        print("Administrator rights required.")
        return False, "Administrator rights required."

    command = get_registry_command()
    if not command:
        return False, "'aicodeprep-gui' not found. Is it installed and in your PATH?"

    # Use custom menu text if provided, otherwise use default
    if menu_text is None or menu_text.strip() == "":
        menu_text = "Open with aicodeprep-gui"
    else:
        menu_text = menu_text.strip()

    # Enable or disable classic menu as requested
    if enable_classic_menu:
        enable_classic_context_menu()
        classic_msg = "Classic context menu enabled."
    else:
        disable_classic_context_menu()
        classic_msg = "Classic context menu NOT enabled (Windows 11 default)."

    try:
        key_path = r'Directory\\Background\\shell\\aicodeprep-gui'
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValue(key, '', winreg.REG_SZ, menu_text)
            with winreg.CreateKey(key, 'command') as command_key:
                winreg.SetValue(command_key, '', winreg.REG_SZ, command)

        logging.info(f"Context menu installed successfully with text: '{menu_text}'")
        restart_explorer()
        return True, f"Context menu installed successfully with text: '{menu_text}'! {classic_msg} Explorer has been restarted."
    except Exception as e:
        logging.error(f"Failed to install context menu: {e}")
        return False, f"An error occurred: {e}"

def remove_context_menu():
    """Removes the context menu item from the Windows Registry. Assumes admin rights."""
    if not is_admin():
        logging.error("Remove function called without admin rights.")
        print("Administrator rights required.")
        return False, "Administrator rights required."

    # Always restore default context menu
    disable_classic_context_menu()

    try:
        key_path = r'Directory\\Background\\shell\\aicodeprep-gui'
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)

        logging.info("Context menu removed successfully.")
        restart_explorer()
        return True, "Context menu removed and classic menu restored! Explorer has been restarted."
    except FileNotFoundError:
        return True, "Context menu item was not found (already removed). Classic menu restored."
    except Exception as e:
        logging.error(f"Failed to remove context menu: {e}")
        return False, f"An error occurred: {e}"

def restart_explorer():
    """Restarts the Windows Explorer process to apply registry changes."""
    try:
        os.system("taskkill /f /im explorer.exe")
        os.system("start explorer.exe")
    except Exception as e:
        logging.error(f"Failed to restart explorer.exe: {e}")
