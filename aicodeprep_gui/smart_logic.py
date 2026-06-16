from importlib import resources
import os
import sys
import logging
from typing import Collection, List, Tuple, Optional
import fnmatch

# New imports for the refactoring
import toml
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern


def get_config_path():
    """Get the path to the default configuration file."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        config_path = os.path.join(
            base_path, 'aicodeprep_gui', 'data', 'default_config.toml')
    else:
        try:
            with resources.path('aicodeprep_gui.data', 'default_config.toml') as config_file:
                config_path = str(config_file)
        except ModuleNotFoundError:
            config_path = os.path.join(os.path.dirname(
                __file__), 'data', 'default_config.toml')
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


def load_configurations(root_dir: Optional[str] = None) -> dict:
    """Load default config, then load project config from the target root and merge them.

    Config is merged in order of priority (last wins):
    1. Built-in defaults
    2. Legacy aicodeprep-gui.toml at project root (backward compat)
    3. New .aicp/config.toml at project root (preferred location)
    """
    default_config_path = get_config_path()
    config = load_config_from_path(default_config_path)
    if not config:
        logging.critical("Failed to load default configuration. Exiting.")
        sys.exit("Could not load the default configuration file.")
    scan_root = os.path.abspath(root_dir or os.getcwd())

    # Legacy location - load first so .aicp/config.toml can override it
    legacy_config_path = os.path.join(scan_root, 'aicodeprep-gui.toml')
    legacy_config = load_config_from_path(legacy_config_path)
    if legacy_config:
        logging.info(
            f"Found legacy user configuration at {legacy_config_path}. Merging settings.")
        config.update(legacy_config)

    # New preferred location - takes priority over legacy
    aicp_config_path = os.path.join(scan_root, '.aicp', 'config.toml')
    aicp_config = load_config_from_path(aicp_config_path)
    if aicp_config:
        logging.info(
            f"Found project configuration at {aicp_config_path}. Merging settings.")
        config.update(aicp_config)

    return config


def is_binary_file(filepath: str) -> bool:
    """Return True if this file is likely binary."""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
    except OSError:
        return False
    if chunk.startswith((b'\xEF\xBB\xBF', b'\xFF\xFE', b'\xFE\xFF', b'\xFF\xFE\x00\x00', b'\x00\x00\xFE\xFF')):
        return False
    return b'\x00' in chunk


def _apply_runtime_config(config_dict: dict) -> None:
    global config, CODE_EXTENSIONS, MAX_FILE_SIZE
    global exclude_spec, include_spec
    global EXCLUDE_DIRS, EXCLUDE_FILES, EXCLUDE_PATTERNS, INCLUDE_FILES, INCLUDE_DIRS, EXCLUDE_EXTENSIONS

    config = config_dict
    CODE_EXTENSIONS = set(config.get('code_extensions', []))
    MAX_FILE_SIZE = config.get('max_file_size', 1000000)
    exclude_spec = PathSpec.from_lines(
        GitWildMatchPattern, config.get('exclude_patterns', []))
    include_spec = PathSpec.from_lines(
        GitWildMatchPattern, config.get('default_include_patterns', []))
    EXCLUDE_DIRS = [
        p.rstrip('/') for p in config.get('exclude_patterns', []) if p.endswith('/')]
    EXCLUDE_FILES = [p for p in config.get(
        'exclude_patterns', []) if not p.endswith('/')]
    EXCLUDE_PATTERNS = EXCLUDE_FILES
    INCLUDE_FILES = config.get('default_include_patterns', [])
    INCLUDE_DIRS = [p.rstrip('/') for p in INCLUDE_FILES if p.endswith('/')]
    EXCLUDE_EXTENSIONS = []


def refresh_runtime_config(root_dir: Optional[str] = None) -> dict:
    """Refresh module-level scan settings for the active target directory."""
    config_dict = load_configurations(root_dir)
    _apply_runtime_config(config_dict)
    return config_dict


def _normalize_saved_paths(checked_relpaths: Optional[Collection[str]]) -> set[str]:
    return {
        os.path.normpath(path)
        for path in (checked_relpaths or set())
        if path
    }


def _is_excluded_dir(rel_dir_path: str) -> bool:
    return exclude_spec.match_file(rel_dir_path + '/')


def _should_check_file(
    abs_path: str,
    rel_path: str,
    name: str,
    saved_checked_paths: Optional[set[str]] = None,
    prefer_saved_selection: bool = False,
) -> bool:
    if prefer_saved_selection:
        return rel_path in (saved_checked_paths or set())

    if include_spec.match_file(rel_path):
        is_checked = True
    else:
        is_checked = os.path.splitext(name)[1].lower() in CODE_EXTENSIONS

    if is_checked:
        try:
            if is_binary_file(abs_path) or os.path.getsize(abs_path) > MAX_FILE_SIZE:
                return False
        except OSError:
            return False

    return is_checked


def collect_seed_paths(
    root_dir: Optional[str] = None,
    checked_relpaths: Optional[Collection[str]] = None,
) -> List[Tuple[str, str, bool]]:
    """Build a sparse initial tree from top-level entries plus saved checked files."""
    seed_paths = []
    root_dir = os.path.abspath(root_dir or os.getcwd())
    refresh_runtime_config(root_dir)
    saved_checked_paths = _normalize_saved_paths(checked_relpaths)
    seen_paths = set()

    logging.info(
        "Using saved project preferences to seed tree in: %s", root_dir)

    try:
        root_entries = sorted(os.listdir(root_dir))
    except OSError as e:
        logging.error("Failed to list project root %s: %s", root_dir, e)
        return seed_paths

    for name in root_entries:
        abs_path = os.path.join(root_dir, name)
        rel_path = name

        if os.path.isdir(abs_path) and _is_excluded_dir(rel_path):
            continue

        is_checked = False
        if os.path.isfile(abs_path):
            is_checked = _should_check_file(
                abs_path,
                rel_path,
                name,
                saved_checked_paths=saved_checked_paths,
                prefer_saved_selection=True,
            )

        seed_paths.append((abs_path, rel_path, is_checked))
        seen_paths.add(abs_path)

    missing_saved_paths = 0
    for rel_path in sorted(saved_checked_paths):
        abs_path = os.path.join(root_dir, rel_path)
        if not os.path.isfile(abs_path):
            missing_saved_paths += 1
            continue

        parts = rel_path.split(os.sep)
        parent_rel_path = ""
        for part in parts[:-1]:
            parent_rel_path = os.path.join(
                parent_rel_path, part) if parent_rel_path else part
            parent_abs_path = os.path.join(root_dir, parent_rel_path)
            if not os.path.isdir(parent_abs_path) or parent_abs_path in seen_paths:
                continue
            seed_paths.append((parent_abs_path, parent_rel_path, False))
            seen_paths.add(parent_abs_path)

        if abs_path not in seen_paths:
            seed_paths.append((abs_path, rel_path, True))
            seen_paths.add(abs_path)

    seed_paths.sort(key=lambda item: (item[1].count(os.sep), item[1].lower()))
    logging.info(
        "Seeded tree with %d visible entries from %d saved selections (%d missing).",
        len(seed_paths),
        len(saved_checked_paths),
        missing_saved_paths,
    )
    return seed_paths


# --- CONFIG AND PATHSPEC LOADING ---
config = {}
CODE_EXTENSIONS = set()
MAX_FILE_SIZE = 1000000
exclude_spec = PathSpec.from_lines(GitWildMatchPattern, [])
include_spec = PathSpec.from_lines(GitWildMatchPattern, [])
EXCLUDE_DIRS = []
EXCLUDE_FILES = []
EXCLUDE_PATTERNS = []
INCLUDE_FILES = []
INCLUDE_DIRS = []
EXCLUDE_EXTENSIONS = []
LAST_SCAN_BACKEND = "unknown"

refresh_runtime_config()

# --- REWRITTEN collect_all_files FOR LAZY LOADING ---


def get_last_scan_backend() -> str:
    return LAST_SCAN_BACKEND


def _rust_scan_enabled() -> bool:
    try:
        from aicodeprep_gui.user_settings import get_setting

        backend_enabled = bool(get_setting("rust_backend", "enabled", True))
        legacy_toggle_enabled = bool(get_setting(
            "pro_options", "rust_fast_processing", True))
        return backend_enabled and legacy_toggle_enabled
    except Exception as exc:
        logging.debug("Could not read Rust scan setting: %s", exc)
        return True


def _collect_all_files_rust(root_dir: str, config_dict: dict) -> Optional[List[Tuple[str, str, bool]]]:
    if not _rust_scan_enabled():
        logging.info("Rust file scan disabled; using Python scan.")
        return None

    try:
        from aicodeprep_gui.rust_backend import scan_with_rust_worker

        result = scan_with_rust_worker(
            root_dir,
            config_dict,
            respect_gitignore=bool(config_dict.get("respect_gitignore", False)),
        )
    except Exception as exc:
        logging.warning("Rust file scan unavailable, falling back to Python: %s", exc)
        return None

    if not result.ok or result.files is None:
        logging.info("Rust file scan unavailable, falling back to Python: %s", result.error)
        return None

    logging.info("Using Rust worker for directory scan: collected %d items.", len(result.files))
    return result.files


def _collect_all_files_python(root_dir: str) -> List[Tuple[str, str, bool]]:
    """
    Collects files and directories. For excluded directories, it returns them as
    a single entry without their contents, allowing the GUI to lazy-load them.
    Returns a list of (absolute_path, relative_path, is_checked_by_default).
    """
    all_paths = []
    seen_paths = set()
    logging.info(f"Starting Python fallback scan in: {root_dir}")

    for root, dirs, files in os.walk(root_dir, topdown=True):
        rel_root = os.path.relpath(root, root_dir)
        if rel_root == '.':
            rel_root = ''

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
            if abs_path in seen_paths:
                continue

            # Determine default check state
            is_checked = False
            check_path = rel_path + \
                '/' if os.path.isdir(abs_path) else rel_path

            if include_spec.match_file(check_path):
                is_checked = True
            elif os.path.isfile(abs_path) and os.path.splitext(name)[1].lower() in CODE_EXTENSIONS:
                is_checked = True

            # Final filters for files
            if os.path.isfile(abs_path):
                is_checked = _should_check_file(abs_path, rel_path, name)

            all_paths.append((abs_path, rel_path, is_checked))
            seen_paths.add(abs_path)

    logging.info(f"Initial scan collected {len(all_paths)} items.")
    return all_paths


def collect_all_files(root_dir: Optional[str] = None) -> List[Tuple[str, str, bool]]:
    global LAST_SCAN_BACKEND
    root_dir = os.path.abspath(root_dir or os.getcwd())
    config_dict = refresh_runtime_config(root_dir)
    logging.info("Starting initial scan in: %s", root_dir)

    rust_paths = _collect_all_files_rust(root_dir, config_dict)
    if rust_paths is not None:
        LAST_SCAN_BACKEND = "Rust worker"
        return rust_paths

    LAST_SCAN_BACKEND = "Python fallback"
    return _collect_all_files_python(root_dir)


def is_excluded_directory(path: str) -> bool:
    """Simplified check used by GUI folder-click logic."""
    dir_name = os.path.basename(path)
    return any(fnmatch.fnmatch(dir_name, pat) for pat in EXCLUDE_DIRS)


def matches_pattern(filename: str, pattern: str) -> bool:
    """Helper used by GUI logic."""
    return fnmatch.fnmatch(filename.lower(), pattern.lower())
