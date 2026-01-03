import winreg
import os
import sys
import subprocess
import argparse


def add_classic_right_click_menu():
    try:
        # Define the registry path
        key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"

        # Check if the key exists
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ):
                print("Classic right-click menu registry entry already exists.")
                return True
        except FileNotFoundError:
            # Key does not exist, so we proceed to create it
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
                print("Classic right-click menu enabled successfully.")
                return True

    except Exception as e:
        print(f"An error occurred while adding classic right-click menu: {e}")
        return False


def remove_classic_right_click_menu():
    try:
        key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            print("Classic right-click menu disabled successfully.")
            return True
        except FileNotFoundError:
            print("Classic right-click menu registry entry not found.")
            return False

    except Exception as e:
        print(f"An error occurred while removing classic right-click menu: {e}")
        return False


def restart_explorer():
    # Restart Windows Explorer to apply changes
    os.system("taskkill /f /im explorer.exe")
    os.system("start explorer.exe")


def add_to_context_menu():
    # Get the path to the aicodeprep executable
    try:
        result = subprocess.run(['where', 'aicodeprep-gui-c'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: aicodeprep-gui-c not found. Please install the package first.")
            return False
        script_path = result.stdout.strip().split('\n')[0]
    except Exception as e:
        print(f"Error finding aicodeprep-gui: {e}")
        return False

    # Create command string that handles spaces in paths
    python_path = sys.executable
    # Wrap paths in quotes and escape existing quotes if necessary
    command = f'cmd /k "\"{python_path}\" \"{script_path}\" \"%V\""'

    try:
        # Create context menu for directories
        key_path = r'Directory\Background\shell\aicodeprep-gui-c'
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, '', winreg.REG_SZ, 'AI Code Prep GUI')

        command_key = winreg.CreateKey(key, 'command')
        winreg.SetValue(command_key, '', winreg.REG_SZ, command)

        print("Context menu entry added successfully!")
        return True

    except Exception as e:
        print(f"Error adding context menu: {str(e)}")
        return False


def remove_from_context_menu():
    try:
        key_path = r'Directory\Background\shell\aicodeprep-gui-c'
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        print("Context menu entry removed successfully!")
        return True
    except Exception as e:
        print(f"Error removing context menu: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Manage Windows Context Menus')

    # Create mutually exclusive group for classic right-click menu
    classic_group = parser.add_mutually_exclusive_group()
    classic_group.add_argument('--enable-classic', action='store_true',
                               help='Enable classic right-click menu')
    classic_group.add_argument('--disable-classic', action='store_true',
                               help='Disable classic right-click menu')

    # Create mutually exclusive group for context menu
    context_group = parser.add_mutually_exclusive_group()
    context_group.add_argument('--add-context', action='store_true',
                               help='Add AI Code Prep to context menu')
    context_group.add_argument('--remove-context', action='store_true',
                               help='Remove AI Code Prep from context menu')

    args = parser.parse_args()

    # Track if any changes were made to trigger explorer restart
    changes_made = False

    # Handle classic right-click menu
    if args.enable_classic:
        if add_classic_right_click_menu():
            changes_made = True
    elif args.disable_classic:
        if remove_classic_right_click_menu():
            changes_made = True

    # Handle context menu
    if args.add_context:
        if add_to_context_menu():
            changes_made = True
    elif args.remove_context:
        if remove_from_context_menu():
            changes_made = True

    # Restart explorer if changes were made
    if changes_made:
        restart_explorer()


if __name__ == '__main__':
    main()
