from importlib import resources
import os
import sys
import logging
from typing import List, Tuple
import fnmatch

# New imports for the refactoring
import toml
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

def get_config_path():
    """Get the path to the default configuration file."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        config_path = os.path.join(base_path, 'aicodeprep_gui', 'data', 'default_config.toml')
    else:
        try:
            with resources.path('aicodeprep_gui.data', 'default_config.toml') as config_file:
                config_path = str(config_file)
        except ModuleNotFoundError:
            config_path = os.path.join(os.path.dirname(__file__), 'data', 'default_config.toml')
    return config_path

def load_config_from_path(path: str) -> dict:
    """Loads a TOML configuration file from a given path."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return toml.load(f)
    except Exception as e:
        logging.error(f"Error loading or parsing TOML config at {path}: {e}")
        return {}

def load_configurations() -> dict:
    """Load default config, then load user config and merge them."""
    default_config_path = get_config_path()
    config = load_config_from_path(default_config_path)
    if not config:
        logging.critical("Failed to load default configuration. Exiting.")
        sys.exit("Could not load the default configuration file.")
    user_config_path = os.path.join(os.getcwd(), 'aicodeprep-gui.toml')
    user_config = load_config_from_path(user_config_path)
    if user_config:
        logging.info(f"Found user configuration at {user_config_path}. Merging settings.")
        config.update(user_config)
    return config

def is_binary_file(filepath: str) -> bool:
    """Return True if this file is likely binary."""
    try:
        with open(filepath, 'rb') as f: chunk = f.read(1024)
    except OSError: return False
    if chunk.startswith((b'\xEF\xBB\xBF', b'\xFF\xFE', b'\xFE\xFF', b'\xFF\xFE\x00\x00', b'\x00\x00\xFE\xFF')): return False
    return b'\x00' in chunk

# --- CONFIG AND PATHSPEC LOADING ---
config = load_configurations()
CODE_EXTENSIONS = set(config.get('code_extensions', []))
MAX_FILE_SIZE = config.get('max_file_size', 1000000)
exclude_spec = PathSpec.from_lines(GitWildMatchPattern, config.get('exclude_patterns', []))
include_spec = PathSpec.from_lines(GitWildMatchPattern, config.get('default_include_patterns', []))
# These are still useful for some simple checks in the GUI and logic
EXCLUDE_DIRS = [p.rstrip('/') for p in config.get('exclude_patterns', []) if p.endswith('/')]
EXCLUDE_FILES = [p for p in config.get('exclude_patterns', []) if not p.endswith('/')]
EXCLUDE_PATTERNS = EXCLUDE_FILES # Simplified for backward compatibility
INCLUDE_FILES = config.get('default_include_patterns', [])
INCLUDE_DIRS = [p.rstrip('/') for p in INCLUDE_FILES if p.endswith('/')]
EXCLUDE_EXTENSIONS = [] # This concept is now handled by patterns

# --- REWRITTEN collect_all_files FOR LAZY LOADING ---
def collect_all_files() -> List[Tuple[str, str, bool]]:
    """
    Collects files and directories. For excluded directories, it returns them as
    a single entry without their contents, allowing the GUI to lazy-load them.
    Returns a list of (absolute_path, relative_path, is_checked_by_default).
    """
    all_paths = []
    root_dir = os.getcwd()
    seen_paths = set()
    logging.info(f"Starting initial fast scan in: {root_dir}")

    for root, dirs, files in os.walk(root_dir, topdown=True):
        rel_root = os.path.relpath(root, root_dir)
        if rel_root == '.': rel_root = ''

        # Add the directory itself unless it's the root
        if rel_root and root not in seen_paths:
             all_paths.append((root, rel_root, False))
             seen_paths.add(root)

        # Prune directories from the walk
        dirs_to_prune = []
        for d in dirs:
            rel_dir_path = os.path.join(rel_root, d)
            if exclude_spec.match_file(rel_dir_path + '/'):
                dirs_to_prune.append(d)
        dirs[:] = [d for d in dirs if d not in dirs_to_prune]

        # Process all items (unpruned dirs and files)
        for name in dirs + files:
            abs_path = os.path.join(root, name)
            rel_path = os.path.join(rel_root, name)
            if abs_path in seen_paths: continue

            # Determine default check state
            is_checked = False
            check_path = rel_path + '/' if os.path.isdir(abs_path) else rel_path

            if include_spec.match_file(check_path):
                is_checked = True
            elif os.path.isfile(abs_path) and os.path.splitext(name)[1].lower() in CODE_EXTENSIONS:
                 is_checked = True

            # Final filters for files
            if os.path.isfile(abs_path):
                if is_binary_file(abs_path) or os.path.getsize(abs_path) > MAX_FILE_SIZE:
                    is_checked = False

            all_paths.append((abs_path, rel_path, is_checked))
            seen_paths.add(abs_path)

    logging.info(f"Initial scan collected {len(all_paths)} items.")
    return all_paths

def is_excluded_directory(path: str) -> bool:
    """Simplified check used by GUI folder-click logic."""
    dir_name = os.path.basename(path)
    return any(fnmatch.fnmatch(dir_name, pat) for pat in EXCLUDE_DIRS)

def matches_pattern(filename: str, pattern: str) -> bool:
    """Helper used by GUI logic."""
    return fnmatch.fnmatch(filename.lower(), pattern.lower())
