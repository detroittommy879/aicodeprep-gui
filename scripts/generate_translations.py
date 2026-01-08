"""
Script to generate translation files for aicodeprep-gui.

This script:
1. Extracts translatable strings from Python files
2. Creates/updates .ts translation files
3. Compiles .ts files to .qm files for runtime use
"""
import os
import subprocess
import sys
from pathlib import Path


def main():
    """Generate translation files."""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    gui_dir = project_root / "aicodeprep_gui"
    trans_dir = project_root / "aicodeprep_gui" / "i18n" / "translations"

    # Ensure translations directory exists
    trans_dir.mkdir(parents=True, exist_ok=True)

    # Find lupdate and lrelease tools
    venv_dir = project_root / ".venv"
    if sys.platform == "win32":
        lupdate = venv_dir / "Lib" / "site-packages" / "PySide6" / "lupdate.exe"
        lrelease = venv_dir / "Lib" / "site-packages" / "PySide6" / "lrelease.exe"
    else:
        lupdate = venv_dir / "lib" / \
            f"python{sys.version_info.major}.{sys.version_info.minor}" / \
            "site-packages" / "PySide6" / "lupdate"
        lrelease = venv_dir / "lib" / \
            f"python{sys.version_info.major}.{sys.version_info.minor}" / \
            "site-packages" / "PySide6" / "lrelease"

    if not lupdate.exists():
        print(f"Error: lupdate not found at {lupdate}")
        print("Make sure PySide6 is installed")
        return 1

    # List of all bundled languages (top 20)
    languages = [
        'en', 'es', 'fr', 'de', 'pt', 'it', 'ru',
        'zh_CN', 'zh_TW', 'ja', 'ko', 'ar', 'hi',
        'tr', 'pl', 'nl', 'sv', 'da', 'fi', 'no'
    ]

    # Find all Python files in gui directory
    py_files = []
    for py_file in gui_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            py_files.append(str(py_file))

    print(f"Found {len(py_files)} Python files")

    # Generate .ts files for each language
    for lang in languages:
        ts_file = trans_dir / f"aicodeprep_gui_{lang}.ts"
        print(f"\nGenerating {ts_file.name}...")

        # Build lupdate command
        cmd = [str(lupdate), "-no-obsolete"]
        cmd.extend(py_files)
        cmd.extend(["-ts", str(ts_file)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Successfully created/updated {ts_file.name}")
            else:
                print(f"✗ Error creating {ts_file.name}")
                print(result.stderr)
        except Exception as e:
            print(f"✗ Exception: {e}")

    # Compile .ts files to .qm files
    print("\nCompiling translation files...")
    if not lrelease.exists():
        print(f"Warning: lrelease not found at {lrelease}")
        print("Translation files (.ts) created but not compiled to .qm")
        return 0

    for lang in languages:
        ts_file = trans_dir / f"aicodeprep_gui_{lang}.ts"
        qm_file = trans_dir / f"aicodeprep_gui_{lang}.qm"

        if not ts_file.exists():
            continue

        print(f"Compiling {ts_file.name} -> {qm_file.name}...")

        try:
            result = subprocess.run([str(lrelease), str(ts_file), "-qm", str(qm_file)],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Successfully compiled {qm_file.name}")
            else:
                print(f"✗ Error compiling {qm_file.name}")
                print(result.stderr)
        except Exception as e:
            print(f"✗ Exception: {e}")

    print("\n=== Translation file generation complete ===")
    print(f"Translation files are in: {trans_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
