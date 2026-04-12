"""
AI Chat Dock Widget - Main dockable panel for AI chat functionality.
Supports both tabbed view and side-by-side view for multiple chats.
"""
import base64
import json

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
        self.setAllowedAreas(QtCore.Qt.RightDockWidgetArea |
                             QtCore.Qt.LeftDockWidgetArea)
        self.setFloating(False)

        # Track dark mode state
        self._is_dark_mode = system_pref_is_dark()
        self._side_by_side = True  # Default to side-by-side view
        self._chat_tabs = []  # List of ChatTabWidget instances (docked only)
        # List of (window, chat_tab) for overflow windows
        self._floating_windows = []
        self._auto_tile = True  # Auto-tile based on number of tabs
        self._tile_mode = "auto"  # "auto" or "custom"
        self._max_docked_tabs = 3  # Max tabs in the dock; extras become floating windows

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

        # Root splitter for grid layout - allows both horizontal and vertical nesting
        self._root_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._root_splitter.setChildrenCollapsible(False)
        self._root_splitter.setHandleWidth(6)
        self._root_splitter.setOpaqueResize(True)  # User can resize
        self._root_splitter.setStretchFactor(0, 1)  # Allow stretching
        self._root_splitter.setSizes([200] * 10)  # Default equal sizes
        self._root_splitter.hide()  # Hidden by default
        self._layout.addWidget(self._root_splitter, stretch=1)

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
        self._side_by_side_button.setChecked(True)
        self._side_by_side_button.clicked.connect(self._toggle_side_by_side)
        toolbar.addWidget(self._side_by_side_button)

        # Tile layout button with menu
        self._tile_button = QtWidgets.QPushButton("Tile")
        self._tile_button.setToolTip("Choose tile layout (click for options)")
        self._tile_menu = QtWidgets.QMenu(self)
        self._tile_menu.addAction(
            "Auto Tile", lambda: self._apply_tile_layout("auto"))
        self._tile_menu.addAction(
            "2 Columns", lambda: self._apply_tile_layout("2col"))
        self._tile_menu.addAction(
            "3 Columns", lambda: self._apply_tile_layout("3col"))
        self._tile_menu.addAction(
            "4 Columns", lambda: self._apply_tile_layout("4col"))
        self._tile_menu.addSeparator()
        self._tile_menu.addAction(
            "2x2 Grid (4)", lambda: self._apply_tile_layout("2x2"))
        self._tile_menu.addAction(
            "3x2 Grid (6)", lambda: self._apply_tile_layout("3x2"))
        self._tile_menu.addAction(
            "3x3 Grid (9)", lambda: self._apply_tile_layout("3x3"))
        self._tile_menu.addSeparator()
        self._tile_menu.addAction("Reset Layout", self._reset_tile_layout)
        self._tile_button.setMenu(self._tile_menu)
        toolbar.addWidget(self._tile_button)

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

        # Enable side-by-side mode by default after tab is created
        self._toggle_side_by_side(True)

    def _serialize_splitter(self, splitter: QtWidgets.QSplitter) -> dict:
        data = {
            "orientation": int(splitter.orientation()),
            "state": base64.b64encode(bytes(splitter.saveState())).decode("utf-8"),
            "children": [],
        }
        for index in range(splitter.count()):
            child = splitter.widget(index)
            if isinstance(child, QtWidgets.QSplitter):
                data["children"].append(self._serialize_splitter(child))
            else:
                data["children"].append(None)
        return data

    def _restore_splitter(self, splitter: QtWidgets.QSplitter, data: dict):
        if not isinstance(data, dict):
            return

        try:
            splitter.setOrientation(QtCore.Qt.Orientation(
                data.get("orientation", int(splitter.orientation()))))
        except Exception:
            pass

        encoded_state = data.get("state")
        if encoded_state:
            try:
                splitter.restoreState(QtCore.QByteArray(
                    base64.b64decode(encoded_state.encode("utf-8"))
                ))
            except Exception:
                pass

        for index, child_state in enumerate(data.get("children", [])):
            if child_state is None or index >= splitter.count():
                continue
            child = splitter.widget(index)
            if isinstance(child, QtWidgets.QSplitter):
                self._restore_splitter(child, child_state)

    def get_layout_state(self) -> dict:
        """Return persistent layout state for project-level preferences."""
        return {
            "side_by_side": bool(self._side_by_side),
            "tile_mode": self._tile_mode,
            "root_splitter": self._serialize_splitter(self._root_splitter),
        }

    def restore_layout_state(self, state: dict):
        """Restore persistent layout state for project-level preferences."""
        if not isinstance(state, dict):
            return

        side_by_side = bool(state.get("side_by_side", True))
        tile_mode = str(state.get("tile_mode") or "auto")
        self._toggle_side_by_side(side_by_side)
        if side_by_side:
            self._apply_tile_layout(tile_mode)

            root_state = state.get("root_splitter")
            if isinstance(root_state, dict):
                QtCore.QTimer.singleShot(
                    0, lambda rs=root_state: self._restore_splitter(
                        self._root_splitter, rs)
                )

    def _all_chat_tabs(self):
        """Return all chat tabs (docked + floating) for operations like send-to-all."""
        all_tabs = list(self._chat_tabs)
        for _win, tab in self._floating_windows:
            all_tabs.append(tab)
        return all_tabs

    def _add_new_tab(self, name: str = None) -> ChatTabWidget:
        """Add a new chat tab. If docked slots are full, open a floating window."""
        total = len(self._chat_tabs) + len(self._floating_windows)
        if name is None or not isinstance(name, str):
            tab_name = f"Chat {total + 1}"
        else:
            tab_name = name

        # Create chat tab widget
        chat_tab = ChatTabWidget()

        # If we already have max docked tabs, open as a floating window
        if len(self._chat_tabs) >= self._max_docked_tabs:
            self._open_floating_chat(chat_tab, tab_name)
            return chat_tab

        # Otherwise add to the dock normally
        self._chat_tabs.append(chat_tab)

        # Add to stacked widget (for tabbed view)
        self._stack.addWidget(chat_tab)

        # Add to tab bar
        tab_id = self._tab_bar.addTab(tab_name)
        self._tab_bar.setCurrentIndex(tab_id)

        # In side-by-side mode, ensure all widgets are visible
        if self._side_by_side:
            chat_tab.show()
            if self._tile_mode == "auto":
                self._apply_auto_tile()

        return chat_tab

    def _open_floating_chat(self, chat_tab: ChatTabWidget, title: str):
        """Open a ChatTabWidget in its own floating window."""
        win = QtWidgets.QWidget()
        win.setWindowTitle(f"AI Chat - {title}")
        win.setWindowFlags(QtCore.Qt.Window)
        win.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        win.resize(500, 600)

        layout = QtWidgets.QVBoxLayout(win)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(chat_tab)

        # Apply current theme
        if hasattr(chat_tab, 'set_dark_mode'):
            chat_tab.set_dark_mode(self._is_dark_mode)

        # Track the window
        self._floating_windows.append((win, chat_tab))

        # Clean up when the window is closed
        win.destroyed.connect(lambda: self._on_floating_closed(win, chat_tab))

        win.show()
        win.raise_()
        win.activateWindow()

    def _on_floating_closed(self, win, chat_tab):
        """Remove a floating window from tracking when it is closed."""
        self._floating_windows = [
            (w, t) for w, t in self._floating_windows if w is not win
        ]

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

        # Safely detach from whatever splitter it's in
        try:
            widget.setParent(None)
        except RuntimeError:
            pass

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

        # Re-apply auto tile in side-by-side mode
        if self._side_by_side and self._tile_mode == "auto":
            self._apply_auto_tile()

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
            self._root_splitter.show()

            # Show all chat widgets
            for widget in self._chat_tabs:
                widget.show()

            # Apply auto-tiling based on number of tabs
            self._apply_auto_tile()
        else:
            # Show tabbed view, hide splitter
            self._tab_bar_container.show()
            self._stack.show()
            self._root_splitter.hide()

            # Hide widgets in splitter (but they're still in stack)
            for widget in self._chat_tabs:
                widget.hide()

            # Show the current tab in stack
            current = self._tab_bar.currentIndex()
            if current >= 0 and current < len(self._chat_tabs):
                self._stack.setCurrentIndex(current)

    def _apply_tile_layout(self, mode: str):
        """Apply specific tile layout mode."""
        self._tile_mode = mode
        num_tabs = len(self._chat_tabs)
        if num_tabs == 0:
            return

        # Show all chat widgets
        for widget in self._chat_tabs:
            widget.show()

        total_height = self._root_splitter.height()

        if mode == "auto":
            self._apply_auto_tile()
        elif mode == "2col":
            # 2 columns, equal width
            self._create_column_layout(2)
        elif mode == "3col":
            # 3 columns, equal width
            self._create_column_layout(3)
        elif mode == "4col":
            # 4 columns, equal width
            self._create_column_layout(4)
        elif mode == "2x2":
            # 2x2 grid (4 panels)
            self._create_grid_layout(2, 2)
        elif mode == "3x2":
            # 3x2 grid (6 panels)
            self._create_grid_layout(3, 2)
        elif mode == "3x3":
            # 3x3 grid (9 panels)
            self._create_grid_layout(3, 3)

    def _create_column_layout(self, num_cols: int, total_width: int = None, total_height: int = None):
        """Create equal-width columns layout."""
        num_tabs = len(self._chat_tabs)
        if num_tabs == 0:
            return

        if total_width is None:
            total_width = max(300, self._root_splitter.width())
        if total_height is None:
            total_height = max(300, self._root_splitter.height())

        # Calculate column width
        col_width = total_width // num_cols

        # If tabs fit in one row, just use horizontal splitter
        if num_tabs <= num_cols:
            # Safely detach tabs, then clear old row splitters
            self._detach_all_tabs()
            self._clear_splitter()
            self._root_splitter.setOrientation(QtCore.Qt.Horizontal)
            # Re-add tabs directly to root splitter
            for tab in self._chat_tabs:
                self._root_splitter.addWidget(tab)
                tab.show()
            sizes = [col_width] * num_tabs
            self._root_splitter.setSizes(sizes)
        else:
            # Multiple rows needed - create nested splitters
            self._build_nested_column_layout(
                num_cols, num_tabs, total_width, total_height)

    def _detach_all_tabs(self):
        """Safely remove all chat tab widgets from any parent splitter/container.

        Must be called BEFORE clearing row splitters, otherwise destroying
        a row splitter cascades and destroys its child chat tabs.
        """
        for tab in self._chat_tabs:
            try:
                if tab.parent() is not None:
                    tab.setParent(None)
            except RuntimeError:
                pass  # C++ object already deleted

    def _clear_splitter(self):
        """Remove and destroy any intermediate row splitters from root splitter.

        Call _detach_all_tabs() first so chat tabs are safe.
        """
        for i in range(self._root_splitter.count() - 1, -1, -1):
            w = self._root_splitter.widget(i)
            if w is not None:
                w.setParent(None)
                # Only delete intermediate splitters, not chat tabs
                if w not in self._chat_tabs:
                    w.deleteLater()

    def _build_nested_column_layout(self, num_cols: int, num_tabs: int, total_width: int, total_height: int):
        """Build nested splitters for multi-row column layout."""
        # Calculate rows needed
        rows = (num_tabs + num_cols - 1) // num_cols
        col_width = total_width // num_cols
        row_height = total_height // rows

        # Safely detach tabs, then clear old row splitters
        self._detach_all_tabs()
        self._clear_splitter()

        # Create row splitters
        row_splitters = []
        for r in range(rows):
            row_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            row_splitter.setChildrenCollapsible(False)
            row_splitter.setHandleWidth(4)
            row_splitter.setOpaqueResize(True)
            row_splitters.append(row_splitter)
            self._root_splitter.addWidget(row_splitter)

        # Distribute widgets across rows
        tab_idx = 0
        for r in range(rows):
            row_splitter = row_splitters[r]
            # Calculate how many widgets in this row
            remaining_tabs = num_tabs - tab_idx
            tabs_in_row = min(num_cols, remaining_tabs)

            for c in range(tabs_in_row):
                if tab_idx < num_tabs:
                    widget = self._chat_tabs[tab_idx]
                    row_splitter.addWidget(widget)
                    tab_idx += 1

            # Set equal sizes for this row
            row_sizes = [col_width] * tabs_in_row
            row_splitter.setSizes(row_sizes)

        # Set root splitter sizes for rows
        root_sizes = [row_height] * len(row_splitters)
        self._root_splitter.setSizes(root_sizes)

    def _create_grid_layout(self, cols: int, rows: int, total_width: int = None, total_height: int = None):
        """Create a proper grid layout with nested splitters."""
        num_tabs = len(self._chat_tabs)
        total_cells = cols * rows

        if num_tabs == 0:
            return

        if total_width is None:
            total_width = max(300, self._root_splitter.width())
        if total_height is None:
            total_height = max(300, self._root_splitter.height())

        # Safely detach tabs, then clear old row splitters
        self._detach_all_tabs()
        self._clear_splitter()

        # Calculate cell dimensions
        cell_width = total_width // cols
        cell_height = total_height // rows

        # Create row splitters
        row_splitters = []
        for r in range(rows):
            row_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            row_splitter.setChildrenCollapsible(False)
            row_splitter.setHandleWidth(4)
            row_splitter.setOpaqueResize(True)
            row_splitters.append(row_splitter)
            self._root_splitter.addWidget(row_splitter)

        # Add widgets to grid, or empty placeholders if not enough widgets
        tab_idx = 0
        for r in range(rows):
            row_splitter = row_splitters[r]
            for c in range(cols):
                if tab_idx < num_tabs:
                    widget = self._chat_tabs[tab_idx]
                    row_splitter.addWidget(widget)
                tab_idx += 1

            # Set equal sizes for row
            row_sizes = [cell_width] * cols
            row_splitter.setSizes(row_sizes)

        # Set root splitter sizes
        root_sizes = [cell_height] * rows
        self._root_splitter.setSizes(root_sizes)

    def _apply_auto_tile(self):
        """Apply automatic tiling based on number of tabs."""
        num_tabs = len(self._chat_tabs)
        if num_tabs == 0:
            return

        # Get current available space
        total_width = max(300, self._root_splitter.width())
        total_height = max(300, self._root_splitter.height())

        # Use simple column layout for auto mode
        if num_tabs <= 3:
            self._create_column_layout(num_tabs, total_width, total_height)
        elif num_tabs <= 6:
            self._create_grid_layout(3, 2, total_width, total_height)
        elif num_tabs <= 9:
            self._create_grid_layout(3, 3, total_width, total_height)
        else:
            # For many tabs, use 4 columns
            self._create_column_layout(4, total_width, total_height)

    def _reset_tile_layout(self):
        """Reset tile layout to auto mode."""
        self._tile_mode = "auto"
        self._apply_auto_tile()

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

        # Clear each tab (docked + floating)
        for widget in self._all_chat_tabs():
            if hasattr(widget, 'clear_chat'):
                widget.clear_chat()

    def _refresh_models(self):
        """Refresh model list in all tabs (docked + floating)."""
        for widget in self._all_chat_tabs():
            if hasattr(widget, 'load_endpoint_config'):
                widget.load_endpoint_config()

    def _open_settings(self):
        """Open AI endpoint settings."""
        try:
            # Import and show endpoint settings dialog
            from aicodeprep_gui.gui.components.ai_settings_dialog import AIEndpointSettingsDialog
            dialog = AIEndpointSettingsDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                self._refresh_models()
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

        # Update all chat tabs (docked + floating)
        for widget in self._all_chat_tabs():
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

        # Update root splitter handle styling
        self._root_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background: {colors['handle']};
            }}
            QSplitter::handle:horizontal {{
                width: 6px;
            }}
            QSplitter::handle:vertical {{
                height: 6px;
            }}
        """)

    def send_context_to_selected_tabs(self, context_text: str, question: str = ""):
        """
        Send context text to all selected tabs.
        Selected tabs have their checkbox checked.
        Automatically sends to AI and scrolls to end.
        """
        count = 0
        for widget in self._all_chat_tabs():
            if hasattr(widget, 'is_selected') and widget.is_selected():
                if hasattr(widget, 'send_context_and_question'):
                    widget.send_context_and_question(context_text, question)
                    count += 1
                elif hasattr(widget, 'send_context'):
                    widget.send_context(context_text)
                    count += 1

        return count

    def get_selected_models(self) -> list[str]:
        """Return the selected model ids for checked chat tabs."""
        models: list[str] = []
        for widget in self._all_chat_tabs():
            if hasattr(widget, 'is_selected') and widget.is_selected():
                if hasattr(widget, 'get_selected_model'):
                    model = widget.get_selected_model()
                else:
                    model = str(
                        getattr(widget, '_selected_model', '') or '').strip()
                if model:
                    models.append(model)
        return models

    def get_selected_tab(self) -> ChatTabWidget:
        """Get the currently selected chat tab widget."""
        index = self._tab_bar.currentIndex()
        if index >= 0 and index < len(self._chat_tabs):
            return self._chat_tabs[index]
        return None

    def get_all_tabs(self) -> list:
        """Get all chat tab widgets (docked + floating)."""
        return self._all_chat_tabs()
