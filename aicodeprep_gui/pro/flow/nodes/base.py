"""Base classes for Flow Studio nodes (Phase 1 - UI only)."""

from typing import Any, Optional

# Guard NodeGraphQt imports to avoid hard failures if missing.
try:
    from NodeGraphQt import BaseNode  # type: ignore
except Exception as e:  # pragma: no cover
    class BaseNode:  # minimal stub to keep imports safe; not used without NodeGraphQt
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "NodeGraphQt is required for Flow Studio nodes. "
                f"Original import error: {e}"
            )


class BaseExecNode(BaseNode):
    """
    Common base for Flow Studio nodes. Phase 1 is UI/scaffold only.
    """
    __identifier__ = "aicp.flow"

    def __init__(self):
        super().__init__()
        # Common version property for future migrations
        try:
            self.create_property("version", "1.0.0")
        except Exception:
            # On older NodeGraphQt versions, create_property may differ.
            pass

    # Helper getters are defensive; rely on name when possible.
    def input_port(self, name: str):
        try:
            # Newer NodeGraphQt versions
            if hasattr(self, "get_input_by_name"):
                return self.get_input_by_name(name)
            if hasattr(self, "port_by_name"):
                return self.port_by_name(name)
            for p in getattr(self, "inputs", lambda: [])():
                if getattr(p, "name", "") == name:
                    return p
        except Exception:
            pass
        return None

    def output_port(self, name: str):
        try:
            if hasattr(self, "get_output_by_name"):
                return self.get_output_by_name(name)
            if hasattr(self, "port_by_name"):
                return self.port_by_name(name)
            for p in getattr(self, "outputs", lambda: [])():
                if getattr(p, "name", "") == name:
                    return p
        except Exception:
            pass
        return None

    # Phase 3 will add run() execution helpers; Phase 1 is visual only.
    def run(self, inputs: dict[str, Any], settings: Optional[dict] = None) -> dict:
        return {}
