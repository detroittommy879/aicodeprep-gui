"""scripts/generate_translations.py

Generate and/or compile Qt translation files for aicodeprep-gui.

By default, this script updates the *.ts files from source using Qt's lupdate,
then compiles *.ts -> *.qm using lrelease.

If you already edited the *.ts files (translations are ready), use:
  uv run python scripts/generate_translations.py --compile-only

This avoids touching the *.ts files and only regenerates the runtime *.qm.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Iterable, Optional


DEFAULT_LANGUAGES = [
    # All bundled languages (top 20)
    'en', 'es', 'fr', 'de', 'pt', 'it', 'ru',
    'zh_CN', 'zh_TW', 'ja', 'ko', 'ar', 'hi',
    'tr', 'pl', 'nl', 'sv', 'da', 'fi', 'no'
]


def _find_qt_tool(tool: str, project_root: Path) -> Optional[Path]:
    """Find a Qt tool executable/script.

    Prefers PATH (works well with `uv run`), but also falls back to PySide6
    packaged tools inside the venv/site-packages.
    """
    # 1) PATH (e.g., `.venv/Scripts/pyside6-lrelease.exe`)
    found = which(tool)
    if found:
        return Path(found)

    # 2) PySide6 packaged tools inside site-packages
    try:
        import PySide6  # type: ignore

        pyside_dir = Path(PySide6.__file__).resolve().parent
        candidates = []
        if sys.platform == "win32":
            candidates.extend([
                pyside_dir / f"{tool}.exe",
                pyside_dir / "Qt" / "libexec" / f"{tool}.exe",
            ])
        else:
            candidates.extend([
                pyside_dir / tool,
                pyside_dir / "Qt" / "libexec" / tool,
            ])
        for candidate in candidates:
            if candidate.exists():
                return candidate
    except Exception:
        pass

    # 3) Legacy fallback: common `.venv` layout
    venv_dir = project_root / ".venv"
    if sys.platform == "win32":
        legacy = venv_dir / "Lib" / "site-packages" / "PySide6" / f"{tool}.exe"
    else:
        legacy = venv_dir / "lib" / \
            f"python{sys.version_info.major}.{sys.version_info.minor}" / \
            "site-packages" / "PySide6" / tool
    if legacy.exists():
        return legacy

    return None


def _iter_py_files(gui_dir: Path) -> Iterable[str]:
    for py_file in gui_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        yield str(py_file)


def _compile_ts_to_qm(lrelease: Path, ts_file: Path, qm_file: Path) -> bool:
    result = subprocess.run(
        [str(lrelease), str(ts_file), "-qm", str(qm_file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if stderr:
            print(stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and/or compile Qt translation files (.ts/.qm)."
    )
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Only compile existing .ts files to .qm (does not run lupdate).",
    )
    parser.add_argument(
        "--update-ts-only",
        action="store_true",
        help="Only update .ts files from source (does not compile to .qm).",
    )
    parser.add_argument(
        "--languages",
        nargs="*",
        default=None,
        help="Optional list of language codes to process (default: bundled set).",
    )
    args = parser.parse_args()

    if args.compile_only and args.update_ts_only:
        print("Error: --compile-only and --update-ts-only are mutually exclusive")
        return 2

    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    gui_dir = project_root / "aicodeprep_gui"
    trans_dir = project_root / "aicodeprep_gui" / "i18n" / "translations"

    # Ensure translations directory exists
    trans_dir.mkdir(parents=True, exist_ok=True)

    # Determine language list
    languages = args.languages if args.languages else DEFAULT_LANGUAGES

    # Find lupdate/lrelease tools (prefer PATH via `uv run`)
    lupdate = None if args.compile_only else _find_qt_tool(
        "lupdate", project_root)
    lrelease = None if args.update_ts_only else _find_qt_tool(
        "lrelease", project_root)

    # Also accept the PySide6 wrappers if present (more common on Windows)
    if lupdate is None and not args.compile_only:
        lupdate = _find_qt_tool("pyside6-lupdate", project_root)
    if lrelease is None and not args.update_ts_only:
        lrelease = _find_qt_tool("pyside6-lrelease", project_root)

    if not args.compile_only and not lupdate:
        print("Error: lupdate not found (tried PATH and PySide6 bundled tools)")
        print("Make sure PySide6 is installed in the active environment")
        return 1

    if not args.compile_only:
        py_files = list(_iter_py_files(gui_dir))
        print(f"Found {len(py_files)} Python files")

        # Generate/update .ts files for each language
        for lang in languages:
            ts_file = trans_dir / f"aicodeprep_gui_{lang}.ts"
            print(f"\nUpdating {ts_file.name} via lupdate...")

            cmd = [str(lupdate), "-no-obsolete"]
            cmd.extend(py_files)
            cmd.extend(["-ts", str(ts_file)])

            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✓ Updated {ts_file.name}")
                else:
                    print(f"✗ Error updating {ts_file.name}")
                    stderr = (result.stderr or "").strip()
                    if stderr:
                        print(stderr)
            except Exception as e:
                print(f"✗ Exception: {e}")

    if not args.update_ts_only:
        print("\nCompiling .ts -> .qm...")
        if not lrelease:
            print("Warning: lrelease not found (tried PATH and PySide6 bundled tools)")
            print("Translation files (.ts) were not compiled to .qm")
            return 0

        for lang in languages:
            ts_file = trans_dir / f"aicodeprep_gui_{lang}.ts"
            qm_file = trans_dir / f"aicodeprep_gui_{lang}.qm"

            if not ts_file.exists():
                continue

            print(f"Compiling {ts_file.name} -> {qm_file.name}...")
            ok = _compile_ts_to_qm(lrelease, ts_file, qm_file)
            if ok:
                print(f"✓ Compiled {qm_file.name}")
            else:
                print(f"✗ Failed compiling {qm_file.name}")

    print("\n=== Translation file generation complete ===")
    print(f"Translation files are in: {trans_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
