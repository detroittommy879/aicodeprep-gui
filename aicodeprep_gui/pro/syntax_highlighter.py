"""Syntax highlighted text edit widget for Pro features."""
from PySide6 import QtWidgets, QtGui
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.util import ClassNotFound
import os


class SyntaxHighlightedTextEdit(QtWidgets.QTextEdit):
    """A QTextEdit with syntax highlighting using Pygments."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

        # Set default font
        font = QtGui.QFont("Consolas", 10)
        font.setStyleHint(QtGui.QFont.Monospace)
        self.setFont(font)

        # Default syntax and theme
        self._syntax = "text"
        self._theme = "default"

        # Connect text change signal
        self.textChanged.connect(self._highlight_text)

    def set_syntax(self, syntax):
        """Set the syntax for highlighting."""
        self._syntax = syntax
        self._highlight_text()

    def set_theme(self, theme):
        """Set the theme for highlighting."""
        self._theme = theme
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
        # Get current text
        plain_text = self.toPlainText()

        if not plain_text:
            return

        # Get lexer for current syntax with better error handling
        try:
            lexer = self._get_lexer_for_syntax(self._syntax)
        except Exception:
            # Fallback to plain text if lexer fails
            super().setPlainText(plain_text)
            return

        # Create HTML formatter with Qt-compatible settings
        try:
            formatter = HtmlFormatter(
                style=self._theme,
                noclasses=True,  # Use inline styles instead of CSS classes
                nobackground=True,
                prestyles=f"white-space:pre-wrap; font-family:'{self.font().family()}'; font-size:{self.font().pointSize()}pt;",
                lineseparator="\n",  # Use newline instead of <br />
                linenos=False,  # Disable line numbers
                wrapcode=True  # Wrap code in a <code> tag
            )
        except Exception:
            # Fallback to plain text if formatter fails
            super().setPlainText(plain_text)
            return

        # Highlight text and set as HTML
        try:
            highlighted = highlight(plain_text, lexer, formatter)
            # Save cursor position
            cursor_pos = self.textCursor().position()

            # Block signals to prevent recursion
            self.blockSignals(True)
            self.setHtml(highlighted)
            self.blockSignals(False)

            # Restore cursor position
            cursor = self.textCursor()
            cursor.setPosition(min(cursor_pos, len(plain_text)))
            self.setTextCursor(cursor)
        except Exception:
            # Fallback to plain text if highlighting fails
            super().setPlainText(plain_text)

    def setPlainText(self, text):
        """Override to ensure highlighting is applied."""
        super().setPlainText(text)
        self._highlight_text()

    def setHtml(self, html):
        """Override to ensure highlighting is applied."""
        super().setHtml(html)
        # Only re-highlight if this wasn't called from _highlight_text
        if not self.signalsBlocked():
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
