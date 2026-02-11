"""
AI Chat Dock Widget - Main dockable panel for AI chat functionality.
Supports both tabbed view and side-by-side view for multiple chats.
"""
from PySide6 import QtWidgets, QtGui, QtCore
from .chat_tab import ChatTabWidget
from ..ai_assist.ai_client import AIClient
from aicodeprep_gui.apptheme import system_pref_is_dark
import logging


class AIChatDock(QtWidgets.QDockWidget):
    """
    Dockable AI Chat panel with multiple tabs.
    Supports multi-select to send context to multiple tabs simultaneously.
    Can display tabs side-by-side in addition to stacked view.
    """

    def __init__(self, parent=None):
        super().__init__("AI Chat", parent)
        self.setObjectName("ai_chat_dock")
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)
        self.setFloating(False)

        # Track dark mode state
        self._is_dark_mode = system_pref_is_dark()
        self._side_by_side = False  # Toggle for side-by-side view
        self._chat_tabs = []  # List of ChatTabWidget instances

        # Main widget container
        self._content_widget = QtWidgets.QWidget()
        self._layout = QtWidgets.QVBoxLayout(self._content_widget)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Container for the tab bar (hidden in side-by-side mode)
        self._tab_bar_container = QtWidgets.QWidget()
        self._tab_bar_layout = QtWidgets.QVBoxLayout(self._tab_bar_container)
        self._tab_bar_layout.setContentsMargins(0, 0, 0, 0)
        self._tab_bar_layout.setSpacing(0)

        # Tab bar for switching between chat tabs
        self._tab_bar = QtWidgets.QTabBar()
        self._tab_bar.setDocumentMode(True)
        self._tab_bar.setTabsClosable(True)
        self._tab_bar.tabCloseRequested.connect(self._close_tab)
        self._tab_bar.currentChanged.connect(self._switch_tab)
        self._tab_bar_layout.addWidget(self._tab_bar)
        self._layout.addWidget(self._tab_bar_container)

        # Stacked widget to hold different chat tab widgets (for tabbed view)
        self._stack = QtWidgets.QStackedWidget()
        self._layout.addWidget(self._stack, stretch=1)

        # Horizontal splitter for side-by-side view
        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter.setChildrenCollapsible(True)
        self._splitter.setHandleWidth(8)
        self._splitter.hide()  # Hidden by default
        self._layout.addWidget(self._splitter, stretch=1)

        # Bottom toolbar for adding tabs and actions
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)

        # New tab button
        self._new_tab_button = QtWidgets.QPushButton("+ New Tab")
        self._new_tab_button.setToolTip("Add a new chat tab")
        self._new_tab_button.clicked.connect(self._add_new_tab)
        toolbar.addWidget(self._new_tab_button)

        # Side-by-side toggle button
        self._side_by_side_button = QtWidgets.QPushButton("Side-by-Side")
        self._side_by_side_button.setToolTip("Show all chats side by side")
        self._side_by_side_button.setCheckable(True)
        self._side_by_side_button.clicked.connect(self._toggle_side_by_side)
        toolbar.addWidget(self._side_by_side_button)

        toolbar.addStretch()

        # Clear all chats button
        self._clear_button = QtWidgets.QPushButton("Clear All")
        self._clear_button.setToolTip("Clear all chat histories")
        self._clear_button.clicked.connect(self._clear_all_chats)
        toolbar.addWidget(self._clear_button)

        # Refresh models button
        self._refresh_button = QtWidgets.QPushButton("Refresh Models")
        self._refresh_button.setToolTip("Reload models from endpoint")
        self._refresh_button.clicked.connect(self._refresh_models)
        toolbar.addWidget(self._refresh_button)

        # Settings button
        self._settings_button = QtWidgets.QPushButton("Settings")
        self._settings_button.setToolTip("Open AI endpoint settings")
        self._settings_button.clicked.connect(self._open_settings)
        toolbar.addWidget(self._settings_button)

        toolbar_widget = QtWidgets.QWidget()
        toolbar_widget.setLayout(toolbar)
        self._layout.addWidget(toolbar_widget)

        # Set the content widget
        self.setWidget(self._content_widget)

        # Set minimum size
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)

        # Hide initially
        self.hide()

        # Apply initial dark mode
        self.set_dark_mode(self._is_dark_mode)

        # Create first tab
        self._add_new_tab()

    def _add_new_tab(self, name: str = None) -> ChatTabWidget:
        """Add a new chat tab."""
        if name is None or not isinstance(name, str):
            count = len(self._chat_tabs) + 1
            tab_name = f"Chat {count}"
        else:
            tab_name = name

        # Create chat tab widget
        chat_tab = ChatTabWidget()
        self._chat_tabs.append(chat_tab)

        # Add to stacked widget (for tabbed view)
        self._stack.addWidget(chat_tab)

        # Add to splitter (for side-by-side view)
        self._splitter.addWidget(chat_tab)

        # Add to tab bar
        tab_id = self._tab_bar.addTab(tab_name)
        self._tab_bar.setCurrentIndex(tab_id)

        # In side-by-side mode, ensure all widgets are visible
        if self._side_by_side:
            chat_tab.show()

        return chat_tab

    def _close_tab(self, index: int):
        """Close a tab."""
        # Don't close the last tab
        if len(self._chat_tabs) <= 1:
            return

        # Get the widget
        if index < 0 or index >= len(self._chat_tabs):
            return

        widget = self._chat_tabs[index]

        # Remove from stack
        self._stack.removeWidget(widget)

        # Remove from splitter
        self._splitter.removeWidget(widget)

        # Remove from list and delete
        self._chat_tabs.pop(index)
        widget.deleteLater()

        # Remove from tab bar
        self._tab_bar.removeTab(index)

        # Update stack index
        current = min(index, self._tab_bar.count() - 1)
        if current >= 0:
            self._tab_bar.setCurrentIndex(current)
            self._stack.setCurrentIndex(current)

    def _switch_tab(self, index: int):
        """Switch to a different chat tab."""
        # Only switch stack if NOT in side-by-side mode
        if not self._side_by_side and index >= 0:
            self._stack.setCurrentIndex(index)

    def _toggle_side_by_side(self, enabled: bool = None):
        """Toggle between tabbed view and side-by-side view."""
        if enabled is None:
            enabled = not self._side_by_side

        self._side_by_side = enabled
        self._side_by_side_button.setChecked(enabled)

        if enabled:
            # Show side-by-side, hide tab bar and stacked widget
            self._tab_bar_container.hide()
            self._stack.hide()
            self._splitter.show()

            # Ensure all widgets in splitter are visible
            for i in range(len(self._chat_tabs)):
                self._chat_tabs[i].show()
        else:
            # Show tabbed view, hide splitter
            self._tab_bar_container.show()
            self._stack.show()
            self._splitter.hide()

            # Hide widgets in splitter (but they're still in stack)
            for i in range(len(self._chat_tabs)):
                self._chat_tabs[i].hide()

            # Show the current tab in stack
            current = self._tab_bar.currentIndex()
            if current >= 0 and current < len(self._chat_tabs):
                self._stack.setCurrentIndex(current)

    def _clear_all_chats(self):
        """Clear all chat histories."""
        # Ask for confirmation
        reply = QtWidgets.QMessageBox.question(
            self,
            "Clear All Chats",
            "Are you sure you want to clear all chat histories?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply != QtWidgets.QMessageBox.Yes:
            return

        # Clear each tab
        for widget in self._chat_tabs:
            if hasattr(widget, 'clear_chat'):
                widget.clear_chat()

    def _refresh_models(self):
        """Refresh model list in all tabs."""
        for widget in self._chat_tabs:
            if hasattr(widget, 'load_endpoint_config'):
                widget.load_endpoint_config()

    def _open_settings(self):
        """Open AI endpoint settings."""
        try:
            # Import and show endpoint settings dialog
            from aicodeprep_gui.gui.components.ai_settings_dialog import EndpointSettingsDialog
            dialog = EndpointSettingsDialog(self)
            dialog.exec()
        except ImportError:
            # Fallback: show a message
            QtWidgets.QMessageBox.information(
                self,
                "Settings",
                "Configure AI endpoints in Settings > AI Endpoints"
            )

    def set_dark_mode(self, is_dark: bool):
        """Update theme for all components."""
        self._is_dark_mode = is_dark

        # Update all chat tabs
        for widget in self._chat_tabs:
            if hasattr(widget, 'set_dark_mode'):
                widget.set_dark_mode(is_dark)

        # Update dock styling
        colors = {
            'bg': '#2D2D2D' if is_dark else '#F0F0F0',
            'text': '#E0E0E0' if is_dark else '#1A1A1A',
            'border': '#404040' if is_dark else '#CCCCCC',
            'handle': '#404040' if is_dark else '#CCCCCC',
        }

        self._tab_bar.setStyleSheet(f"""
            QTabBar {{
                background: {colors['bg']};
                color: {colors['text']};
                border-bottom: 1px solid {colors['border']};
            }}
            QTabBar::tab {{
                background: {colors['bg']};
                color: {colors['text']};
                padding: 5px 10px;
                min-width: 60px;
            }}
            QTabBar::tab:selected {{
                background: {colors['text']};
                color: {colors['bg']};
            }}
            QTabBar::close-button {{
                image: none;
                subcontrol-position: right;
                width: 16px;
            }}
        """)

        # Update splitter handle styling
        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {colors['handle']};
            }}
            QSplitter::handle:horizontal {{
                width: 8px;
            }}
        """)

    def send_context_to_selected_tabs(self, context_text: str):
        """
        Send context text to all selected tabs.
        Selected tabs have their checkbox checked.
        """
        count = 0
        for widget in self._chat_tabs:
            if hasattr(widget, 'is_selected') and widget.is_selected():
                if hasattr(widget, 'send_context'):
                    widget.send_context(context_text)
                    count += 1

        return count

    def get_selected_tab(self) -> ChatTabWidget:
        """Get the currently selected chat tab widget."""
        index = self._tab_bar.currentIndex()
        if index >= 0 and index < len(self._chat_tabs):
            return self._chat_tabs[index]
        return None

    def get_all_tabs(self) -> list:
        """Get all chat tab widgets."""
        return self._chat_tabs.copy()
