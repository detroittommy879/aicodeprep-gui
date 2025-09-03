"""Flow Studio Dock (Phase 1: visual, read-only for Free, no execution).

- Embeds a NodeGraphQt graph widget in a QDockWidget.
- Registers IO nodes and builds a default graph:
  ContextOutputNode -> ClipboardNode
  ContextOutputNode -> FileWriteNode(path='fullcode.txt')
- Toolbar buttons:
  - Run Flow (disabled in Phase 1)
  - Import / Export (stubbed; Phase 2 will implement)
- Graceful fallback if NodeGraphQt is not installed.
"""

from PySide6 import QtWidgets, QtCore
import logging

# Try to import NodeGraphQt; fallback to a placeholder dock if missing.
try:
    from NodeGraphQt import NodeGraph  # type: ignore
    NG_AVAILABLE = True
except Exception as e:
    NG_AVAILABLE = False
    _NG_IMPORT_ERROR = e


class FlowStudioDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None, read_only: bool = False):
        super().__init__("Flow Studio", parent)
        self.setObjectName("flow_studio_dock")

        if not NG_AVAILABLE:
            # Graceful fallback UI: show message about missing dependency
            placeholder = QtWidgets.QWidget()
            lay = QtWidgets.QVBoxLayout(placeholder)
            lay.setContentsMargins(8, 8, 8, 8)
            label = QtWidgets.QLabel(
                "Flow Studio requires the 'NodeGraphQt' package.\n"
                "Install it to enable the node graph view.\n\n"
                f"Import error: {str(_NG_IMPORT_ERROR)}"
            )
            label.setWordWrap(True)
            lay.addWidget(label)
            lay.addStretch(1)
            self.setWidget(placeholder)
            return

        # NodeGraph available
        self.graph = NodeGraph()
        self.graph_widget = self.graph.widget
        # Try to reduce grid square size for better density
        try:
            viewer = getattr(self.graph, "viewer", None) or getattr(
                self.graph, "view", None)
            if viewer and hasattr(viewer, "set_grid_size"):
                viewer.set_grid_size(20)
        except Exception:
            pass

        # Central wrapper to hold toolbar + graph widget
        wrapper = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = QtWidgets.QToolBar("Flow Studio")
        toolbar.setIconSize(QtCore.QSize(16, 16))
        self._act_run = toolbar.addAction("Run Flow")
        self._act_run.setEnabled(False)  # Disabled in Phase 1
        toolbar.addSeparator()
        self._act_import = toolbar.addAction("Import…")
        self._act_export = toolbar.addAction("Export…")

        self._act_import.triggered.connect(self._on_import_clicked)
        self._act_export.triggered.connect(self._on_export_clicked)

        vbox.addWidget(toolbar)
        vbox.addWidget(self.graph_widget)

        self.setWidget(wrapper)

        # Register Phase 1 I/O nodes
        self._register_nodes()

        # Build or load default graph
        self._load_default_flow_or_build()

        # Apply read-only gating for Free users
        if read_only:
            self._apply_read_only()

    # ---- Node registration ----
    def _register_nodes(self):
        try:
            from .nodes.io_nodes import (
                ContextOutputNode,
                ClipboardNode,
                FileWriteNode,
                OutputDisplayNode,
            )
            # Register custom nodes with the graph
            self.graph.register_node(ContextOutputNode)
            self.graph.register_node(ClipboardNode)
            self.graph.register_node(FileWriteNode)
            self.graph.register_node(OutputDisplayNode)
        except Exception as e:
            logging.error(f"Failed to register Flow Studio nodes: {e}")

    def _create_node_compat(self, cls, identifier: str, node_name: str, pos: tuple[int, int]):
        """
        Create a node in a way that works across NodeGraphQt versions.

        Tries, in order:
        1) create_node using the identifier string "identifier.NODE_NAME"
        2) create_node using the class reference
        3) Instantiate the class directly and add via add_node, then set position
        Returns the node instance or None if all attempts fail.
        """
        node = None
        ident_str = f"{identifier}.{node_name}"
        # 1) identifier string
        try:
            node = self.graph.create_node(ident_str, pos=pos)
            if node:
                return node
        except Exception:
            pass
        # 2) class reference (some versions support this)
        try:
            node = self.graph.create_node(cls, pos=pos)
            if node:
                return node
        except Exception:
            pass
        # 3) manual add_node fallback
        try:
            inst = cls()
            if hasattr(self.graph, "add_node"):
                self.graph.add_node(inst)
                # set position if API available
                try:
                    if hasattr(inst, "set_pos"):
                        inst.set_pos(pos[0], pos[1])
                    elif hasattr(inst, "setPos"):
                        inst.setPos(pos[0], pos[1])
                except Exception:
                    pass
                return inst
        except Exception as e:
            logging.error(f"Failed to instantiate/add node {cls}: {e}")
        logging.error(f"Could not create node via any method: {ident_str}")
        return None

    # ---- Default flow ----
    def _load_default_flow_or_build(self):
        """Phase 1: Just build in-memory default graph."""
        try:
            # Create nodes using a compatibility helper (supports multiple NodeGraphQt versions)
            from .nodes.io_nodes import ContextOutputNode, ClipboardNode, FileWriteNode
            ctx = self._create_node_compat(
                ContextOutputNode, "aicp.flow", "Context Output", (0, 0))
            clip = self._create_node_compat(
                ClipboardNode, "aicp.flow", "Clipboard", (280, -60))
            fwr = self._create_node_compat(
                FileWriteNode, "aicp.flow", "File Write", (280, 60))
            if not all([ctx, clip, fwr]):
                logging.error(
                    "Flow Studio default nodes could not be created (one or more None).")
                return

            # Set file path property if available
            try:
                if hasattr(fwr, "set_property"):
                    fwr.set_property("path", "fullcode.txt")
            except Exception:
                pass

            # Connect ports: ctx.text -> clip.text and ctx.text -> fwr.text
            try:
                out_text = None
                if hasattr(ctx, "get_output_by_name"):
                    out_text = ctx.get_output_by_name("text")
                elif hasattr(ctx, "output_port"):
                    out_text = ctx.output_port("text")

                in_clip = None
                if hasattr(clip, "get_input_by_name"):
                    in_clip = clip.get_input_by_name("text")

                in_fwr = None
                if hasattr(fwr, "get_input_by_name"):
                    in_fwr = fwr.get_input_by_name("text")

                if out_text and in_clip:
                    self.graph.connect_ports(out_text, in_clip)
                if out_text and in_fwr:
                    self.graph.connect_ports(out_text, in_fwr)
            except Exception as e:
                logging.error(f"Failed to connect default flow ports: {e}")

            # Optional: try to auto layout nodes if supported
            try:
                if hasattr(self.graph, "auto_layout_nodes"):
                    self.graph.auto_layout_nodes()
            except Exception:
                pass

        except Exception as e:
            logging.error(f"Failed to build default Flow Studio graph: {e}")

    # ---- Read-only gating for Free mode ----
    def _apply_read_only(self):
        """Disable add/delete/connect editing while keeping pan/zoom/inspect."""
        try:
            # Disable context menu on the scene widget
            try:
                self.graph_widget.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
            except Exception:
                pass

            # Lock all current ports to prevent new connections
            try:
                for node in self.graph.all_nodes():
                    for port in list(getattr(node, "inputs", lambda: [])()) + list(
                        getattr(node, "outputs", lambda: [])()
                    ):
                        # Try common API names that might exist across versions
                        for attr in ("set_locked", "setLock", "set_locked_state"):
                            if hasattr(port, attr):
                                try:
                                    getattr(port, attr)(True)
                                    break
                                except Exception:
                                    continue
            except Exception:
                pass
        except Exception as e:
            logging.error(f"Failed to apply Flow Studio read-only mode: {e}")

    # ---- Toolbar handlers (Phase 1: stubs) ----
    def _on_import_clicked(self):
        QtWidgets.QMessageBox.information(
            self,
            "Flow Import",
            "Import is coming in Phase 2 (persistence & JSON).",
        )

    def _on_export_clicked(self):
        QtWidgets.QMessageBox.information(
            self,
            "Flow Export",
            "Export is coming in Phase 2 (persistence & JSON).",
        )

    # Placeholder for Phase 3
    def run(self):
        QtWidgets.QMessageBox.information(
            self,
            "Run Flow",
            "Execution engine arrives in Phase 3.",
        )
