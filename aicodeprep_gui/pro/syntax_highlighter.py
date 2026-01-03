"""Syntax highlighted text edit widget for Pro features."""
from PySide6 import QtWidgets, QtGui
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.util import ClassNotFound
import os
from aicodeprep_gui.apptheme import system_pref_is_dark


class SyntaxHighlightedTextEdit(QtWidgets.QTextEdit):
    """A QTextEdit with syntax highlighting using Pygments."""

    def __init__(self, parent=None, font_name="JetBrains Mono"):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        # Robust JetBrains Mono font selection
        font_family = font_name
        available_fonts = QtGui.QFontDatabase.families()
        if font_name not in available_fonts:
            for family in available_fonts:
                if "jetbrains" in family.lower() and "mono" in family.lower():
                    font_family = family
                    break

        # Set default font with explicit weight
        font = QtGui.QFont(font_family, 10)
        font.setStyleHint(QtGui.QFont.Monospace)
        font.setWeight(QtGui.QFont.Weight.ExtraLight)
        self.setFont(font)

        # Log font info for debugging
        import logging
        logging.info(
            f"SyntaxHighlightedTextEdit: Using font family '{font_family}' (requested: '{font_name}')")

        # Default syntax and theme
        self._syntax = "text"
        self._is_dark_mode = system_pref_is_dark()  # Track current theme
        self._update_theme()  # Set initial theme

        # Add flag to control syntax highlighting
        self._syntax_highlighting_enabled = True
        # Add flag to prevent recursion
        self._applying_highlighting = False

        # Connect text change signal
        self.textChanged.connect(self._highlight_text)

    def set_syntax(self, syntax):
        """Set the syntax for highlighting."""
        self._syntax = syntax
        if self._syntax_highlighting_enabled:
            self._highlight_text()
        else:
            # Just update the plain text without highlighting
            # But preserve the font settings
            plain_text = self.toPlainText()
            super().setPlainText(plain_text)

    def set_theme(self, theme):
        """Set the theme for highlighting."""
        self._theme = theme
        self._highlight_text()

    def _update_theme(self):
        """Update the Pygments theme based on current dark/light mode."""
        if self._is_dark_mode:
            self._theme = "monokai"
        else:
            self._theme = "default"

    def set_dark_mode(self, is_dark):
        """Set dark/light mode and update theme."""
        if self._is_dark_mode != is_dark:
            self._is_dark_mode = is_dark
            self._update_theme()
            if self._syntax_highlighting_enabled:
                self._highlight_text()

    def _get_lexer_for_syntax(self, syntax):
        """Get the appropriate lexer for the given syntax."""
        try:
            return get_lexer_by_name(syntax.lower())
        except ClassNotFound:
            # Try to guess lexer from filename
            try:
                # Create a temporary filename with the syntax as extension
                temp_filename = f"file.{syntax}"
                from pygments.lexers import guess_lexer_for_filename
                return guess_lexer_for_filename(temp_filename, "")
            except ClassNotFound:
                # Fallback to text lexer
                return get_lexer_by_name("text")

    def _highlight_text(self):
        """Apply syntax highlighting to the text content."""
        # Prevent recursion
        if self._applying_highlighting:
            return

        # Remove dynamic theme selection and revert to original behavior

        # Get current text
        plain_text = self.toPlainText()

        # Block signals to avoid recursion when updating text
        self.blockSignals(True)

        # If syntax highlighting is disabled, just set plain text but preserve font
        if not self._syntax_highlighting_enabled:
            cursor_pos = self.textCursor().position()
            super().setPlainText(plain_text)
            cursor = self.textCursor()
            cursor.setPosition(min(cursor_pos, len(plain_text)))
            self.setTextCursor(cursor)
            self.blockSignals(False)
            return

        if not plain_text:
            self.blockSignals(False)
            return

        # Get lexer for current syntax with better error handling
        try:
            lexer = self._get_lexer_for_syntax(self._syntax)
        except Exception:
            super().setPlainText(plain_text)
            self.blockSignals(False)
            return

        # Create HTML formatter with Qt-compatible settings
        try:
            formatter = HtmlFormatter(
                style=self._theme,
                noclasses=True,
                nobackground=True,
                prestyles=f"white-space:pre-wrap; font-family:'{self.font().family()}'; font-size:{self.font().pointSize()}pt; font-weight:{self.font().weight()};",
                lineseparator="\n",
                linenos=False,
                wrapcode=True
            )
        except Exception:
            super().setPlainText(plain_text)
            self.blockSignals(False)
            return

        # Highlight text and set as HTML
        try:
            highlighted = highlight(plain_text, lexer, formatter)
            cursor_pos = self.textCursor().position()
            self._applying_highlighting = True
            self.setHtml(highlighted)
            self._applying_highlighting = False
            cursor = self.textCursor()
            cursor.setPosition(min(cursor_pos, len(plain_text)))
            self.setTextCursor(cursor)
        except Exception:
            self._applying_highlighting = False
            super().setPlainText(plain_text)
        self.blockSignals(False)

    def setPlainText(self, text):
        """Override to ensure highlighting is applied, but avoid recursion."""
        self.blockSignals(True)
        super().setPlainText(text)
        self.blockSignals(False)
        self._highlight_text()

    def setHtml(self, html):
        """Override to ensure highlighting is applied, but avoid recursion."""
        self.blockSignals(True)
        super().setHtml(html)
        self.blockSignals(False)
        if not self._applying_highlighting and self._syntax_highlighting_enabled:
            self._highlight_text()


def get_file_syntax(file_path):
    """Determine the syntax highlighting based on file extension."""
    if not file_path:
        return "text"

    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Map common extensions to syntax names
    extension_map = {
        '.py': 'python',
        '.pyw': 'python',
        '.js': 'javascript',
        '.jsx': 'jsx',
        '.ts': 'typescript',
        '.tsx': 'tsx',
        '.html': 'html',
        '.htm': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.rst': 'rst',
        '.txt': 'text',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.java': 'java',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.kts': 'kotlin',
        '.scala': 'scala',
        '.pl': 'perl',
        '.pm': 'perl',
        '.r': 'r',
        '.lua': 'lua',
        '.dart': 'dart',
        '.groovy': 'groovy',
        '.gradle': 'groovy',
        '.coffee': 'coffeescript',
        '.elm': 'elm',
        '.erl': 'erlang',
        '.hrl': 'erlang',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.fs': 'fsharp',
        '.fsi': 'fsharp',
        '.fsx': 'fsharp',
        '.hs': 'haskell',
        '.lhs': 'haskell',
        '.clj': 'clojure',
        '.cljs': 'clojure',
        '.cljc': 'clojure',
        '.sql': 'sql',
        '.dockerfile': 'docker',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.gitignore': 'gitignore',
        '.gitattributes': 'gitignore',
        '.diff': 'diff',
        '.patch': 'diff',
    }

    # Return mapped syntax or default to text
    return extension_map.get(ext, 'text')


def get_available_themes():
    """Get a list of available Pygments themes."""
    from pygments.styles import get_all_styles
    return list(get_all_styles())


def get_available_lexers():
    """Get a list of available lexers."""
    return [lexer[0] for lexer in get_all_lexers()]


def set_syntax_highlighting_enabled(text_edit, enabled):
    """Enable or disable syntax highlighting for a SyntaxHighlightedTextEdit instance."""
    text_edit._syntax_highlighting_enabled = enabled
    if enabled:
        # When enabling, re-apply highlighting to current text
        text_edit._highlight_text()
    else:
        # When disabling, just set plain text without triggering highlighting process
        # But preserve the font settings
        plain_text = text_edit.toPlainText()
        # Temporarily block signals to avoid recursion
        text_edit.blockSignals(True)
        text_edit.setPlainText(plain_text)
        text_edit.blockSignals(False)
