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
import os

# Try to import NodeGraphQt; fallback to a placeholder dock if missing.
try:
    from NodeGraphQt import NodeGraph  # type: ignore
    NG_AVAILABLE = True
except Exception as e:
    NG_AVAILABLE = False
    _NG_IMPORT_ERROR = e


class _ReadOnlyEventFilter(QtCore.QObject):
    """
    Blocks destructive edit shortcuts (del/cut/paste/copy) and certain gestures in read-only mode.
    """

    def eventFilter(self, obj, event):  # noqa: N802
        try:
            et = event.type()
            if et in (QtCore.QEvent.KeyPress, QtCore.QEvent.ShortcutOverride):
                key = event.key()
                mods = int(event.modifiers()) if hasattr(
                    event, "modifiers") else 0
                # Block delete/backspace
                if key in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
                    return True
                # Block copy/cut/paste (Ctrl/Command combinations)
                ctrl = (mods & int(QtCore.Qt.ControlModifier)) or (
                    mods & int(QtCore.Qt.MetaModifier))
                if ctrl and key in (QtCore.Qt.Key_C, QtCore.Qt.Key_X, QtCore.Qt.Key_V):
                    return True
            # Block drag/drop edits
            if et in (QtCore.QEvent.DragEnter, QtCore.QEvent.Drop, QtCore.QEvent.DragMove):
                return True
        except Exception:
            pass
        return False


class _PanEventFilter(QtCore.QObject):
    """
    Event filter to temporarily enable pan mode with the spacebar.
    """

    def __init__(self, viewer, dock_widget):
        super().__init__()
        self.viewer = viewer
        self.dock_widget = dock_widget
        self._previous_drag_mode = None
        self._space_pressed = False

    def eventFilter(self, obj, event):
        from PySide6.QtWidgets import QGraphicsView
        from PySide6.QtCore import Qt

        # Remap LMB to MMB when pan mode is active (toolbar toggle or spacebar)
        try:
            pan_active = getattr(
                self.dock_widget, "_pan_active", False) or self._space_pressed
            if pan_active and event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonRelease):
                if hasattr(event, "buttons") and hasattr(event, "button"):
                    if event.button() == Qt.LeftButton or (event.type() == QtCore.QEvent.MouseMove and (event.buttons() & Qt.LeftButton)):
                        from PySide6.QtGui import QMouseEvent
                        from PySide6.QtWidgets import QApplication
                        # Build synthetic MMB event
                        btn = Qt.MiddleButton if event.type() != QtCore.QEvent.MouseMove else Qt.NoButton
                        buttons = event.buttons()
                        if buttons & Qt.LeftButton:
                            buttons = (
                                buttons & ~Qt.LeftButton) | Qt.MiddleButton
                        ev2 = QMouseEvent(
                            event.type(),
                            getattr(event, "position",
                                    lambda: event.localPos())(),
                            getattr(event, "globalPosition",
                                    lambda: event.globalPos())(),
                            btn,
                            buttons,
                            event.modifiers(),
                        )
                        target = self.viewer.viewport() if hasattr(
                            self.viewer, "viewport") and self.viewer.viewport() else self.viewer
                        QApplication.sendEvent(target, ev2)
                        # Update cursor to hand while panning
                        try:
                            cur = Qt.ClosedHandCursor if event.type() == QtCore.QEvent.MouseButtonPress or (
                                event.type() == QtCore.QEvent.MouseMove and (buttons & Qt.MiddleButton)) else Qt.OpenHandCursor
                            if hasattr(self.viewer, "setCursor"):
                                self.viewer.setCursor(cur)
                            if hasattr(self.viewer, "viewport") and self.viewer.viewport():
                                self.viewer.viewport().setCursor(cur)
                            logging.info("Remapped LMB->MMB for panning")
                        except Exception:
                            pass
                        return True
        except Exception:
            pass

        try:
            if event.type() == QtCore.QEvent.KeyPress and event.key() == Qt.Key_Space and not event.isAutoRepeat():
                if not self._space_pressed:
                    self._space_pressed = True
                    # Store current state before enabling pan
                    self._previous_pan_state = False

                    # Check if we're already in pan mode (for NodeGraphQt)
                    if hasattr(self.viewer, '_pan_mode'):
                        self._previous_pan_state = getattr(
                            self.viewer, '_pan_mode', False)
                    elif hasattr(self.viewer, 'dragMode'):
                        current_mode = self.viewer.dragMode()
                        self._previous_pan_state = (
                            current_mode == QGraphicsView.ScrollHandDrag)

                    # Enable pan mode using standard QGraphicsView methods
                    if hasattr(self.viewer, 'setDragMode'):
                        self.viewer.setDragMode(QGraphicsView.ScrollHandDrag)
                        logging.info(
                            "Space pressed - enabled pan via setDragMode(ScrollHandDrag)")
                    elif hasattr(self.viewer, 'set_drag_mode'):
                        self.viewer.set_drag_mode(QGraphicsView.ScrollHandDrag)
                        logging.info(
                            "Space pressed - enabled pan via set_drag_mode(ScrollHandDrag)")
                    # Cursor hint while space is held
                    try:
                        if hasattr(self.viewer, 'setCursor'):
                            from PySide6.QtCore import Qt as _Qt
                            self.viewer.setCursor(_Qt.OpenHandCursor)
                        if hasattr(self.viewer, "viewport") and self.viewer.viewport():
                            from PySide6.QtCore import Qt as _Qt
                            self.viewer.viewport().setCursor(_Qt.OpenHandCursor)
                    except Exception:
                        pass

                    # Update pan button state
                    if hasattr(self.dock_widget, '_pan_button'):
                        self.dock_widget._pan_button.setChecked(True)

                return True

            elif event.type() == QtCore.QEvent.KeyRelease and event.key() == Qt.Key_Space and not event.isAutoRepeat():
                if self._space_pressed:
                    self._space_pressed = False

                    # Restore previous pan state using standard QGraphicsView methods
                    if hasattr(self.viewer, 'setDragMode'):
                        mode = QGraphicsView.ScrollHandDrag if self._previous_pan_state else QGraphicsView.RubberBandDrag
                        self.viewer.setDragMode(mode)
                        logging.info(
                            f"Space released - restored drag mode to {mode}")
                    elif hasattr(self.viewer, 'set_drag_mode'):
                        mode = QGraphicsView.ScrollHandDrag if self._previous_pan_state else QGraphicsView.RubberBandDrag
                        self.viewer.set_drag_mode(mode)
                        logging.info(
                            f"Space released - restored drag mode to {mode}")
                    # Restore cursor to match pan state
                    try:
                        from PySide6.QtCore import Qt as _Qt
                        cur = _Qt.OpenHandCursor if self._previous_pan_state else _Qt.ArrowCursor
                        if hasattr(self.viewer, 'setCursor'):
                            self.viewer.setCursor(cur)
                        if hasattr(self.viewer, "viewport") and self.viewer.viewport():
                            self.viewer.viewport().setCursor(cur)
                    except Exception:
                        pass

                    # Update pan button state to match previous state
                    if hasattr(self.dock_widget, '_pan_button'):
                        self.dock_widget._pan_button.setChecked(
                            self._previous_pan_state)

                return True

        except Exception as e:
            logging.error(f"Error in pan event filter: {e}")

        return super().eventFilter(obj, event)


class FlowStudioDock(QtWidgets.QDockWidget):
    def __init__(self, parent=None, read_only: bool = False):
        super().__init__("Flow Studio", parent)
        self.setObjectName("flow_studio_dock")

        self.read_only = read_only
        # Track whether pan mode is active (toolbar toggle) to support LMB->MMB remap
        self._pan_active = False

        if not NG_AVAILABLE:
            # Graceful fallback UI for missing dependency
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

        # Get the actual viewer widget - comprehensive detection with debugging
        self.viewer = None

        # Debug: Log what we're working with
        logging.info(f"NodeGraph type: {type(self.graph)}")
        logging.info(
            f"NodeGraph attributes: {[attr for attr in dir(self.graph) if not attr.startswith('_')]}")
        logging.info(f"Widget type: {type(self.graph_widget)}")
        logging.info(
            f"Widget attributes: {[attr for attr in dir(self.graph_widget) if not attr.startswith('_')]}")

        # Try multiple approaches to get the viewer
        potential_viewers = []

        # Approach 1: Direct attributes on graph
        for attr_name in ["viewer", "view", "_viewer", "_view"]:
            if hasattr(self.graph, attr_name):
                try:
                    attr_obj = getattr(self.graph, attr_name)
                    logging.info(
                        f"Found graph.{attr_name}: {type(attr_obj)} - callable: {callable(attr_obj)}")

                    if callable(attr_obj):
                        try:
                            potential_viewer = attr_obj()
                            logging.info(
                                f"Called {attr_name}() -> {type(potential_viewer)}")
                            potential_viewers.append(
                                (f"graph.{attr_name}()", potential_viewer))
                        except Exception as e:
                            logging.info(f"Failed to call {attr_name}(): {e}")
                    else:
                        logging.info(
                            f"Direct access to {attr_name}: {type(attr_obj)}")
                        potential_viewers.append(
                            (f"graph.{attr_name}", attr_obj))
                except Exception as e:
                    logging.info(f"Error accessing graph.{attr_name}: {e}")

        # Approach 2: Attributes on widget
        for attr_name in ["viewer", "view", "_viewer", "_view"]:
            if hasattr(self.graph_widget, attr_name):
                try:
                    attr_obj = getattr(self.graph_widget, attr_name)
                    logging.info(
                        f"Found widget.{attr_name}: {type(attr_obj)} - callable: {callable(attr_obj)}")

                    if callable(attr_obj):
                        try:
                            potential_viewer = attr_obj()
                            logging.info(
                                f"Called widget.{attr_name}() -> {type(potential_viewer)}")
                            potential_viewers.append(
                                (f"widget.{attr_name}()", potential_viewer))
                        except Exception as e:
                            logging.info(
                                f"Failed to call widget.{attr_name}(): {e}")
                    else:
                        logging.info(
                            f"Direct access to widget.{attr_name}: {type(attr_obj)}")
                        potential_viewers.append(
                            (f"widget.{attr_name}", attr_obj))
                except Exception as e:
                    logging.info(f"Error accessing widget.{attr_name}: {e}")

        # Approach 3: Try to find QGraphicsView in widget hierarchy
        try:
            from PySide6.QtWidgets import QGraphicsView

            def find_graphics_view(widget):
                if isinstance(widget, QGraphicsView):
                    return widget
                for child in widget.findChildren(QGraphicsView):
                    return child
                return None

            graphics_view = find_graphics_view(self.graph_widget)
            if graphics_view:
                logging.info(
                    f"Found QGraphicsView in widget hierarchy: {type(graphics_view)}")
                potential_viewers.append(
                    ("widget_hierarchy_search", graphics_view))
        except Exception as e:
            logging.info(f"Error searching widget hierarchy: {e}")

        # Now evaluate all potential viewers
        for source, viewer in potential_viewers:
            if viewer is None:
                continue

            # Check if this looks like a QGraphicsView
            has_drag_mode = hasattr(
                viewer, 'setDragMode') and hasattr(viewer, 'dragMode')
            has_scene = hasattr(viewer, 'scene')
            has_viewport = hasattr(viewer, 'viewport')

            logging.info(
                f"Evaluating {source}: dragMode={has_drag_mode}, scene={has_scene}, viewport={has_viewport}")

            if has_drag_mode and (has_scene or has_viewport):
                self.viewer = viewer
                logging.info(f"Selected viewer from: {source}")
                break

        if not self.viewer:
            logging.error("Failed to find a suitable viewer object")
        else:
            # Log all methods that might be related to pan/drag functionality
            all_methods = [m for m in dir(
                self.viewer) if not m.startswith('__')]
            pan_drag_methods = [
                m for m in all_methods if 'drag' in m.lower() or 'pan' in m.lower()]
            logging.info(f"Final viewer: {type(self.viewer)}")
            logging.info(f"Pan/drag methods: {pan_drag_methods}")

            # Also check for any methods that might control interaction modes
            mode_methods = [m for m in all_methods if any(word in m.lower() for word in [
                                                          'mode', 'state', 'interaction', 'mouse', 'hand'])]
            logging.info(f"Mode/state methods: {mode_methods}")

        # Configure the graph viewer for better usability
        self._configure_viewer()

        # Central wrapper to hold toolbar + graph widget
        wrapper = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self._create_toolbar())
        vbox.addWidget(self.graph_widget)
        self.setWidget(wrapper)

        # Register I/O nodes
        self._register_nodes()
        self._load_default_flow_or_build()

        # Show config instructions if no API keys are configured
        self._check_and_show_config_instructions()

        if read_only:
            self._apply_read_only()

    def _create_toolbar(self):
        """Creates the toolbar with actions and the new pan button."""
        toolbar = QtWidgets.QToolBar("Flow Studio")
        toolbar.setIconSize(QtCore.QSize(16, 16))

        # Pan tool button
        self._pan_button = QtWidgets.QToolButton()
        self._pan_button.setText("✋")
        self._pan_button.setToolTip(
            "Pan Mode (Hold Spacebar for temporary pan)")
        self._pan_button.setCheckable(True)
        self._pan_button.clicked.connect(self._toggle_pan_mode)
        toolbar.addWidget(self._pan_button)

        toolbar.addSeparator()

        self._act_run = toolbar.addAction("Run Flow")
        self._act_run.setEnabled(True)
        self._act_run.triggered.connect(self._on_run_clicked)
        toolbar.addSeparator()
        self._act_import = toolbar.addAction("Import…")
        self._act_export = toolbar.addAction("Export…")

        self._act_import.triggered.connect(self._on_import_clicked)
        self._act_export.triggered.connect(self._on_export_clicked)

        if self.read_only:
            self._act_import.setEnabled(False)
            self._act_export.setEnabled(False)
            self._act_import.setToolTip("Import requires Pro")
            self._act_export.setToolTip("Export requires Pro")

        return toolbar

    def _configure_viewer(self):
        """Sets up the NodeGraphQt viewer with usability enhancements."""
        if not self.viewer:
            return

        from PySide6.QtWidgets import QGraphicsView

        try:
            # Set default mode to selection, not panning.
            if hasattr(self.viewer, 'setDragMode'):
                self.viewer.setDragMode(QGraphicsView.RubberBandDrag)

            # Set grid size
            if hasattr(self.viewer, 'set_grid_size'):
                self.viewer.set_grid_size(20)

            # Enable zooming
            if hasattr(self.viewer, 'set_zoom_lock'):
                self.viewer.set_zoom_lock(False)

            # Enable panning with middle mouse button.
            if hasattr(self.viewer, "set_pan_on_mouse_button"):
                self.viewer.set_pan_on_mouse_button(True)

            # Set a very large scene rect to allow unlimited panning.
            scene = getattr(self.viewer, "scene", lambda: None)()
            if scene and hasattr(scene, "setSceneRect"):
                from PySide6.QtCore import QRectF
                scene.setSceneRect(QRectF(-50000, -50000, 100000, 100000))

            # Make viewer focusable to receive keyboard events
            if hasattr(self.viewer, 'setFocusPolicy'):
                from PySide6.QtCore import Qt
                self.viewer.setFocusPolicy(Qt.StrongFocus)

            # Install event filter for temporary spacebar panning.
            self.pan_filter = _PanEventFilter(self.viewer, self)

            # Install on multiple widgets to ensure keyboard events are caught
            self.viewer.installEventFilter(self.pan_filter)
            if hasattr(self.viewer, "viewport"):
                self.viewer.viewport().installEventFilter(self.pan_filter)

            # Also install on the graph widget itself
            self.graph_widget.installEventFilter(self.pan_filter)

            logging.info(
                "Pan event filter installed on viewer and graph widget")

        except Exception as e:
            logging.error(f"Failed to configure NodeGraph viewer: {e}")

    def _toggle_pan_mode(self, checked):
        """Toggles the viewer's drag mode between selection and panning."""
        if not self.viewer:
            return

        from PySide6.QtWidgets import QGraphicsView

        try:
            # Track active pan state and set cursor hint
            self._pan_active = checked
            try:
                from PySide6.QtCore import Qt as _Qt
                cur = _Qt.OpenHandCursor if checked else _Qt.ArrowCursor
                if hasattr(self.viewer, 'setCursor'):
                    self.viewer.setCursor(cur)
                if hasattr(self.viewer, "viewport") and self.viewer.viewport():
                    self.viewer.viewport().setCursor(cur)
            except Exception:
                pass
            if checked:
                # Enable pan mode - use standard QGraphicsView methods
                if hasattr(self.viewer, 'setDragMode'):
                    self.viewer.setDragMode(QGraphicsView.ScrollHandDrag)
                    logging.info(
                        "Pan mode enabled via setDragMode(ScrollHandDrag)")
                elif hasattr(self.viewer, 'set_drag_mode'):
                    self.viewer.set_drag_mode(QGraphicsView.ScrollHandDrag)
                    logging.info(
                        "Pan mode enabled via set_drag_mode(ScrollHandDrag)")
            else:
                # Enable selection mode - use standard QGraphicsView methods
                if hasattr(self.viewer, 'setDragMode'):
                    self.viewer.setDragMode(QGraphicsView.RubberBandDrag)
                    logging.info(
                        "Selection mode enabled via setDragMode(RubberBandDrag)")
                elif hasattr(self.viewer, 'set_drag_mode'):
                    self.viewer.set_drag_mode(QGraphicsView.RubberBandDrag)
                    logging.info(
                        "Selection mode enabled via set_drag_mode(RubberBandDrag)")
        except Exception as e:
            logging.error(f"Error toggling pan mode: {e}")

    # ---- Node registration ----
    def _register_nodes(self):
        try:
            from .nodes.io_nodes import (
                ContextOutputNode,
                ClipboardNode,
                FileWriteNode,
                OutputDisplayNode,
            )
            from .nodes.llm_nodes import (
                OpenRouterNode,
                OpenAINode,
                GeminiNode,
                OpenAICompatibleNode,
            )
            from .nodes.aggregate_nodes import BestOfNNode

            # Register custom nodes with the graph
            self.graph.register_node(ContextOutputNode)
            self.graph.register_node(ClipboardNode)
            self.graph.register_node(FileWriteNode)
            self.graph.register_node(OutputDisplayNode)

            self.graph.register_node(OpenRouterNode)
            self.graph.register_node(OpenAINode)
            self.graph.register_node(GeminiNode)
            self.graph.register_node(OpenAICompatibleNode)

            self.graph.register_node(BestOfNNode)
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

    def _find_port(self, node, port_name, port_type="output"):
        """
        Find a port by its label name across different NodeGraphQt versions.

        Args:
            node: The node to search for ports
            port_name: The label name of the port (e.g., "text", "candidate1")
            port_type: "output" or "input"

        Returns:
            The port object or None if not found
        """
        getter = getattr(node, "port_by_name", None)
        if callable(getter):
            port = getter(port_name, port_type)
            if port:
                return port

        ports = node.outputs() if port_type == "output" else node.inputs()
        if hasattr(ports, "values"):
            iterable = ports.values()
        else:
            iterable = ports

        for port in iterable:
            name = getattr(port, "port_name", None)
            if callable(name) and name() == port_name:
                return port
            label = getattr(port, "name", None)
            if callable(label) and label() == port_name:
                return port
        return None

    def _get_project_flow_path(self) -> str:
        """
        Return the project-level default flow path: '.aicodeprep-flow.json' in cwd.
        """
        try:
            return os.path.join(os.getcwd(), ".aicodeprep-flow.json")
        except Exception:
            return ""

    # ---- Default flow ----
    def _load_default_flow_or_build(self):
        """Phase 1: Just build in-memory default graph."""
        try:
            # Phase 2: try to load project-level default if present
            try:
                from .serializer import load_session
            except Exception:
                load_session = None  # type: ignore
            project_path = self._get_project_flow_path()
            if load_session and project_path and os.path.isfile(project_path):
                try:
                    if load_session(self.graph, project_path):
                        return
                except Exception:
                    pass
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
                if not in_clip and hasattr(clip, "input_port"):
                    in_clip = clip.input_port("text")

                in_fwr = None
                if hasattr(fwr, "get_input_by_name"):
                    in_fwr = fwr.get_input_by_name("text")
                if not in_fwr and hasattr(fwr, "input_port"):
                    in_fwr = fwr.input_port("text")

                if out_text and in_clip:
                    out_text.connect_to(in_clip)
                if out_text and in_fwr:
                    out_text.connect_to(in_fwr)
            except Exception as e:
                logging.error(f"Failed to connect default flow ports: {e}")

            # Optional: try to auto layout nodes if supported
            try:
                if hasattr(self.graph, "auto_layout_nodes"):
                    self.graph.auto_layout_nodes()
            except Exception:
                pass

            # Persist default to project-level file if not present (Pro only)
            try:
                if not self.read_only:
                    from .serializer import save_session
                    default_path = self._get_project_flow_path()
                    if default_path and not os.path.isfile(default_path):
                        save_session(self.graph, default_path)
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

            # Disable drag & drop on the view if available
            try:
                self.graph_widget.setAcceptDrops(False)
                view = getattr(self.graph, "viewer", None) or getattr(
                    self.graph, "view", None)
                if view and hasattr(view, "viewport"):
                    vp = view.viewport()
                    if vp:
                        vp.setAcceptDrops(False)
            except Exception:
                pass

            # Install a key/gesture filter to block edits
            try:
                self._readonly_filter = _ReadOnlyEventFilter(self)
                self.graph_widget.installEventFilter(self._readonly_filter)
                view = getattr(self.graph, "viewer", None) or getattr(
                    self.graph, "view", None)
                if view and hasattr(view, "viewport"):
                    vp = view.viewport()
                    if vp:
                        vp.installEventFilter(self._readonly_filter)
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
        """Phase 2: Import a flow JSON, replacing current graph (Pro only)."""
        try:
            if self.read_only:
                QtWidgets.QMessageBox.information(
                    self, "Flow Import", "Import requires Pro (graph is read-only in Free mode)."
                )
                return
            settings = QtCore.QSettings("aicodeprep-gui", "FlowStudio")
            start_dir = settings.value("last_import_dir", os.getcwd())
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Import Flow JSON", start_dir, "JSON Files (*.json);;All Files (*)"
            )
            if not path:
                return
            try:
                from .serializer import import_from_json
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Import", f"Serializer unavailable: {e}")
                return
            if import_from_json(self.graph, path):
                settings.setValue("last_import_dir", os.path.dirname(path))
                QtWidgets.QMessageBox.information(
                    self, "Flow Import", "Flow imported successfully.")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Import", "Failed to import flow JSON.")
        except Exception as e:
            logging.error(f"Flow import failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Flow Import", f"Error: {e}")

    def _on_export_clicked(self):
        """Phase 2: Export current flow JSON (redacted). Pro-only."""
        try:
            if self.read_only:
                QtWidgets.QMessageBox.information(
                    self, "Flow Export", "Export requires Pro (graph is read-only in Free mode)."
                )
                return
            settings = QtCore.QSettings("aicodeprep-gui", "FlowStudio")
            start_dir = settings.value("last_export_dir", os.getcwd())
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Flow JSON", os.path.join(
                    start_dir, "flow.json"), "JSON Files (*.json)"
            )
            if not path:
                return
            try:
                from .serializer import export_to_json
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Export", f"Serializer unavailable: {e}")
                return
            if export_to_json(self.graph, path, redact=True):
                settings.setValue("last_export_dir", os.path.dirname(path))
                QtWidgets.QMessageBox.information(
                    self, "Flow Export", "Flow exported successfully.")
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Flow Export", "Failed to export flow JSON.")
        except Exception as e:
            logging.error(f"Flow export failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Flow Export", f"Error: {e}")

    def reset_to_default_flow(self):
        """Phase 2: Reset graph to built-in default and overwrite project-level file if any."""
        try:
            if self.read_only:
                QtWidgets.QMessageBox.information(
                    self, "Reset Flow", "Reset requires Pro (graph is read-only in Free mode)."
                )
                return
            # Clear graph
            try:
                if hasattr(self.graph, "clear_session"):
                    self.graph.clear_session()
                else:
                    for n in list(getattr(self.graph, "all_nodes", lambda: [])()):
                        try:
                            if hasattr(self.graph, "delete_node"):
                                self.graph.delete_node(n)
                            elif hasattr(n, "delete"):
                                n.delete()  # type: ignore
                        except Exception:
                            continue
            except Exception:
                pass

            # Rebuild default in-memory
            self._load_default_flow_or_build()

            # Persist to project-level file
            try:
                from .serializer import save_session
                default_path = self._get_project_flow_path()
                if default_path and not self.read_only:
                    save_session(self.graph, default_path)
            except Exception:
                pass

            QtWidgets.QMessageBox.information(
                self, "Reset Flow", "Flow reset to built-in default.")
        except Exception as e:
            logging.error(f"Flow reset failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Reset Flow", f"Error: {e}")

    def _on_run_clicked(self):
        """Handle Run Flow button click."""
        try:
            from .engine import execute_graph
            execute_graph(self.graph, parent_widget=self)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, "Run Flow", f"Execution failed: {e}")

    def load_template_best_of_5_openrouter(self):
        """
        Build:
            ContextOutput -> [5x OpenRouter LLM nodes] -> BestOfNNode -> Clipboard + FileWrite(best_of_n.txt)
        """
        try:
            # Clear graph first (best-effort)
            try:
                if hasattr(self.graph, "clear_session"):
                    self.graph.clear_session()
                else:
                    for n in list(getattr(self.graph, "all_nodes", lambda: [])()):
                        try:
                            if hasattr(self.graph, "delete_node"):
                                self.graph.delete_node(n)
                        except Exception:
                            continue
            except Exception:
                pass

            # Create nodes
            from .nodes.io_nodes import ContextOutputNode, ClipboardNode, FileWriteNode
            from .nodes.llm_nodes import OpenRouterNode
            from .nodes.aggregate_nodes import BestOfNNode

            ctx = self._create_node_compat(
                ContextOutputNode, "aicp.flow", "Context Output", (0, 0))
            logging.info(f"Created context node: {ctx}")
            if ctx:
                try:
                    outputs = list(ctx.outputs())
                    logging.info(f"Context node outputs: {outputs}")
                    for out in outputs:
                        logging.info(
                            f"  Output port: {out}, name: {getattr(out, 'name', 'N/A')}, type: {type(out)}")
                except Exception as e:
                    logging.error(f"Failed to get context outputs: {e}")

            or_nodes = []
            x = 350
            y = -200
            for i in range(5):
                n = self._create_node_compat(
                    OpenRouterNode, "aicp.flow", "OpenRouter LLM", (x, y + i * 100))
                if n and hasattr(n, "set_property"):
                    n.set_property("model_mode", "random_free")
                    # left blank, random_free will pick
                    n.set_property("model", "")
                logging.info(f"Created OpenRouter node {i}: {n}")
                if n:
                    try:
                        inputs = list(n.inputs())
                        logging.info(f"OpenRouter {i} inputs: {inputs}")
                        for inp in inputs:
                            logging.info(
                                f"  Input port: {inp}, name: {getattr(inp, 'name', 'N/A')}, type: {type(inp)}")
                    except Exception as e:
                        logging.error(
                            f"Failed to get OpenRouter {i} inputs: {e}")
                or_nodes.append(n)

            best = self._create_node_compat(
                BestOfNNode, "aicp.flow", "Best-of-N Synthesizer", (700, 0))
            if best and hasattr(best, "set_property"):
                best.set_property("provider", "openrouter")
                best.set_property("model_mode", "random_free")
                # base_url already defaulted to OpenRouter
            logging.info(f"Created BestOfN node: {best}")
            if best:
                try:
                    inputs = list(best.inputs())
                    logging.info(f"BestOfN inputs: {inputs}")
                    for inp in inputs:
                        logging.info(
                            f"  Input port: {inp}, name: {getattr(inp, 'name', 'N/A')}, type: {type(inp)}")
                except Exception as e:
                    logging.error(f"Failed to get BestOfN inputs: {e}")

            clip = self._create_node_compat(
                ClipboardNode, "aicp.flow", "Clipboard", (1050, -60))
            logging.info(f"Created Clipboard node: {clip}")
            if clip:
                try:
                    inputs = list(clip.inputs())
                    logging.info(f"Clipboard inputs: {inputs}")
                    for inp in inputs:
                        logging.info(
                            f"  Input port: {inp}, name: {getattr(inp, 'name', 'N/A')}, type: {type(inp)}")
                except Exception as e:
                    logging.error(f"Failed to get Clipboard inputs: {e}")

            fwr = self._create_node_compat(
                FileWriteNode, "aicp.flow", "File Write", (1050, 60))
            if fwr and hasattr(fwr, "set_property"):
                fwr.set_property("path", "best_of_n.txt")
            logging.info(f"Created FileWrite node: {fwr}")
            if fwr:
                try:
                    inputs = list(fwr.inputs())
                    logging.info(f"FileWrite inputs: {inputs}")
                    for inp in inputs:
                        logging.info(
                            f"  Input port: {inp}, name: {getattr(inp, 'name', 'N/A')}, type: {type(inp)}")
                except Exception as e:
                    logging.error(f"Failed to get FileWrite inputs: {e}")

            # Wire: ctx.text -> each OpenRouter input.text
            try:
                out_text = self._find_port(ctx, "text", "output")
                logging.info(f"Context output port: {out_text}")

                # Connect each OpenRouter node
                for i, or_node in enumerate(or_nodes):
                    if or_node and out_text:
                        in_text = self._find_port(or_node, "text", "input")
                        logging.info(f"OpenRouter {i} input port: {in_text}")

                        if out_text and in_text:
                            try:
                                out_text.connect_to(in_text)
                                logging.info(
                                    f"Connected ctx -> OpenRouter {i}")
                            except Exception as e:
                                logging.error(
                                    f"Failed to connect ctx -> OpenRouter {i}: {e}")
                        else:
                            logging.warning(
                                f"Missing ports for ctx->OpenRouter {i}: out_text={out_text}, in_text={in_text}")
                    else:
                        logging.warning(
                            f"Missing nodes for ctx->OpenRouter {i}: ctx={ctx}, or_node={or_node}")
            except Exception as e:
                logging.error(
                    f"Failed connecting ctx->OpenRouter: {e}", exc_info=True)

            # Wire: ctx.text -> best.context
            try:
                best_in_ctx = self._find_port(best, "context", "input")
                logging.info(f"Best context input port: {best_in_ctx}")
                if out_text and best_in_ctx:
                    try:
                        out_text.connect_to(best_in_ctx)
                        logging.info(
                            "Successfully connected ctx->best.context")
                    except Exception as conn_err:
                        logging.error(
                            f"Failed to connect ctx->best.context: {conn_err}")
                else:
                    logging.warning(
                        f"Missing ports for ctx->best.context: out_text={out_text}, best_in_ctx={best_in_ctx}")
            except Exception as e:
                logging.error(
                    f"Failed connecting ctx->best.context: {e}", exc_info=True)

            # Wire: each OR.text -> best.candidate{i}
            try:
                for i, n in enumerate(or_nodes, 1):
                    if not n:
                        continue

                    or_out = self._find_port(n, "text", "output")
                    candidate_name = f'candidate{i}'
                    best_in = self._find_port(best, candidate_name, "input")

                    logging.info(f"OpenRouter {i} output port: {or_out}")
                    logging.info(f"Best candidate{i} input port: {best_in}")
                    if or_out and best_in:
                        try:
                            or_out.connect_to(best_in)
                            logging.info(
                                f"Successfully connected OpenRouter {i}->best.candidate{i}")
                        except Exception as conn_err:
                            logging.error(
                                f"Failed to connect OpenRouter {i}->best.candidate{i}: {conn_err}")
                    else:
                        logging.warning(
                            f"Missing ports for OpenRouter {i}->best.candidate{i}: or_out={or_out}, best_in={best_in}")
            except Exception as e:
                logging.error(
                    f"Failed connecting OpenRouter->best candidates: {e}", exc_info=True)

            # Wire: best.text -> Clipboard + FileWrite.text
            try:
                best_out = self._find_port(best, "text", "output")
                in_clip = self._find_port(clip, "text", "input")
                in_fwr = self._find_port(fwr, "text", "input")

                logging.info(f"Best output port: {best_out}")
                logging.info(f"Clipboard input port: {in_clip}")
                logging.info(f"FileWrite input port: {in_fwr}")

                if best_out and in_clip:
                    try:
                        best_out.connect_to(in_clip)
                        logging.info("Successfully connected best->Clipboard")
                    except Exception as conn_err:
                        logging.error(
                            f"Failed to connect best->Clipboard: {conn_err}")
                if best_out and in_fwr:
                    try:
                        best_out.connect_to(in_fwr)
                        logging.info("Successfully connected best->FileWrite")
                    except Exception as conn_err:
                        logging.error(
                            f"Failed to connect best->FileWrite: {conn_err}")
            except Exception as e:
                logging.error(
                    f"Failed connecting best->outputs: {e}", exc_info=True)

            # Optional auto-layout
            try:
                if hasattr(self.graph, "auto_layout_nodes"):
                    self.graph.auto_layout_nodes()
            except Exception:
                pass

        except Exception as e:
            logging.error(f"load_template_best_of_5_openrouter failed: {e}")

    def _check_and_show_config_instructions(self):
        """Check if API keys are configured and show instructions if not."""
        try:
            from aicodeprep_gui.config import load_api_config, get_config_dir
            config = load_api_config()

            # Check if any provider has an API key configured
            has_keys = False
            for provider, provider_config in config.items():
                if provider_config.get("api_key", "").strip():
                    has_keys = True
                    break

            if not has_keys:
                config_dir = get_config_dir()
                config_file = config_dir / "api-keys.toml"
                message = f"""Flow Studio Configuration

To use AI nodes, please configure your API keys:

1. Open: {config_file}
2. Add your API keys to the appropriate sections

Example:
[openrouter]
api_key = "sk-or-v1-your-key-here"

[openai] 
api_key = "sk-your-openai-key-here"

The config file has been created with default settings."""

                QtWidgets.QMessageBox.information(
                    self, "Flow Studio Setup", message)
        except Exception as e:
            logging.error(f"Failed to check config: {e}")

    # Phase 1: Run flow execution
    def run(self):
        """Execute the current flow graph."""
        self._on_run_clicked()
