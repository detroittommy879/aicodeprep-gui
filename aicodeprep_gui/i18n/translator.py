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

    # All languages bundled with the application (top 20 world languages)
    # Fonts are handled by OS, so no size concerns
    BUNDLED_LANGUAGES = {
        'en': 'English',
        'es': 'Español (Spanish)',
        'fr': 'Français (French)',
        'de': 'Deutsch (German)',
        'pt': 'Português (Portuguese)',
        'it': 'Italiano (Italian)',
        'ru': 'Русский (Russian)',
        'uk': 'Українська (Ukrainian)',
        'zh_CN': '简体中文 (Chinese Simplified)',
        'zh_TW': '繁體中文 (Chinese Traditional)',
        'ja': '日本語 (Japanese)',
        'ko': '한국어 (Korean)',
        'ar': 'العربية (Arabic)',
        'hi': 'हिन्दी (Hindi)',
        'tr': 'Türkçe (Turkish)',
        'pl': 'Polski (Polish)',
        'nl': 'Nederlands (Dutch)',
        'sv': 'Svenska (Swedish)',
        'da': 'Dansk (Danish)',
        'fi': 'Suomi (Finnish)',
        'no': 'Norsk (Norwegian)'
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
        Get list of all available languages (all are bundled).

        Returns:
            List of tuples: [(language_code, language_name), ...]
        """
        # Return all bundled languages
        return [(code, name) for code, name in self.BUNDLED_LANGUAGES.items()]

    def is_language_available(self, lang_code: str) -> bool:
        """
        Check if a language is available (all are bundled now).

        Args:
            lang_code: Language code (e.g., 'en', 'es', 'zh_CN')

        Returns:
            True if language is available
        """
        return lang_code in self.BUNDLED_LANGUAGES

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
        if locale_name in self.BUNDLED_LANGUAGES:
            return locale_name

        # Try language code only (first 2 chars)
        lang_code = locale_name.split('_')[0]

        # Check if base language is available
        for code in self.BUNDLED_LANGUAGES.keys():
            if code.startswith(lang_code):
                return code

        # Default to English
        return 'en'

    def download_language_if_needed(self, lang_code: str) -> bool:
        """
        Check if language is available (no downloads needed, all bundled).

        Args:
            lang_code: Language code to check

        Returns:
            True if language is available
        """
        return self.is_language_available(lang_code)

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
                # Trigger live UI updates for already-open windows
                self.retranslate_ui()
                return True

            # Load translation file
            translator = QTranslator()

            # Determine where to load from (all bundled now)
            trans_dir = self.translations_dir

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
            # Trigger live UI updates for already-open windows
            self.retranslate_ui()
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
