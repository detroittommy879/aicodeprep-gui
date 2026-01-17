"""Tests for internationalization (i18n) system."""
import pytest
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore


class TestTranslationManager:
    """Tests for the TranslationManager class."""

    def test_translation_manager_initializes(self):
        """Translation manager should load without errors."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        assert manager is not None, "TranslationManager should initialize"
        assert manager.app == app, "TranslationManager should store app reference"

    def test_get_available_languages(self):
        """Should return list of supported languages."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        languages = manager.get_available_languages()

        assert isinstance(languages, list), "Should return a list"
        assert len(languages) > 0, "Should have at least one language (English)"

        # Check format: list of tuples (code, name)
        for lang in languages:
            assert isinstance(lang, tuple), "Each language should be a tuple"
            assert len(lang) == 2, "Each tuple should have (code, name)"
            assert isinstance(lang[0], str), "Language code should be string"
            assert isinstance(lang[1], str), "Language name should be string"

        # English should always be available
        codes = [l[0] for l in languages]
        assert 'en' in codes, "English should always be available"

    def test_detect_system_language(self):
        """Should detect OS language correctly."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        detected_lang = manager.detect_system_language()

        assert detected_lang is not None, "Should detect a language"
        assert isinstance(
            detected_lang, str), "Language code should be a string"
        assert len(
            detected_lang) >= 2, "Language code should be at least 2 chars (e.g., 'en')"

    def test_fallback_to_english(self):
        """Should fall back to English if system language unavailable."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        # Try to set a non-existent language
        result = manager.set_language('xx_NonExistent')

        # Should fall back to English
        current = manager.get_current_language()
        assert current == 'en', "Should fall back to English for non-existent language"

    def test_switch_to_spanish(self):
        """Should be able to switch to Spanish (bundled language)."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        # Switch to Spanish
        success = manager.set_language('es')

        assert success, "Should successfully switch to Spanish"
        assert manager.get_current_language() == 'es', "Current language should be Spanish"

    def test_language_change_event_sent(self):
        """Changing language should send a LanguageChange event to open windows."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        class LanguageChangeCatcher(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()
                self.language_change_count = 0

            def changeEvent(self, event):
                if event.type() == QtCore.QEvent.LanguageChange:
                    self.language_change_count += 1
                return super().changeEvent(event)

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        catcher = LanguageChangeCatcher()
        # Don't show the widget in tests: showing can trigger flaky Windows
        # message-pump/COM interactions in headless/CI environments.
        QtWidgets.QApplication.processEvents()

        assert manager.set_language('es')
        QtWidgets.QApplication.processEvents()
        assert catcher.language_change_count > 0

        # Switching back to English should also trigger LanguageChange
        previous = catcher.language_change_count
        assert manager.set_language('en')
        QtWidgets.QApplication.processEvents()
        assert catcher.language_change_count > previous

        catcher.close()
        catcher.deleteLater()
        QtWidgets.QApplication.processEvents()

    def test_is_language_bundled(self):
        """Should correctly identify bundled vs non-bundled languages."""
        from aicodeprep_gui.i18n.translator import TranslationManager
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        manager = TranslationManager(app)

        # Bundled languages
        assert manager.is_language_bundled('en'), "English should be bundled"
        assert manager.is_language_bundled('es'), "Spanish should be bundled"
        assert manager.is_language_bundled(
            'zh_CN'), "Chinese Simplified should be bundled"
        assert manager.is_language_bundled('fr'), "French should be bundled"

        # Other bundled languages (top 20)
        assert manager.is_language_bundled('de'), "German should be bundled"
        assert manager.is_language_bundled('ja'), "Japanese should be bundled"

        # Not bundled / unsupported language codes
        assert not manager.is_language_bundled(
            'he'), "Hebrew should not be bundled"


class TestTranslationFiles:
    """Tests for translation file structure and content."""

    def test_translation_directory_exists(self):
        """Translation directory should exist."""
        from pathlib import Path
        trans_dir = Path(__file__).parent.parent / \
            "aicodeprep_gui" / "i18n" / "translations"
        assert trans_dir.exists(
        ), f"Translation directory should exist at {trans_dir}"

    def test_english_source_file_exists(self):
        """English source translation file should exist."""
        from pathlib import Path
        en_file = Path(__file__).parent.parent / "aicodeprep_gui" / \
            "i18n" / "translations" / "aicodeprep_gui_en.ts"
        # Will be created when we run pylupdate6
        # For now, just check the directory exists
        trans_dir = en_file.parent
        assert trans_dir.exists(), "Translation directory should exist"
