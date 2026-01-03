"""
Translation Manager for aicodeprep-gui.

Handles loading, switching, and managing UI translations for multiple languages.
Supports both bundled languages (shipped with app) and on-demand downloads.
"""
import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTranslator, QLocale, QSettings


logger = logging.getLogger(__name__)


class TranslationManager:
    """Manages UI translations for the application."""

    # Bundled languages (shipped with the application)
    BUNDLED_LANGUAGES = {
        'en': 'English',
        'es': 'Español (Spanish)',
        'zh_CN': '简体中文 (Chinese Simplified)',
        'fr': 'Français (French)'
    }

    # On-demand languages (downloaded when user selects them)
    ONDEMAND_LANGUAGES = {
        'de': 'Deutsch (German)',
        'ja': '日本語 (Japanese)',
        'ko': '한국어 (Korean)',
        'ar': 'العربية (Arabic)',
        'he': 'עברית (Hebrew)',
        'ru': 'Русский (Russian)',
        'pt': 'Português (Portuguese)',
        'zh_TW': '繁體中文 (Chinese Traditional)',
        'it': 'Italiano (Italian)'
    }

    def __init__(self, app: QtWidgets.QApplication):
        """
        Initialize the Translation Manager.

        Args:
            app: The QApplication instance
        """
        self.app = app
        self.current_translator = None
        self.current_language = 'en'  # Default to English
        self.settings = QSettings("aicodeprep-gui", "Language")

        # Get translations directory
        self.translations_dir = self._get_translations_directory()

        logger.info(
            f"TranslationManager initialized. Translations dir: {self.translations_dir}")

    def _get_translations_directory(self) -> Path:
        """
        Get the directory where translation files are stored.

        Returns:
            Path to translations directory
        """
        # For bundled translations (inside package)
        package_dir = Path(__file__).parent
        bundled_dir = package_dir / "translations"
        bundled_dir.mkdir(parents=True, exist_ok=True)
        return bundled_dir

    def _get_user_translations_directory(self) -> Path:
        """
        Get the user directory for downloaded translations.

        Returns:
            Path to user translations directory
        """
        # Platform-specific user data directory
        if os.name == 'nt':  # Windows
            user_dir = Path(os.environ.get('APPDATA', '~')) / \
                'aicodeprep-gui' / 'translations'
        else:  # macOS/Linux
            user_dir = Path.home() / '.aicodeprep-gui' / 'translations'

        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_available_languages(self) -> List[Tuple[str, str]]:
        """
        Get list of all available languages (bundled + downloaded).

        Returns:
            List of tuples: [(language_code, language_name), ...]
        """
        available = []

        # Add bundled languages
        for code, name in self.BUNDLED_LANGUAGES.items():
            available.append((code, name))

        # Check which on-demand languages are downloaded
        user_trans_dir = self._get_user_translations_directory()
        for code, name in self.ONDEMAND_LANGUAGES.items():
            trans_file = user_trans_dir / f"aicodeprep_gui_{code}.qm"
            if trans_file.exists():
                name_with_mark = f"{name} ✓"  # Mark as downloaded
                available.append((code, name_with_mark))
            else:
                name_with_download = f"{name} (download)"
                available.append((code, name_with_download))

        return available

    def is_language_available(self, lang_code: str) -> bool:
        """
        Check if a language is available (bundled or downloaded).

        Args:
            lang_code: Language code (e.g., 'en', 'es', 'zh_CN')

        Returns:
            True if language is available
        """
        if lang_code in self.BUNDLED_LANGUAGES:
            return True

        if lang_code in self.ONDEMAND_LANGUAGES:
            user_trans_dir = self._get_user_translations_directory()
            trans_file = user_trans_dir / f"aicodeprep_gui_{lang_code}.qm"
            return trans_file.exists()

        return False

    def is_language_bundled(self, lang_code: str) -> bool:
        """
        Check if a language is bundled with the application.

        Args:
            lang_code: Language code

        Returns:
            True if language is bundled
        """
        return lang_code in self.BUNDLED_LANGUAGES

    def detect_system_language(self) -> str:
        """
        Detect the system's default language.

        Returns:
            Language code (e.g., 'en', 'es', 'zh_CN')
        """
        system_locale = QLocale.system()
        locale_name = system_locale.name()  # e.g., 'en_US', 'es_ES', 'zh_CN'

        logger.info(f"Detected system locale: {locale_name}")

        # Try exact match first
        if locale_name in self.BUNDLED_LANGUAGES or locale_name in self.ONDEMAND_LANGUAGES:
            return locale_name

        # Try language code only (first 2 chars)
        lang_code = locale_name.split('_')[0]

        # Check if base language is available
        all_codes = list(self.BUNDLED_LANGUAGES.keys()) + \
            list(self.ONDEMAND_LANGUAGES.keys())
        for code in all_codes:
            if code.startswith(lang_code):
                return code

        # Default to English
        return 'en'

    def download_language_if_needed(self, lang_code: str) -> bool:
        """
        Download a language file if it's an on-demand language.

        For now, this is a placeholder. In a real implementation, this would
        download from a CDN or GitHub releases.

        Args:
            lang_code: Language code to download

        Returns:
            True if download successful or not needed
        """
        # If it's bundled, no download needed
        if self.is_language_bundled(lang_code):
            return True

        # If already downloaded, no need
        if self.is_language_available(lang_code):
            logger.info(f"Language {lang_code} already downloaded")
            return True

        # Check if it's a valid on-demand language
        if lang_code not in self.ONDEMAND_LANGUAGES:
            logger.warning(f"Unknown language code: {lang_code}")
            return False

        # TODO: Implement actual download from CDN/GitHub
        logger.info(f"Would download language: {lang_code}")
        logger.info("Note: On-demand language download not yet implemented")
        return False

    def set_language(self, lang_code: str) -> bool:
        """
        Set the application language.

        Args:
            lang_code: Language code (e.g., 'en', 'es', 'zh_CN')

        Returns:
            True if language was successfully set
        """
        try:
            # Check if language is available
            if not self.is_language_available(lang_code):
                logger.warning(
                    f"Language {lang_code} not available, falling back to English")
                lang_code = 'en'

            # Remove current translator if any
            if self.current_translator:
                self.app.removeTranslator(self.current_translator)
                self.current_translator = None

            # For English, no translation file needed (it's the source language)
            if lang_code == 'en':
                self.current_language = 'en'
                self.settings.setValue("current_language", 'en')
                logger.info("Set language to English (source)")
                return True

            # Load translation file
            translator = QTranslator()

            # Determine where to load from
            if self.is_language_bundled(lang_code):
                trans_dir = self.translations_dir
            else:
                trans_dir = self._get_user_translations_directory()

            trans_file = trans_dir / f"aicodeprep_gui_{lang_code}.qm"

            if not trans_file.exists():
                logger.warning(f"Translation file not found: {trans_file}")
                self.current_language = 'en'
                self.settings.setValue("current_language", 'en')
                return False

            # Load the translation
            success = translator.load(str(trans_file))

            if not success:
                logger.error(f"Failed to load translation file: {trans_file}")
                self.current_language = 'en'
                self.settings.setValue("current_language", 'en')
                return False

            # Install the translator
            self.app.installTranslator(translator)
            self.current_translator = translator
            self.current_language = lang_code

            # Save to settings
            self.settings.setValue("current_language", lang_code)

            # Set layout direction for RTL languages
            if lang_code in ['ar', 'he']:
                self.app.setLayoutDirection(QtCore.Qt.RightToLeft)
            else:
                self.app.setLayoutDirection(QtCore.Qt.LeftToRight)

            logger.info(f"Successfully set language to: {lang_code}")
            return True

        except Exception as e:
            logger.error(f"Error setting language to {lang_code}: {e}")
            self.current_language = 'en'
            self.settings.setValue("current_language", 'en')
            return False

    def get_current_language(self) -> str:
        """
        Get the current application language.

        Returns:
            Current language code
        """
        return self.current_language

    def get_saved_language_preference(self) -> Optional[str]:
        """
        Get the user's saved language preference.

        Returns:
            Saved language code, or None if not set
        """
        return self.settings.value("current_language", None)

    def retranslate_ui(self):
        """
        Signal all windows to retranslate their UI.

        This sends a LanguageChange event to all widgets.
        """
        # Send LanguageChange event to all top-level widgets
        for widget in self.app.topLevelWidgets():
            event = QtCore.QEvent(QtCore.QEvent.LanguageChange)
            self.app.sendEvent(widget, event)

        logger.info("Retranslation event sent to all widgets")
