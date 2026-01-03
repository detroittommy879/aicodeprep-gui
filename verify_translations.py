#!/usr/bin/env python3
"""
Script to verify that all user-facing strings are properly marked for translation.
This script searches for strings that should be wrapped with self.tr() or similar
translation methods.
"""

import os
import re
from pathlib import Path


def find_untranslated_strings(file_path):
    """Find strings that should be translated but aren't marked properly."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    untranslated_strings = []
    lines = content.split('\n')

    # Common patterns for user-facing strings that should be translated
    string_patterns = [
        # Qt widget constructors with strings
        r'Q[A-Z][a-zA-Z]*\(["\']([^"\']+)["\']\)',
        r'setWindowTitle\(["\']([^"\']+)["\']\)',
        r'setText\(["\']([^"\']+)["\']\)',
        r'setToolTip\(["\']([^"\']+)["\']\)',
        r'setPlaceholderText\(["\']([^"\']+)["\']\)',
        r'QMessageBox\.[a-zA-Z]+\(["\'][^"\']*["\'],\s*["\']([^"\']+)["\']',
        r'QInputDialog\.[a-zA-Z]+\([^,]+,\s*["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']',
    ]

    # Look for literal strings in UI contexts
    ui_contexts = [
        'setWindowTitle', 'setText', 'setToolTip', 'setPlaceholderText',
        'QMessageBox', 'QInputDialog', 'QLabel', 'QPushButton',
        'QCheckBox', 'QGroupBox', 'QAction'
    ]

    for i, line in enumerate(lines, 1):
        # Skip comments and empty lines
        if line.strip().startswith('#') or not line.strip():
            continue

        # Check if this line contains UI string contexts
        if any(context in line for context in ui_contexts):
            # Look for literal strings not wrapped in self.tr() or tr()
            # This is a simplified check - in practice, you'd want more sophisticated parsing
            literal_strings = re.findall(r'["\']([^"\']{3,})["\']', line)
            for string in literal_strings:
                # Skip common non-user strings
                if (string in ['UTF-8', 'utf-8', 'config', 'settings'] or
                        string.startswith('.') or string.startswith('/')):
                    continue

                # Check if the string is already wrapped with translation
                if not ('tr(' in line or 'self.tr(' in line):
                    untranslated_strings.append({
                        'line': i,
                        'string': string,
                        'context': line.strip()
                    })

    return untranslated_strings


def scan_project_for_translations(root_dir):
    """Scan the entire project for translation issues."""
    gui_files = []
    untranslated_files = {}

    # Find all Python files in gui directory
    gui_dir = Path(root_dir) / 'aicodeprep_gui' / 'gui'
    if gui_dir.exists():
        for py_file in gui_dir.rglob('*.py'):
            gui_files.append(py_file)

    # Also check main files
    main_files = [
        Path(root_dir) / 'aicodeprep_gui' / 'main.py',
        Path(root_dir) / 'aicodeprep_gui' / 'gui' / 'main_window.py',
        Path(root_dir) / 'aicodeprep_gui' /
        'gui' / 'components' / 'dialogs.py',
    ]

    all_files = gui_files + [f for f in main_files if f.exists()]

    for file_path in all_files:
        untranslated = find_untranslated_strings(file_path)
        if untranslated:
            untranslated_files[str(file_path)] = untranslated

    return untranslated_files


def main():
    """Main function to run the translation verification."""
    print("🔍 Scanning project for untranslated strings...")
    print("=" * 50)

    untranslated_files = scan_project_for_translations('.')

    if untranslated_files:
        print("❌ Found potentially untranslated strings:")
        print()
        for file_path, strings in untranslated_files.items():
            print(f"📄 {file_path}:")
            for item in strings:
                print(f"   Line {item['line']}: '{item['string']}'")
                print(f"   Context: {item['context']}")
                print()
        print(f"Total files with issues: {len(untranslated_files)}")
    else:
        print("✅ No untranslated strings found (based on simple pattern matching)")
        print("Note: This is a basic check. Manual verification is still recommended.")

    print("\n💡 Tip: Remember to wrap user-facing strings with self.tr() in Qt applications")


if __name__ == '__main__':
    main()
