"""
Keyboard shortcut management for aicodeprep-gui.
Provides centralized keyboard shortcut handling with cross-platform support.
"""

import sys
import platform
from PySide6 import QtCore, QtGui, QtWidgets


def is_macos():
    """Detect if running on macOS for Cmd vs Ctrl handling."""
    return platform.system() == "Darwin"


class KeyboardShortcutManager:
    """
    Manages keyboard shortcuts with platform-specific key handling.
    Provides hardcoded default shortcuts for core application actions.
    """

    def __init__(self, parent=None):
        """
        Initialize the shortcut manager.
        
        Args:
            parent: Parent QWidget (typically main window)
        """
        self.parent = parent
        self.shortcuts = {}
        self._init_default_shortcuts()

    def _init_default_shortcuts(self):
        """Initialize hardcoded default keyboard shortcuts."""
        # Determine modifier key based on platform
        mod = QtCore.Qt.KeyboardModifier.MetaModifier if is_macos() else QtCore.Qt.KeyboardModifier.ControlModifier
        
        # Core action shortcuts
        self.shortcuts = {
            'generate': {
                'key': QtCore.Qt.Key.Key_G,
                'modifiers': mod,
                'description': self.tr('Generate context and copy to clipboard')
            },
            'select_all': {
                'key': QtCore.Qt.Key.Key_A,
                'modifiers': mod,
                'description': self.tr('Select all files in tree')
            },
            'deselect_all': {
                'key': QtCore.Qt.Key.Key_A,
                'modifiers': mod | QtCore.Qt.KeyboardModifier.ShiftModifier,
                'description': self.tr('Deselect all files in tree')
            },
            'open_folder': {
                'key': QtCore.Qt.Key.Key_O,
                'modifiers': mod,
                'description': self.tr('Open folder')
            },
            'preferences': {
                'key': QtCore.Qt.Key.Key_Comma,
                'modifiers': mod,
                'description': self.tr('Open preferences')
            },
            'quit': {
                'key': QtCore.Qt.Key.Key_Q,
                'modifiers': mod,
                'description': self.tr('Quit application')
            },
        }

    def tr(self, text):
        """Translation helper for i18n compatibility."""
        if self.parent and hasattr(self.parent, 'tr'):
            return self.parent.tr(text)
        return text

    def get_shortcut_text(self, action_name):
        """
        Get human-readable shortcut text for display in UI.
        
        Args:
            action_name: Name of the action (e.g., 'generate', 'select_all')
            
        Returns:
            String representation of the shortcut (e.g., "Ctrl+G" or "Cmd+G")
        """
        if action_name not in self.shortcuts:
            return ""
        
        shortcut_data = self.shortcuts[action_name]
        key = shortcut_data['key']
        modifiers = shortcut_data['modifiers']
        
        # Build modifier string
        mod_parts = []
        if modifiers & QtCore.Qt.KeyboardModifier.ControlModifier:
            mod_parts.append("Ctrl")
        if modifiers & QtCore.Qt.KeyboardModifier.MetaModifier:
            mod_parts.append("Cmd" if is_macos() else "Meta")
        if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
            mod_parts.append("Shift")
        if modifiers & QtCore.Qt.KeyboardModifier.AltModifier:
            mod_parts.append("Alt")
        
        # Get key name
        key_name = QtGui.QKeySequence(key).toString()
        
        # Combine
        if mod_parts:
            return "+".join(mod_parts) + "+" + key_name
        return key_name

    def create_shortcut(self, action_name, callback, context=QtCore.Qt.ShortcutContext.ApplicationShortcut):
        """
        Create a QShortcut for the specified action.
        
        Args:
            action_name: Name of the action (must exist in shortcuts dict)
            callback: Function to call when shortcut is triggered
            context: Shortcut context (default: ApplicationShortcut)
            
        Returns:
            QShortcut object or None if action_name not found
        """
        if action_name not in self.shortcuts:
            return None
        
        shortcut_data = self.shortcuts[action_name]
        key_sequence = QtGui.QKeySequence(
            shortcut_data['modifiers'] | shortcut_data['key']
        )
        
        shortcut = QtWidgets.QShortcut(key_sequence, self.parent)
        shortcut.setContext(context)
        shortcut.activated.connect(callback)
        
        return shortcut

    def create_action(self, action_name, callback, parent=None):
        """
        Create a QAction with keyboard shortcut for menu/toolbar use.
        
        Args:
            action_name: Name of the action (must exist in shortcuts dict)
            callback: Function to call when action is triggered
            parent: Parent widget for the action
            
        Returns:
            QAction object or None if action_name not found
        """
        if action_name not in self.shortcuts:
            return None
        
        shortcut_data = self.shortcuts[action_name]
        description = shortcut_data['description']
        
        if parent is None:
            parent = self.parent
        
        action = QtGui.QAction(description, parent)
        
        key_sequence = QtGui.QKeySequence(
            shortcut_data['modifiers'] | shortcut_data['key']
        )
        action.setShortcut(key_sequence)
        action.triggered.connect(callback)
        
        return action

    def get_modifier_key(self):
        """
        Get the primary modifier key for the current platform.
        
        Returns:
            QtCore.Qt.KeyboardModifier (Cmd on macOS, Ctrl elsewhere)
        """
        return QtCore.Qt.KeyboardModifier.MetaModifier if is_macos() else QtCore.Qt.KeyboardModifier.ControlModifier
