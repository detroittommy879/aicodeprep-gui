import os
import sys
import platform
import ctypes
from PySide6.QtCore import QSettings

# Handle --delset command-line option to delete user settings and exit
if "--delset" in sys.argv:
    # Delete ButtonPresets
    QSettings("aicodeprep-gui", "ButtonPresets").clear()
    # Delete PromptOptions
    QSettings("aicodeprep-gui", "PromptOptions").clear()
    # Delete UserIdentity
    QSettings("aicodeprep-gui", "UserIdentity").clear()
    print("All aicodeprep-gui user settings deleted.")
    sys.exit(0)
import argparse
import logging
from typing import List
from aicodeprep_gui.smart_logic import collect_all_files
from aicodeprep_gui.gui import show_file_selection_gui

# Configure logging with explicit console handler only
logger = logging.getLogger()

# Remove any existing handlers to prevent duplicate logging
for handler in logger.handlers:
    logger.removeHandler(handler)

logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handler to root logger
logger.addHandler(console_handler)


def main():
    parser = argparse.ArgumentParser(
        description="aicodeprep-gui: A smart GUI for preparing code repositories for AI analysis. Select and bundle files to be copied into your clipboard.")
    parser.add_argument("-n", "--no-copy", action="store_true",
                        help="Do NOT copy output to clipboard (default: copy to clipboard)")
    parser.add_argument("--pro", action="store_true",
                        help="Enable Pro features (fake license mode)")
    parser.add_argument("-o", "--output", default="fullcode.txt",
                        help="Output file name (default: fullcode.txt)")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to process (default: current directory)")
    parser.add_argument("--force-update-check", action="store_true",
                        help="Force update check (ignore 24h limit)")

    # --- ADD THESE NEW ARGUMENTS ---
    if platform.system() == "Windows":
        parser.add_argument("--install-context-menu-privileged",
                            action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("--remove-context-menu-privileged",
                            action="store_true", help=argparse.SUPPRESS)
        parser.add_argument("--menu-text", type=str, help=argparse.SUPPRESS)
        parser.add_argument("--disable-classic-menu",
                            action="store_true", help=argparse.SUPPRESS)
    # --- END OF NEW ARGUMENTS ---

    args = parser.parse_args()
    if '--pro' in sys.argv:
        open('pro_enabled', 'w').close()   # Create marker file

    force_update = args.force_update_check

    # Set Windows AppUserModelID for proper taskbar icon
    if platform.system() == "Windows":
        myappid = 'wuu73.aicodeprep-gui.1.1.2'  # arbitrary unique string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                myappid)
        except AttributeError:
            # Fails on older Windows versions, but that's acceptable.
            logging.warning(
                "Could not set AppUserModelID. Taskbar icon may not be correct on older Windows.")

    # --- ADD THIS NEW LOGIC BLOCK ---
    if platform.system() == "Windows":
        try:
            from aicodeprep_gui import windows_registry
        except ImportError:
            windows_registry = None
        if args.install_context_menu_privileged and windows_registry:
            print("Running privileged action: Install context menu...")
            menu_text = getattr(args, 'menu_text', None)
            enable_classic = not getattr(args, 'disable_classic_menu', False)
            windows_registry.install_context_menu(
                menu_text, enable_classic_menu=enable_classic)
            sys.exit(0)
        if args.remove_context_menu_privileged and windows_registry:
            print("Running privileged action: Remove context menu...")
            windows_registry.remove_context_menu()
            sys.exit(0)
    # --- END OF NEW LOGIC BLOCK ---

    # Ensure Fusion style for QSS consistency
    from PySide6 import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application icon from package favicon.ico
    from PySide6.QtGui import QIcon
    from importlib import resources
    with resources.as_file(resources.files('aicodeprep_gui.images').joinpath('favicon.ico')) as icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))

    if args.debug:
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)

    # Get the target directory from the parsed arguments
    target_dir = args.directory
    logger.info(f"Target directory: {target_dir}")

    # Change to the specified directory with error handling
    try:
        os.chdir(target_dir)
    except FileNotFoundError:
        logger.error(f"Directory not found: {target_dir}")
        return
    except Exception as e:
        logger.error(f"Error changing directory: {e}")
        return

    logger.info("Starting code concatenation...")

    all_files_with_flags = collect_all_files()

    if not all_files_with_flags:
        logger.warning("No files found to process!")
        return

    action, _ = show_file_selection_gui(all_files_with_flags)

    if action != 'quit':
        logger.info(
            "Buy my cat a treat, comments, ideas for improvement appreciated: ")
        logger.info("https://wuu73.org/hello.html")


if __name__ == "__main__":
    main()
