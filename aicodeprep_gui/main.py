import os
import sys
import platform
import ctypes
from PySide6 import QtWidgets
from aicodeprep_gui import pro
from aicodeprep_gui.file_processor import process_files
from aicodeprep_gui.rust_backend import process_with_rust_worker
from aicodeprep_gui.gui.settings.preferences import _existing_prefs_path, _read_prefs_file
from aicodeprep_gui.config import get_flows_dir, copy_builtin_flows
from aicodeprep_gui.user_settings import (
    delete_settings_file,
    clear_legacy_qsettings,
    get_setting,
)

# Handle --delset command-line option to delete user settings and exit
if "--delset" in sys.argv:
    delete_settings_file()
    clear_legacy_qsettings()
    print("All aicodeprep-gui user settings deleted.")
    sys.exit(0)
import argparse
import logging
from typing import List
from aicodeprep_gui.smart_logic import collect_all_files, collect_seed_paths
from aicodeprep_gui.gui import show_file_selection_gui
from aicodeprep_gui.apptheme import load_custom_fonts

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

LINUX_DESKTOP_APP_ID = "io.github.detroittommy879.aicodeprep_gui"


def process_files_with_fast_backend(
    selected_files,
    output_filename,
    output_format,
    prompt,
    prompt_to_top,
    prompt_to_bottom,
) -> int:
    """Use Rust packing when available, with the Python implementation as fallback."""
    use_rust = bool(get_setting("rust_backend", "enabled", True)) and bool(
        get_setting("pro_options", "rust_fast_processing", True))
    if use_rust:
        rust_result = process_with_rust_worker(
            selected_files,
            output_filename,
            output_format,
            prompt,
            prompt_to_top,
            prompt_to_bottom,
        )
        if rust_result.ok:
            logger.info("Generated context with Rust worker.")
            return rust_result.files_processed
        logger.info(
            "Rust worker unavailable for context generation, falling back to Python: %s",
            rust_result.error,
        )

    return process_files(
        selected_files,
        output_filename,
        fmt=output_format,
        prompt=prompt,
        prompt_to_top=prompt_to_top,
        prompt_to_bottom=prompt_to_bottom,
    )


def _configure_application_metadata(app: QtWidgets.QApplication) -> None:
    """Apply stable application metadata for desktop integration."""
    app.setApplicationName("aicodeprep-gui")
    app.setOrganizationName("wuu73")
    app.setOrganizationDomain("wuu73.org")

    if hasattr(app, "setApplicationDisplayName"):
        app.setApplicationDisplayName("AICodePrep GUI")

    if platform.system() == "Linux" and hasattr(app, "setDesktopFileName"):
        app.setDesktopFileName(LINUX_DESKTOP_APP_ID)


def main():
    # Ensure configuration directories are created and copy built-in flows
    get_flows_dir()  # This creates ~/.aicodeprep-gui/flows/
    copy_builtin_flows()  # Copy flow_*.json templates from data/ to flows/

    parser = argparse.ArgumentParser(
        description="aicodeprep-gui: A smart GUI for preparing code repositories for AI analysis. Select and bundle files to be copied into your clipboard.")
    parser.add_argument("-n", "--no-copy", action="store_true",
                        help="Do NOT copy output to clipboard (default: copy to clipboard)")
    parser.add_argument("-o", "--output", default=os.path.join(".aicp", "context_block.md"),
                        help="Output file name (default: .aicp/context_block.md)")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to process (default: current directory)")
    parser.add_argument("--force-update-check", action="store_true",
                        help="Force update check (ignore 24h limit)")
    parser.add_argument("--notpro", action="store_true",
                        help="Temporarily disable Pro features for this session")
    parser.add_argument("--262144", action="store_true",
                        help=argparse.SUPPRESS)
    parser.add_argument("-s", "--skipui", nargs='?', const='', default=None,
                        help="Pro: Skip UI and generate context immediately. Optionally provide a prompt string after the flag.")
    parser.add_argument("--list-languages", action="store_true",
                        help="List all available languages and exit")
    parser.add_argument("--language", type=str, metavar="CODE",
                        help="Set application language (e.g., --language es for Spanish)")
    parser.add_argument("--fastads", action="store_true",
                        help="Speed up ad rotation to 1.5 seconds (for testing)")

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

    if args.fastads:
        os.environ["AICODEPREP_FASTADS"] = "1"

    # Handle --list-languages
    if args.list_languages:
        from aicodeprep_gui.i18n.translator import TranslationManager
        # Create minimal app just for TranslationManager
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        _configure_application_metadata(app)
        tm = TranslationManager(app)
        print("Available languages:")
        for code, name in sorted(tm.get_available_languages()):
            current = " (current)" if tm.get_saved_language_preference(
            ) == code else ""
            print(f"  {code:8} - {name}{current}")
        sys.exit(0)

    # --- START: Headless / Skip-UI Mode ---
    if args.skipui is not None:
        if not pro.enabled:
            print("Pro feature --skipui: Please enable Pro mode.")
            print("Check out https://wuu73.org/aicp for more info.")
            sys.exit(1)

        # Ensure we are in the target directory
        target_dir_headless = args.directory
        try:
            os.chdir(target_dir_headless)
        except FileNotFoundError:
            logger.error(f"Directory not found: {target_dir_headless}")
            sys.exit(1)

        logger.info("Running in headless (skip-UI) mode...")

        selected_files = []
        output_format = "xml"
        prefs_path, _ = _existing_prefs_path(target_dir_headless)
        prefs_file_exists = os.path.exists(prefs_path)

        if prefs_file_exists:
            checked_from_prefs, _, _, output_format, _, _, _, _, _ = _read_prefs_file(
                target_dir_headless)
            logger.info(
                "Found project preferences at %s. Using saved file selection for headless generation.",
                prefs_path,
            )
            for rel_path in checked_from_prefs:
                abs_path = os.path.join(target_dir_headless, rel_path)
                if os.path.isfile(abs_path):
                    selected_files.append(abs_path)

        if not selected_files:
            logger.info(
                "No usable saved project selection found. Performing a full recursive scan.")
            all_files_with_flags = collect_all_files(target_dir_headless)
            if not all_files_with_flags:
                logger.warning("No files found to process!")
                sys.exit(0)
            logger.info("Using smart default file selection.")
            for abs_path, _, is_checked in all_files_with_flags:
                if is_checked and os.path.isfile(abs_path):
                    selected_files.append(abs_path)

        if not selected_files:
            logger.warning(
                "No files were selected based on defaults or saved preferences. Nothing to generate.")
            sys.exit(0)

        # 3. Load prompt placement settings from global config
        # We need a QApplication instance for clipboard access
        try:
            app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            _configure_application_metadata(app)
        except Exception as e:
            logger.error(f"Failed to create QApplication instance: {e}")
            sys.exit(1)

        prompt_to_top = get_setting("prompt_options", "prompt_to_top", True)
        prompt_to_bottom = get_setting(
            "prompt_options", "prompt_to_bottom", True)

        # 4. Get prompt from arguments
        prompt = args.skipui if args.skipui else ""

        # 5. Process files
        logger.info(f"Generating context for {len(selected_files)} files...")
        output_filename = args.output
        try:
            processed_count = process_files_with_fast_backend(
                selected_files,
                output_filename,
                output_format,
                prompt=prompt,
                prompt_to_top=prompt_to_top,
                prompt_to_bottom=prompt_to_bottom
            )
        except Exception as e:
            logger.error(f"Failed to process files: {e}")
            sys.exit(1)

        if processed_count > 0:
            output_path = os.path.join(os.getcwd(), output_filename)
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if not args.no_copy:
                    try:
                        clipboard = QtWidgets.QApplication.clipboard()
                        clipboard.setText(content)
                        logger.info(
                            f"Successfully generated '{output_filename}' and copied content to clipboard.")
                    except Exception as e:
                        logger.error(f"Failed to copy to clipboard: {e}")
                        logger.info(
                            f"Successfully generated '{output_filename}' (clipboard copy failed)")
                else:
                    logger.info(
                        f"Successfully generated '{output_filename}' (clipboard copy skipped)")
            except Exception as e:
                logger.error(
                    f"Failed to read output file '{output_path}': {e}")
                sys.exit(1)
        else:
            logger.warning("No files were processed.")

        sys.exit(0)
    # --- END: Headless / Skip-UI Mode ---

    force_update = args.force_update_check

    # Set Windows AppUserModelID for proper taskbar icon
    if platform.system() == "Windows":
        myappid = 'wuu73.aicodeprep-gui'  # arbitrary unique string
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
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    _configure_application_metadata(app)
    app.setStyle("Fusion")

    # Set application icon from package favicon.ico
    from PySide6.QtGui import QIcon
    from importlib import resources
    with resources.as_file(resources.files('aicodeprep_gui.images').joinpath('favicon.ico')) as icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))

    # Initialize internationalization (i18n)
    from aicodeprep_gui.i18n.translator import TranslationManager
    translation_manager = TranslationManager(app)

    # Handle --language command line option
    if args.language:
        if translation_manager.is_language_available(args.language):
            logger.info(f"Setting language from command line: {args.language}")
            translation_manager.set_language(args.language)
        else:
            logger.warning(
                f"Language '{args.language}' not available. Use --list-languages to see available languages.")
            sys.exit(1)
    else:
        # Load saved language preference or detect system language
        saved_lang = translation_manager.get_saved_language_preference()
        if saved_lang:
            logger.info(f"Loading saved language: {saved_lang}")
            translation_manager.set_language(saved_lang)
        else:
            detected_lang = translation_manager.detect_system_language()
            logger.info(f"Detected system language: {detected_lang}")
            if translation_manager.is_language_bundled(detected_lang):
                translation_manager.set_language(detected_lang)
            else:
                # Use English for non-bundled languages (user can change later)
                translation_manager.set_language('en')

    # Store translation manager in app for global access
    app.translation_manager = translation_manager

    # Load custom fonts
    loaded_fonts = load_custom_fonts()
    if loaded_fonts:
        logging.info(f"Loaded custom fonts: {', '.join(loaded_fonts)}")
    else:
        logging.warning("No custom fonts were loaded")

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

    prefs_path, _ = _existing_prefs_path(target_dir)
    if os.path.exists(prefs_path):
        checked_from_prefs, _, _, _, _, _, _, _, _ = _read_prefs_file(
            target_dir)
        logger.info(
            "Found project preferences at %s; seeding visible tree without a full recursive scan.",
            prefs_path,
        )
        all_files_with_flags = collect_seed_paths(
            target_dir, checked_from_prefs)
        initial_tree_fully_loaded = False
    else:
        logger.info(
            "No project preferences found for %s; performing a full recursive scan.",
            target_dir,
        )
        all_files_with_flags = collect_all_files(target_dir)
        initial_tree_fully_loaded = True

    if not all_files_with_flags:
        logger.warning("No files found to process!")
        return

    action, _ = show_file_selection_gui(
        all_files_with_flags,
        project_root=target_dir,
        initial_tree_fully_loaded=initial_tree_fully_loaded,
    )

    if action != 'quit':
        logger.info(
            "Buy my cat a treat, comments, ideas for improvement appreciated: ")
        logger.info("https://wuu73.org/hello.html")


if __name__ == "__main__":
    main()
