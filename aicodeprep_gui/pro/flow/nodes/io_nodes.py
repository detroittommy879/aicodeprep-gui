"""I/O nodes for Flow Studio (Phase 1 - executable)."""

# Guard NodeGraphQt import so non-installed environments still launch the app.
try:
    from NodeGraphQt import BaseNode  # type: ignore
    from NodeGraphQt.constants import NodePropWidgetEnum
except Exception as e:  # pragma: no cover
    class BaseNode:  # minimal stub to keep imports safe; not used without NodeGraphQt
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "NodeGraphQt is required for Flow Studio nodes. "
                f"Original import error: {e}"
            )

    class NodePropWidgetEnum:
        QLINE_EDIT = 3
        FILE_SAVE = 14

from .base import BaseExecNode
from typing import Any, Dict, Optional
import os
import logging

try:
    from PySide6 import QtWidgets
except ImportError:
    QtWidgets = None


class ContextOutputNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Context Output"

    def __init__(self):
        super().__init__()
        # Outputs
        self.add_output("text")

        # Properties
        self.create_property("path", "fullcode.txt")
        self.create_property("use_latest_generated", True)

        # Add read-only text widget to display file path
        try:
            self.add_text_input('_file_display', '',
                                multi_line=False, tab=None)
            # Make it read-only
            try:
                widget = self.get_widget('_file_display')
                if widget and hasattr(widget, 'get_custom_widget'):
                    qt_widget = widget.get_custom_widget()
                    if qt_widget and hasattr(qt_widget, 'setReadOnly'):
                        qt_widget.setReadOnly(True)
                        qt_widget.setStyleSheet(
                            "background: transparent; border: none; color: #888;")
            except Exception:
                pass
        except Exception:
            pass

        # Schedule label display update after node is fully initialized
        try:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._update_node_label)
        except Exception:
            pass

    def _update_node_label(self):
        """Update node display to show file path in node name."""
        try:
            from NodeGraphQt import BaseNode as NGBaseNode
            # Try to get path property value
            path = "fullcode.txt"
            try:
                path = NGBaseNode.get_property(self, "path") or "fullcode.txt"
            except Exception as e:
                logging.debug(f"Error getting path property: {e}")
            # Truncate path if too long
            if len(path) > 15:
                path_display = "..." + path[-12:]
            else:
                path_display = path
            display = f"{self.NODE_NAME}: {path_display}"
            if hasattr(self, 'set_name'):
                self.set_name(display)

            # Update the file display widget
            try:
                if hasattr(self, 'set_property'):
                    from NodeGraphQt import BaseNode as NGBaseNode
                    NGBaseNode.set_property(
                        self, '_file_display', f"📄 {path}", push_undo=False)
            except Exception as e:
                logging.debug(f"Failed to update file display widget: {e}")
        except Exception as e:
            logging.debug(f"Failed to update ContextOutputNode label: {e}")

    def set_property(self, name: str, value, push_undo: bool = True):
        """Override to update node display when path changes."""
        result = super().set_property(name, value, push_undo)
        if name == "path":
            self._update_node_label()
        return result

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Read the context text from path (default: fullcode.txt).
        In future we could regenerate context on-demand.
        """
        path = self.get_property("path") or "fullcode.txt"
        abspath = os.path.join(os.getcwd(), path)
        logging.info("[ContextOutputNode] Resolving context path %s", abspath)
        if not os.path.isfile(abspath):
            logging.warning(
                "[ContextOutputNode] Context file missing at %s", abspath)
            if QtWidgets is not None:
                QtWidgets.QMessageBox.warning(None, self.NODE_NAME,
                                              f"Context file not found: {abspath}\n\n"
                                              "To generate a context file:\n"
                                              "1. Go to File → Generate Code Context\n"
                                              "2. Select files and generate fullcode.txt\n"
                                              "3. Then run the flow again")
            return {}
        try:
            with open(abspath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            logging.info(
                "[ContextOutputNode] Loaded %d characters from context", len(content))
            return {"text": content}
        except Exception as e:
            logging.error(
                "[ContextOutputNode] Failed reading %s: %s", abspath, e)
            if QtWidgets is not None:
                QtWidgets.QMessageBox.warning(
                    None, self.NODE_NAME, f"Error reading context file: {e}")
            return {}


class ClipboardNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Clipboard"

    def __init__(self):
        super().__init__()
        self.add_input("text")

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Copy input text to system clipboard."""
        text = inputs.get("text") or ""
        if not text:
            return {}
        try:
            if QtWidgets is not None:
                clip = QtWidgets.QApplication.clipboard()
                clip.setText(text)
        except Exception:
            pass
        return {}


class FileWriteNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "File Write"

    def __init__(self):
        super().__init__()
        self.add_input("text")

        # Use text widget with clear label for file path
        self.create_property("path", "fullcode.txt",
                             widget_type=NodePropWidgetEnum.FILE_SAVE.value)
        # If file_save not available, fallback to regular text
        if not self.has_property("path"):
            self.create_property("path", "fullcode.txt")

        # Add read-only text widget to display file path
        try:
            self.add_text_input('_file_display', '',
                                multi_line=False, tab=None)
            # Make it read-only
            try:
                widget = self.get_widget('_file_display')
                if widget and hasattr(widget, 'get_custom_widget'):
                    qt_widget = widget.get_custom_widget()
                    if qt_widget and hasattr(qt_widget, 'setReadOnly'):
                        qt_widget.setReadOnly(True)
                        qt_widget.setStyleSheet(
                            "background: transparent; border: none; color: #888;")
            except Exception:
                pass
        except Exception:
            pass

        # Schedule label display update after node is fully initialized
        try:
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, self._update_node_label)
        except Exception:
            pass

    def _update_node_label(self):
        """Update node display to show file path in node name."""
        try:
            from NodeGraphQt import BaseNode as NGBaseNode
            # Try to get path property value
            path = "output.txt"
            try:
                path = NGBaseNode.get_property(self, "path") or "output.txt"
            except Exception as e:
                logging.debug(f"Error getting path property: {e}")
            # Truncate path if too long
            if len(path) > 15:
                path_display = "..." + path[-12:]
            else:
                path_display = path
            display = f"{self.NODE_NAME}: {path_display}"
            if hasattr(self, 'set_name'):
                self.set_name(display)

            # Update the file display widget
            try:
                if hasattr(self, 'set_property'):
                    from NodeGraphQt import BaseNode as NGBaseNode
                    NGBaseNode.set_property(
                        self, '_file_display', f"📝 {path}", push_undo=False)
            except Exception as e:
                logging.debug(f"Failed to update file display widget: {e}")
        except Exception as e:
            logging.debug(f"Failed to update FileWriteNode label: {e}")

    def set_property(self, name: str, value, push_undo: bool = True):
        """Override to update node display when path changes."""
        result = super().set_property(name, value, push_undo)
        if name == "path":
            self._update_node_label()
        return result

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Write input text to configured file path."""
        from pathlib import Path

        text = inputs.get("text") or ""
        path = self.get_property("path") or "output.txt"

        # Expand ~ and make absolute
        if path.startswith("~"):
            abspath = Path(path).expanduser()
        else:
            abspath = Path(os.getcwd()) / path

        try:
            # Ensure parent directory exists
            abspath.parent.mkdir(parents=True, exist_ok=True)
            abspath.write_text(text, encoding="utf-8")

            # Log the full path so user can find it
            logging.info(f"✅ File saved: {abspath}")

        except Exception as e:
            logging.error(f"Failed writing file: {e}")
            if QtWidgets is not None:
                QtWidgets.QMessageBox.warning(
                    None, self.NODE_NAME, f"Failed writing file: {e}")
        return {}


class OutputDisplayNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Output Display"

    def __init__(self):
        super().__init__()
        self.add_input("text")
        self.create_property("last_result", "")

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Store text in property for display in Properties Bin."""
        text = inputs.get("text") or ""
        # Store it so Properties Bin can show it
        try:
            self.set_property("last_result", text)
        except Exception:
            pass
        return {}
