"""I/O nodes for Flow Studio (Phase 1 - visual scaffold only)."""

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

        # Properties (UI placeholders for Phase 1)
        try:
            self.create_property("path", "fullcode.txt")
            self.create_property("use_latest_generated", True)
        except Exception:
            pass


class ClipboardNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Clipboard"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
        except Exception:
            pass


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
            self.create_property("path", "fullcode.txt")
        except Exception:
            pass


class OutputDisplayNode(BaseExecNode):
    __identifier__ = "aicp.flow"
    NODE_NAME = "Output Display"

    def __init__(self):
        super().__init__()
        try:
            self.add_input("text")
        except Exception:
            pass

        # For Phase 1, store a placeholder last_result property for display via Properties Bin later
        try:
            self.create_property("last_result", "")
        except Exception:
            pass
