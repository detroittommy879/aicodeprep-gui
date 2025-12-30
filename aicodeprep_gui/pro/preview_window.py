"""Docked file preview window for pro features."""
import os
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui.smart_logic import is_binary_file
from .syntax_highlighter import SyntaxHighlightedTextEdit, get_file_syntax


class FilePreviewDock(QtWidgets.QDockWidget):
    """A dockable window for previewing file contents."""

    def __init__(self, parent=None, font_name="JetBrains Mono"):
        super().__init__("File Preview", parent)
        self.setObjectName("file_preview_dock")
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

        # Create the content widget
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)

        # Text preview area with specified font
        self.text_edit = SyntaxHighlightedTextEdit(font_name=font_name)

        # Font setup is handled by SyntaxHighlightedTextEdit

        # Status label
        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")

        layout.addWidget(self.text_edit)
        layout.addWidget(self.status_label)

        self.setWidget(content)
        self.setMinimumWidth(200)
        # Remove maximum width restriction to allow unlimited expansion
        # self.setMaximumWidth(600)

        # Hide initially
        self.hide()

    # Removed refresh_syntax_highlighting method

        # Syntax highlighting state (enabled by default for pro users)
        self.syntax_highlighting_enabled = True

    def set_dark_mode(self, is_dark):
        """Update the preview window for dark/light mode."""
        if hasattr(self, "text_edit") and self.text_edit:
            try:
                # Store current font settings
                current_font = self.text_edit.font()
                font_family = current_font.family()
                font_size = current_font.pointSize()
                font_weight = current_font.weight()

                # Update theme
                self.text_edit.set_dark_mode(is_dark)

                # Restore font settings
                restored_font = QtGui.QFont(font_family, font_size)
                restored_font.setWeight(QtGui.QFont.Weight(font_weight))
                self.text_edit.setFont(restored_font)

                # Re-apply highlighting
                self.text_edit._highlight_text()
            except Exception as e:
                self.text_edit.setPlainText(f"Theme update error: {str(e)}")

    def set_syntax_highlighting_enabled(self, enabled):
        """Enable or disable syntax highlighting."""
        self.syntax_highlighting_enabled = enabled
        # Also update the text edit widget directly
        from .syntax_highlighter import set_syntax_highlighting_enabled
        set_syntax_highlighting_enabled(self.text_edit, enabled)

    def preview_file(self, file_path):
        """Load and display file contents."""
        if not file_path or not os.path.isfile(file_path):
            self.clear_preview()
            return

        try:
            # Check if binary
            if is_binary_file(file_path):
                self.show_binary_warning(file_path)
                return

            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Truncate very large files
            max_chars = 100000
            if len(content) > max_chars:
                content = content[:max_chars] + "\n\n... [Content truncated]"

            if self.syntax_highlighting_enabled:
                # Determine syntax based on file extension
                syntax = get_file_syntax(file_path)
                self.text_edit.set_syntax(syntax)
                self.text_edit.setPlainText(content)
                self.status_label.setText(
                    f"Preview: {os.path.basename(file_path)} ({syntax})")
            else:
                # Instead of disabling syntax highlighting, treat as plain text
                # This avoids the recursion issues with toggling syntax highlighting
                self.text_edit.set_syntax("text")
                self.text_edit.setPlainText(content)
                self.status_label.setText(
                    f"Preview: {os.path.basename(file_path)} (plain text)")

        except Exception as e:
            self.text_edit.setPlainText(f"Error loading file: {str(e)}")
            self.status_label.setText("Error")

    def show_binary_warning(self, file_path):
        """Show warning for binary files."""
        self.text_edit.setPlainText(
            f"[Binary file - contents not shown]\n\n"
            f"File: {os.path.basename(file_path)}\n"
            f"Size: {os.path.getsize(file_path):,} bytes"
        )
        self.status_label.setText("Binary file")

    def clear_preview(self):
        """Clear the preview."""
        self.text_edit.clear()
        self.status_label.setText("Select a file to preview")
