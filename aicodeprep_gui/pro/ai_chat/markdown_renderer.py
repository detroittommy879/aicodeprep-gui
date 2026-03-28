"""
Custom markdown renderer for AI Chat.
Lean implementation using Pygments for code blocks, custom QTextEdit for text.
"""
from PySide6 import QtWidgets, QtGui, QtCore
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
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

        # Step 1: Extract fenced code blocks and inline code BEFORE HTML-escaping.
        # This prevents double-escaping of <, >, & characters in code content,
        # and ensures Pygments receives raw source code (not HTML entities).
        placeholders: dict[str, tuple] = {}
        counter = [0]

        def save_fenced_block(match):
            key = f'\x01F{counter[0]}\x01'
            counter[0] += 1
            lang = (match.group(1) or 'text').lower().strip()
            placeholders[key] = ('block', lang, match.group(2))
            return key

        def save_inline_code(match):
            key = f'\x01I{counter[0]}\x01'
            counter[0] += 1
            placeholders[key] = ('inline', '', match.group(1))
            return key

        text = re.sub(r'```(\w*)\n([\s\S]*?)```',
                      save_fenced_block, markdown_text)
        text = re.sub(r'`([^`\n]+)`', save_inline_code, text)

        # Step 2: HTML-escape the non-code text
        html = self._escape_html(text)

        # Step 3: Apply markdown transforms on the escaped text
        html = self._parse_headings(html)
        html = self._parse_bold(html)
        html = self._parse_italic(html)
        html = self._parse_links(html)
        html = self._parse_blockquotes(html)
        html = self._parse_horizontal_rules(html)
        html = self._parse_lists(html)

        # Step 4: Convert newlines to <br> so Qt renders line breaks.
        # Then clean up spurious <br> tags that were injected inside list HTML.
        html = html.replace('\n', '<br>')
        html = re.sub(r'<br>(<(?:ul|ol|li)[^>]*>)', r'\1', html)
        html = re.sub(r'(</(?:ul|ol|li)>)<br>', r'\1', html)

        # Step 5: Restore placeholders with properly rendered code
        colors = self._colors
        for key, data in placeholders.items():
            kind = data[0]
            if kind == 'inline':
                escaped = self._escape_html(data[2])
                replacement = (
                    f'<code style="background:{colors["code_bg"]}; color:#FF6B6B;'
                    f' padding:1px 4px; border-radius:3px; font-family:monospace;">'
                    f'{escaped}</code>'
                )
            else:
                replacement = self._render_code_block(data[1], data[2])
            html = html.replace(key, replacement, 1)

        return html

    def _render_code_block(self, language: str, code: str) -> str:
        """Render a fenced code block with Pygments syntax highlighting."""
        colors = self._colors
        try:
            lexer = get_lexer_by_name(language or 'text')
        except ClassNotFound:
            lexer = TextLexer()
        formatter = HtmlFormatter(
            style='monokai' if self._is_dark_mode else 'default',
            noclasses=True,
            nobackground=True,
            prestyles=(
                f"background:{colors['code_bg']}; padding:10px; border-radius:5px;"
                f" white-space:pre-wrap; word-wrap:break-word;"
                f" font-family:monospace; font-size:12px; display:block;"
            ),
        )
        return highlight(code, lexer, formatter)

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
        html = re.sub(r'^(#{1,4})\s+(.+?)$',
                      replace_heading, html, flags=re.MULTILINE)

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
                    result.append(
                        f'<span style="{heading_style}; font-size:18px;">{line}</span>')
                    i += 2
                    continue
                elif next_line.startswith('---'):
                    # H2
                    result.append(
                        f'<span style="{heading_style}; font-size:16px;">{line}</span>')
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
                    result.append(
                        '<ul style="margin:10px 0; padding-left:25px;">')
                item_text = stripped[2:]
                result.append(f'<li style="margin:3px 0;">{item_text}</li>')
            # Ordered list
            elif re.match(r'^\d+\.\s', stripped):
                if not in_ol:
                    in_ol = True
                    in_ul = False
                    result.append(
                        f'<ol style="margin:10px 0; padding-left:25px;">')
                match = re.match(r'^(\d+)\.\s(.+)$', stripped)
                if match:
                    result.append(
                        f'<li style="margin:3px 0;">{match.group(2)}</li>')
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

        # Streaming state
        self._streaming_message_div = None
        self._streaming_content = ""

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

    def set_messages(self, messages: list):
        """
        Re-render the full conversation from a list of {'role', 'content'} dicts.
        Uses setHtml() for correct layout — QTextEdit.append() wraps content in
        <p> tags which breaks <div> block elements, making everything shift inline.
        """
        colors = self._renderer._colors
        is_dark = self._renderer._is_dark_mode
        body_bg = '#1E1E1E' if is_dark else '#FFFFFF'

        rows = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            content_html = self._renderer.render(content)

            if role == 'user':
                header_label = 'You'
                header_color = colors['heading']
                cell_bg = colors['code_bg']
            else:
                header_label = 'AI'
                header_color = '#4CAF50'
                cell_bg = body_bg

            rows.append(
                f'<table width="100%" cellpadding="10" cellspacing="0" border="0">'
                f'<tr><td bgcolor="{cell_bg}">'
                f'<b style="color:{header_color};">{header_label}</b><br><br>'
                f'<span style="color:{colors["text"]};">{content_html}</span>'
                f'</td></tr></table><br>'
            )

        full_html = (
            f'<html><body style="background-color:{body_bg}; margin:4px;">'
            + ''.join(rows)
            + '</body></html>'
        )

        sb = self.verticalScrollBar()
        was_at_bottom = sb.value() >= sb.maximum() - 10
        self.setHtml(full_html)
        if was_at_bottom:
            QtCore.QTimer.singleShot(0, lambda: self.verticalScrollBar().setValue(
                self.verticalScrollBar().maximum()))

    def append_message(self, role: str, content: str):
        """
        Append a single message. Delegates to set_messages() via a one-item list
        so the layout is always correct (uses setHtml, not append).
        NOTE: callers that already have the full history should call set_messages()
        directly instead of looping over append_message().
        """
        # Build a minimal messages list and reuse set_messages for correct layout
        # We don't track internal state here; callers own the history list.
        colors = self._renderer._colors
        is_dark = self._renderer._is_dark_mode
        body_bg = '#1E1E1E' if is_dark else '#FFFFFF'

        content_html = self._renderer.render(content)
        if role == 'user':
            header_label = 'You'
            header_color = colors['heading']
            cell_bg = colors['code_bg']
        else:
            header_label = 'AI'
            header_color = '#4CAF50'
            cell_bg = body_bg

        new_row = (
            f'<table width="100%" cellpadding="10" cellspacing="0" border="0">'
            f'<tr><td bgcolor="{cell_bg}">'
            f'<b style="color:{header_color};">{header_label}</b><br><br>'
            f'<span style="color:{colors["text"]};">{content_html}</span>'
            f'</td></tr></table><br>'
        )

        # Insert at end of existing document without append()'s <p> wrapping
        sb = self.verticalScrollBar()
        was_at_bottom = sb.value() >= sb.maximum() - 10
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
        self.insertHtml(new_row)
        if was_at_bottom:
            QtCore.QTimer.singleShot(0, lambda: self.verticalScrollBar().setValue(
                self.verticalScrollBar().maximum()))

    def start_streaming(self, role: str):
        """
        Start a streaming response message.
        Creates a placeholder that will be populated with streaming content.
        """
        colors = self._renderer._colors
        if role == 'user':
            header = f'<div style="color:{colors["heading"]}; font-weight:bold; margin-bottom:8px;">User</div>'
            bg_style = f'background:{colors["code_bg"]};'
        else:
            header = f'<div style="color:#4CAF50; font-weight:bold; margin-bottom:8px;">AI</div>'
            bg_style = ''

        # Create placeholder message
        self._streaming_message_html = f'''
        <div style="{bg_style} padding:10px; margin:8px 0; border-radius:5px; line-height:1.6;">
            {header}
            <div id="streaming-content" style="color:{colors["text"]};">
            </div>
        </div>
        '''
        self._streaming_content = ""

        # Store scroll position
        self._was_at_bottom = self.verticalScrollBar(
        ).value() >= self.verticalScrollBar().maximum() - 10

        # Append the placeholder
        self.append(self._streaming_message_html)

    def append_stream_chunk(self, chunk: str):
        """
        Append a chunk of content to the streaming message.
        Uses word wrap to prevent horizontal scrolling.
        """
        self._streaming_content += chunk

        # Escape HTML for proper display
        escaped_chunk = chunk.replace('&', '&amp;').replace(
            '<', '&lt;').replace('>', '&gt;')

        # Insert with automatic wrapping - use a space to trigger word wrap
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        # Insert text with zero-width space after spaces to encourage wrapping
        # This prevents very long words from causing horizontal scroll
        if escaped_chunk:
            # Add a space after content to help with wrapping
            text_to_insert = escaped_chunk
            cursor.insertText(text_to_insert)

        self.setTextCursor(cursor)

        # Auto-scroll
        if self._was_at_bottom:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def finish_streaming(self):
        """
        Called when streaming is complete. Clears accumulated streaming state.
        The caller (ChatTabWidget) is responsible for re-rendering the full
        conversation with proper markdown now that the complete text is available.
        """
        self._streaming_message_html = None
        self._streaming_content = ""

    def clear(self):
        """Clear all messages."""
        self.setHtml('')
        self._streaming_message_html = None
        self._streaming_content = ""
