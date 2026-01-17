"""scripts/gui_language_screenshot_loop.py

Run the real GUI, switch languages live, capture screenshots, and emit a simple
"untranslated strings" report.

This is intended for agent + human iteration loops:
- Launch main window
- Capture English baseline screenshot
- Switch language (uses TranslationManager.set_language)
- Capture screenshot for target language
- Dump a heuristic report of strings that stayed identical to English
- Close the app cleanly

Examples:
  uv run python scripts/gui_language_screenshot_loop.py --language es
  uv run python scripts/gui_language_screenshot_loop.py --languages es fr zh_CN --auto-close-ms 1500
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from PySide6 import QtCore, QtWidgets

from aicodeprep_gui.i18n.translator import TranslationManager
from aicodeprep_gui.utils.screenshot_helper import (
    capture_window_screenshot,
    get_screenshot_directory,
)


_ASCII_LETTERS_RE = re.compile(r"[A-Za-z]")
_ACCEL_RE = re.compile(r"&(?=\w)")
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class TextHit:
    class_name: str
    object_name: str
    text: str


def _normalize_text(text: str) -> str:
    # Remove Qt accelerator markers and normalize whitespace.
    text = _ACCEL_RE.sub("", text)
    text = text.replace("…", "...")
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def _looks_like_user_facing_english(text: str) -> bool:
    text = _normalize_text(text)
    if not text:
        return False
    if len(text) <= 2:
        return False
    if not _ASCII_LETTERS_RE.search(text):
        return False

    # Ignore pure punctuation/emoji/icon buttons.
    if all(not ch.isalnum() for ch in text):
        return False

    # Ignore paths / extensions / very code-ish tokens.
    if "/" in text or "\\" in text:
        return False
    if "." in text and " " not in text and len(text) <= 12:
        return False

    return True


def _is_allowed_english(text: str) -> bool:
    text = _normalize_text(text)

    # Brand/proper nouns / acronyms that are likely to remain English.
    allow = {
        "AI",
        "LLM",
        "aicodeprep-gui",
        "OpenAI",
        "GitHub",
        "Pro",
        "Flow",
        "JSON",
        "XML",
        "Markdown",
    }
    if text in allow:
        return True

    # Common patterns that are not translations.
    if re.fullmatch(r"[0-9.,:%]+", text):
        return True

    return False


def _iter_widget_text_hits(root: QtWidgets.QWidget) -> Iterable[TextHit]:
    widgets: List[QtWidgets.QWidget] = [root]
    widgets.extend(root.findChildren(QtWidgets.QWidget))

    for widget in widgets:
        class_name = widget.metaObject().className()
        object_name = widget.objectName() or ""

        # Common text-bearing widget APIs.
        for attr in ("text", "title", "windowTitle", "placeholderText"):
            getter = getattr(widget, attr, None)
            if callable(getter):
                try:
                    value = getter()
                except Exception:
                    continue
                if isinstance(value, str) and value:
                    yield TextHit(class_name, object_name, value)

        # Special-case QGroupBox.title() already covered; QPlainTextEdit placeholder:
        if hasattr(widget, "placeholderText") and callable(getattr(widget, "placeholderText")):
            # already handled above
            pass

    # Menubar actions + nested menus.
    try:
        menubar = root.menuBar() if hasattr(root, "menuBar") else None
    except Exception:
        menubar = None

    if menubar is not None:
        def walk_menu(menu: QtWidgets.QMenu) -> Iterable[QtWidgets.QAction]:
            for action in menu.actions():
                yield action
                sub = action.menu()
                if sub is not None:
                    yield from walk_menu(sub)

        for top_action in menubar.actions():
            if top_action.text():
                yield TextHit("QAction", "menubar", top_action.text())
            menu = top_action.menu()
            if menu is not None:
                for action in walk_menu(menu):
                    if action.text():
                        yield TextHit("QAction", "menu", action.text())


def _collect_text_set(root: QtWidgets.QWidget) -> set[str]:
    return {_normalize_text(hit.text) for hit in _iter_widget_text_hits(root)}


def _write_report(
    report_path: Path,
    language: str,
    english_texts: Sequence[TextHit],
    target_texts_set: set[str],
) -> None:
    lines: List[str] = []
    lines.append(f"UI i18n audit report")
    lines.append(f"timestamp: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"language: {language}")
    lines.append("")

    flagged: List[str] = []
    seen_norm: set[str] = set()

    for hit in english_texts:
        norm = _normalize_text(hit.text)
        if not norm or norm in seen_norm:
            continue
        seen_norm.add(norm)

        if norm not in target_texts_set:
            continue
        if not _looks_like_user_facing_english(norm):
            continue
        if _is_allowed_english(norm):
            continue

        flagged.append(norm)

    flagged.sort(key=str.lower)

    lines.append(f"flagged_unchanged_english_strings: {len(flagged)}")
    lines.append("")
    for text in flagged:
        lines.append(f"- {text}")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch GUI, switch language, capture screenshots, and emit an i18n report.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--language", help="Single language code (e.g. es)")
    group.add_argument(
        "--languages",
        nargs="+",
        help="Multiple language codes (e.g. es fr zh_CN)")

    parser.add_argument(
        "--auto-close-ms",
        type=int,
        default=2500,
        help="Milliseconds to keep the window open before closing (default: 2500).",
    )

    return parser.parse_args(argv)


def _ensure_test_mode_env() -> None:
    os.environ.setdefault("AICODEPREP_TEST_MODE", "1")
    os.environ.setdefault("AICODEPREP_NO_METRICS", "1")
    os.environ.setdefault("AICODEPREP_NO_UPDATES", "1")


def run_for_language(lang: str, auto_close_ms: int) -> tuple[str, str, str]:
    """Returns (baseline_screenshot, lang_screenshot, report_path)."""
    _ensure_test_mode_env()

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

    # Ensure translation manager exists on the app (matches runtime expectation).
    manager = getattr(app, "translation_manager", None)
    if not isinstance(manager, TranslationManager):
        manager = TranslationManager(app)
        app.translation_manager = manager

    from aicodeprep_gui.gui.main_window import FileSelectionGUI

    window = FileSelectionGUI([])
    window.show()
    QtWidgets.QApplication.processEvents()

    # Baseline in English
    manager.set_language("en")
    QtWidgets.QApplication.processEvents()

    english_hits = list(_iter_widget_text_hits(window))
    baseline_path = capture_window_screenshot(
        window, filename_prefix="ui_baseline_en")

    # Switch language
    manager.set_language(lang)
    QtWidgets.QApplication.processEvents()

    target_texts = _collect_text_set(window)
    lang_path = capture_window_screenshot(
        window, filename_prefix=f"ui_lang_{lang}")

    # Write report
    out_dir = get_screenshot_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = out_dir / f"ui_i18n_audit_{lang}_{timestamp}.txt"
    _write_report(report_path, lang, english_hits, target_texts)

    # Close
    def _close():
        try:
            window.close()
            window.deleteLater()
        finally:
            QtWidgets.QApplication.processEvents()
            app.quit()

    QtCore.QTimer.singleShot(max(0, auto_close_ms), _close)
    app.exec()

    return baseline_path, lang_path, str(report_path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    languages = []
    if args.languages:
        languages = args.languages
    elif args.language:
        languages = [args.language]
    else:
        languages = ["es"]

    for lang in languages:
        baseline, shot, report = run_for_language(lang, args.auto_close_ms)
        print(f"baseline: {baseline}")
        print(f"screenshot: {shot}")
        print(f"report: {report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
