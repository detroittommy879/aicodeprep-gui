"""
Custom markdown renderer for AI Chat.
Lean implementation using Pygments for code blocks, custom QTextEdit for text.
"""
from PySide6 import QtWidgets, QtGui, QtCore
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
import re
from aicodeprep_gui.apptheme import system_pref_is_dark


class MarkdownRenderer:
    """Simple markdown renderer for chat messages."""

    # Colors for dark/light mode
    DARK_COLORS = {
        'heading': '#6EC1E4',  # Light blue
        'text': '#E0E0E0',      # Light gray
        'code_bg': '#1E1E1E',   # Dark gray background
        'link': '#0098D4',      # Blue link
        'bold': '#FFFFFF',      # White
        'italic': '#B0B0B0',    # Gray
        'quote': '#4CAF50',     # Green
        'hr': '#444444',        # Dark gray
    }

    LIGHT_COLORS = {
        'heading': '#0066CC',   # Darker blue
        'text': '#1A1A1A',      # Near black
        'code_bg': '#F5F5F5',    # Light gray background
        'link': '#0066CC',       # Blue link
        'bold': '#000000',       # Black
        'italic': '#666666',     # Gray
        'quote': '#2E7D32',     # Green
        'hr': '#CCCCCC',         # Medium gray
    }

    def __init__(self, is_dark_mode: bool = False):
        self._is_dark_mode = is_dark_mode
        self._colors = self.DARK_COLORS if is_dark_mode else self.LIGHT_COLORS

    def set_dark_mode(self, is_dark: bool):
        """Update colors for dark/light mode."""
        self._is_dark_mode = is_dark
        self._colors = self.DARK_COLORS if is_dark else self.LIGHT_COLORS

    def render(self, markdown_text: str) -> str:
        """
        Render markdown text to HTML.
        Supports: headings, bold, italic, code (inline and blocks), links, lists, hr, quotes.
        """
        if not markdown_text:
            return ''

        # Escape HTML but preserve markdown syntax
        html = self._escape_html(markdown_text)

        # Parse and convert markdown elements
        html = self._parse_code_blocks(html)
        html = self._parse_inline_code(html)
        html = self._parse_headings(html)
        html = self._parse_bold(html)
        html = self._parse_italic(html)
        html = self._parse_links(html)
        html = self._parse_blockquotes(html)
        html = self._parse_horizontal_rules(html)
        html = self._parse_lists(html)

        return html

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _parse_headings(self, html: str) -> str:
        """Convert headings (#, ##, ###) to styled spans."""
        colors = self._colors
        heading_style = f"color:{colors['heading']}; font-weight:bold;"

        # Match ATX-style headings (##, ###, ####)
        def replace_heading(match):
            level = len(match.group(1))
            text = match.group(2)
            # Clamp heading levels 1-4 to visual size
            font_size = max(11, 16 - level * 1.5)
            return f'<span style="{heading_style}; font-size:{font_size}px;">{text}</span>'

        # Handle ##, ###, #### headings
        html = re.sub(r'^(#{1,4})\s+(.+?)$', replace_heading, html, flags=re.MULTILINE)

        # Handle underline-style headings (=== and ---)
        lines = html.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check if next line is underline
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('==='):
                    # H1
                    result.append(f'<span style="{heading_style}; font-size:18px;">{line}</span>')
                    i += 2
                    continue
                elif next_line.startswith('---'):
                    # H2
                    result.append(f'<span style="{heading_style}; font-size:16px;">{line}</span>')
                    i += 2
                    continue
            result.append(line)
            i += 1

        return '\n'.join(result)

    def _parse_bold(self, html: str) -> str:
        """Convert **bold** to styled spans."""
        colors = self._colors
        # **bold**
        pattern = r'\*\*(.+?)\*\*'
        return re.sub(pattern, f'<span style="color:{colors["bold"]}; font-weight:bold;">\\1</span>', html)

    def _parse_italic(self, html: str) -> str:
        """Convert *italic* to styled spans."""
        colors = self._colors
        # *italic* (but not already bold)
        pattern = r'(?<!\*)\*(?!\*)(.+?)\*(?!\*)'
        return re.sub(pattern, f'<span style="color:{colors["italic"]}; font-style:italic;">\\1</span>', html)

    def _parse_inline_code(self, html: str) -> str:
        """Convert `code` to styled spans."""
        colors = self._colors
        # `code`
        pattern = r'`(.+?)`'
        return re.sub(pattern, f'<code style="background:{colors["code_bg"]}; color:#FF6B6B; padding:1px 4px; border-radius:3px; font-family:monospace;">\\1</code>', html)

    def _parse_code_blocks(self, html: str) -> str:
        """Convert ```code blocks``` to syntax-highlighted HTML."""
        colors = self._colors

        # Pattern for code blocks with optional language
        pattern = r'```(\w*)\n([\s\S]*?)```'

        def replace_code_block(match):
            language = match.group(1).lower() if match.group(1) else 'text'
            code = match.group(2).rstrip('\n')

            # Escape for HTML
            code = self._escape_html(code)

            # Try to get lexer
            try:
                lexer = get_lexer_by_name(language)
            except ClassNotFound:
                try:
                    lexer = get_lexer_by_name('text')
                except ClassNotFound:
                    lexer = get_lexer_by_name('text')

            # Format with Pygments
            formatter = HtmlFormatter(
                style='monokai' if self._is_dark_mode else 'default',
                noclasses=True,
                nobackground=True,
                prestyles=f"background:{colors['code_bg']}; padding:10px; border-radius:5px; overflow-x:auto;",
            )
            highlighted = highlight(code, lexer, formatter)
            return highlighted

        return re.sub(pattern, replace_code_block, html)

    def _parse_links(self, html: str) -> str:
        """Convert [text](url) to anchor tags."""
        colors = self._colors
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        return re.sub(pattern, f'<a href="\\2" style="color:{colors["link"]}; text-decoration:underline;">\\1</a>', html)

    def _parse_blockquotes(self, html: str) -> str:
        """Convert > quotes to styled blocks."""
        colors = self._colors
        lines = html.split('\n')
        result = []
        in_quote = False
        quote_lines = []

        for line in lines:
            if line.strip().startswith('>'):
                if not in_quote:
                    in_quote = True
                    quote_lines = []
                quote_lines.append(line.lstrip('>').lstrip())
            else:
                if in_quote:
                    quote_content = ' '.join(quote_lines)
                    result.append(
                        f'<div style="border-left:3px solid {colors["quote"]}; padding-left:10px; margin:10px 0; color:{colors["italic"]};">'
                        f'{quote_content}</div>'
                    )
                    quote_lines = []
                    in_quote = False
                result.append(line)

        # Handle trailing quote
        if in_quote and quote_lines:
            quote_content = ' '.join(quote_lines)
            result.append(
                f'<div style="border-left:3px solid {colors["quote"]}; padding-left:10px; margin:10px 0; color:{colors["italic"]};">'
                f'{quote_content}</div>'
            )

        return '\n'.join(result)

    def _parse_horizontal_rules(self, html: str) -> str:
        """Convert ---, ***, ___ to hr elements."""
        colors = self._colors
        hr_style = f"border:none; border-top:1px solid {colors['hr']}; margin:15px 0;"

        patterns = [
            r'^---+$',
            r'^\*\*\*+$',
            r'^_+$',
        ]

        lines = html.split('\n')
        result = []
        for line in lines:
            is_hr = any(re.match(p, line.strip()) for p in patterns)
            if is_hr:
                result.append(f'<hr style="{hr_style}"/>')
            else:
                result.append(line)

        return '\n'.join(result)

    def _parse_lists(self, html: str) -> str:
        """Convert - item and 1. item to styled list items."""
        lines = html.split('\n')
        result = []
        in_ul = False
        in_ol = False
        ol_start = 1

        for line in lines:
            stripped = line.strip()

            # Unordered list
            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_ul:
                    in_ul = True
                    in_ol = False
                    result.append('<ul style="margin:10px 0; padding-left:25px;">')
                item_text = stripped[2:]
                result.append(f'<li style="margin:3px 0;">{item_text}</li>')
            # Ordered list
            elif re.match(r'^\d+\.\s', stripped):
                if not in_ol:
                    in_ol = True
                    in_ul = False
                    result.append(f'<ol style="margin:10px 0; padding-left:25px;">')
                match = re.match(r'^(\d+)\.\s(.+)$', stripped)
                if match:
                    result.append(f'<li style="margin:3px 0;">{match.group(2)}</li>')
            else:
                if in_ul:
                    result.append('</ul>')
                    in_ul = False
                if in_ol:
                    result.append('</ol>')
                    in_ol = False
                result.append(line)

        # Close any open lists
        if in_ul:
            result.append('</ul>')
        if in_ol:
            result.append('</ol>')

        return '\n'.join(result)


class ChatMessageDisplay(QtWidgets.QTextEdit):
    """
    Read-only QTextEdit for displaying rendered markdown chat messages.
    Supports dark/light mode and custom styling.
    """

    def __init__(self, parent=None, is_dark_mode: bool = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Font settings
        font = QtGui.QFont("Segoe UI", 10)
        font.setStyleHint(QtGui.QFont.SansSerif)
        self.setFont(font)

        # Use system preference if not specified
        if is_dark_mode is None:
            is_dark_mode = system_pref_is_dark()

        # Renderer
        self._renderer = MarkdownRenderer(is_dark_mode)

        # Initial styling
        self.set_dark_mode(is_dark_mode)

    def set_dark_mode(self, is_dark: bool):
        """Update theme for dark/light mode."""
        colors = MarkdownRenderer.DARK_COLORS if is_dark else MarkdownRenderer.LIGHT_COLORS
        bg_color = '#1E1E1E' if is_dark else '#FFFFFF'
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_color};
                color: {colors['text']};
                border: 1px solid {colors['hr']};
                border-radius: 5px;
                padding: 8px;
            }}
        """)
        self._renderer.set_dark_mode(is_dark)

    def append_message(self, role: str, content: str):
        """
        Append a chat message with role styling.
        role: 'user' or 'assistant'
        """
        # Style based on role
        colors = self._renderer._colors
        if role == 'user':
            header = f'<div style="color:{colors["heading"]}; font-weight:bold; margin-bottom:8px;">User</div>'
            bg_style = f'background:{colors["code_bg"]};'
        else:
            header = f'<div style="color:#4CAF50; font-weight:bold; margin-bottom:8px;">AI</div>'
            bg_style = ''

        # Render markdown content with proper spacing
        content_html = self._renderer.render(content)

        # Add line breaks between HTML elements for better rendering
        content_html = content_html.replace('</div>', '</div><br>')
        content_html = content_html.replace('<br><br>', '<br>')
        content_html = content_html.rstrip('<br>')

        # Combine
        message_html = f'''
        <div style="{bg_style} padding:10px; margin:8px 0; border-radius:5px; line-height:1.6;">
            {header}
            <div style="color:{colors["text"]};">
                {content_html}
            </div>
        </div>
        '''

        # Store cursor position
        cursor = self.textCursor()
        at_bottom = cursor.atEnd()

        # Append HTML
        self.append(message_html)

        # Scroll to bottom if was at bottom
        if at_bottom:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear(self):
        """Clear all messages."""
        self.setHtml('')
