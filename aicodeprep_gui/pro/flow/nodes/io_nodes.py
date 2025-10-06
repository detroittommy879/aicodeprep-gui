"""I/O nodes for Flow Studio (Phase 1 - executable)."""

# Guard NodeGraphQt import so non-installed environments still launch the app.
try:
    from NodeGraphQt import BaseNode  # type: ignore
except Exception as e:  # pragma: no cover
    class BaseNode:  # minimal stub to keep imports safe; not used without NodeGraphQt
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "NodeGraphQt is required for Flow Studio nodes. "
                f"Original import error: {e}"
            )

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
        try:
            self.add_output("text")
        except Exception:
            pass

        # Properties
        try:
            self.create_property("path", "fullcode.txt")
            self.create_property("use_latest_generated", True)
        except Exception:
            pass

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
        try:
            self.add_input("text")
        except Exception:
            pass

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
        try:
            self.add_input("text")
        except Exception:
            pass

        try:
            # Use text widget with clear label for file path
            self.create_property("path", "fullcode.txt",
                                 widget_type="file_save")
            # If file_save not available, fallback to regular text
            if not self.has_property("path"):
                self.create_property("path", "fullcode.txt")
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Write input text to configured file path."""
        text = inputs.get("text") or ""
        path = self.get_property("path") or "output.txt"
        abspath = os.path.join(os.getcwd(), path)
        try:
            with open(abspath, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            if QtWidgets is not None:
                QtWidgets.QMessageBox.warning(
                    None, self.NODE_NAME, f"Failed writing file: {e}")
        return {}


class OutputDisplayNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Output Display"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
            self.create_property("last_result", "")
        except Exception:
            pass

    def run(self, inputs: Dict[str, Any], settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Store text in property for display in Properties Bin."""
        text = inputs.get("text") or ""
        # Store it so Properties Bin can show it
        try:
            self.set_property("last_result", text)
        except Exception:
            pass
        return {}
