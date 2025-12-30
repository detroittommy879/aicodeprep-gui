"""
Flow execution engine for NodeGraphQt-based workflows.
Provides topological sorting and parallel execution of executable nodes.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Set, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# Qt for popups
try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    QtWidgets = None
    QtCore = None


def _safe_node_id(node) -> str:
    """Get a safe string ID for a node."""
    try:
        return str(node.id())
    except Exception:
        try:
            return str(node.id)
        except Exception:
            return f"node_{id(node)}"


def _input_ports(node) -> List:
    """Get input ports for a node, handling different NodeGraphQt versions."""
    for api in ("input_ports", "inputs"):
        if hasattr(node, api):
            try:
                ports = getattr(node, api)()
                if isinstance(ports, dict):
                    return list(ports.values())
                return list(ports)
            except Exception:
                pass
    try:
        return list(node.inputs())
    except Exception:
        return []


def _output_ports(node) -> List:
    """Get output ports for a node, handling different NodeGraphQt versions."""
    for api in ("output_ports", "outputs"):
        if hasattr(node, api):
            try:
                ports = getattr(node, api)()
                if isinstance(ports, dict):
                    return list(ports.values())
                return list(ports)
            except Exception:
                pass
    try:
        return list(node.outputs())
    except Exception:
        return []


def _port_name(port) -> str:
    """Get the name of a port, handling different NodeGraphQt versions."""
    for name_attr in ("name", "port_name", "label"):
        if hasattr(port, name_attr):
            try:
                attr = getattr(port, name_attr)
                # Try calling it if it's a method
                if callable(attr):
                    result = attr()
                    return str(result)
                else:
                    return str(attr)
            except Exception:
                continue
    return f"port_{id(port)}"


def _connected_input_sources(port) -> List[Tuple[Any, Any]]:
    """
    For an input port, return list of (src_node, src_port) connected to it.
    """
    out = []
    for api in ("connected_ports", "connections"):
        if hasattr(port, api):
            try:
                conns = getattr(port, api)()
                for cp in conns:
                    try:
                        n = cp.node()
                        if hasattr(cp, "port_type") and getattr(cp, "port_type") == "in":
                            pass
                        out.append((n, cp))
                    except Exception:
                        continue
                if out:
                    return out
            except Exception:
                continue
    return []


def topological_order(nodes) -> List[Any]:
    """
    Best-effort topological order using input connections as dependencies.
    """
    node_list = list(nodes)
    indeg: Dict[str, int] = {}
    id_to_node: Dict[str, Any] = {}

    # Build indegree
    for n in node_list:
        nid = _safe_node_id(n)
        id_to_node[nid] = n
        indeg[nid] = 0

    for n in node_list:
        nid = _safe_node_id(n)
        for ip in _input_ports(n):
            srcs = _connected_input_sources(ip)
            for (src_node, src_port) in srcs:
                if src_node is None:
                    continue
                sid = _safe_node_id(src_node)
                if sid in indeg and sid != nid:
                    indeg[nid] += 1

    # Kahn's algorithm
    queue = [id_to_node[nid] for nid, d in indeg.items() if d == 0]
    order: List[Any] = []
    visited: Set[str] = set()

    while queue:
        u = queue.pop(0)
        uid = _safe_node_id(u)
        if uid in visited:
            continue
        visited.add(uid)
        order.append(u)

        # Decrement indeg of neighbors
        for v in node_list:
            vid = _safe_node_id(v)
            if vid in visited:
                continue
            # If v depends on u
            dep = False
            for ip in _input_ports(v):
                for (src_node, src_port) in _connected_input_sources(ip):
                    if src_node and _safe_node_id(src_node) == uid:
                        dep = True
                        break
                if dep:
                    break
            if dep:
                indeg[vid] -= 1
                if indeg[vid] <= 0:
                    queue.append(v)

    # If cycle, just append remaining
    if len(order) < len(node_list):
        for n in node_list:
            if n not in order:
                order.append(n)

    return order


def _gather_inputs_for_node(graph, node, results: Dict[Tuple[str, str], Any]) -> Dict[str, Any]:
    """
    Build {input_port_name: value} from upstream results.
    """
    inputs: Dict[str, Any] = {}
    for ip in _input_ports(node):
        ip_name = _port_name(ip)
        srcs = _connected_input_sources(ip)
        if not srcs:
            continue
        # Take the first source by default (multi-in ports merge strategy can be added later)
        src_node, src_port = srcs[0]
        out_key = (_safe_node_id(src_node), _port_name(src_port))
        if out_key in results:
            inputs[ip_name] = results[out_key]
    return inputs


def _set_node_state(node, state: str):
    """
    Set visual state of a node: 'pending', 'running', 'completed', 'error'.
    Uses node coloring to show execution state.
    """
    if not hasattr(node, 'set_color'):
        return

    try:
        # Color scheme for execution states
        colors = {
            'pending': (100, 100, 100),      # Gray
            'running': (255, 200, 0),        # Yellow/amber
            'completed': (50, 200, 100),     # Green
            'error': (255, 50, 50)           # Red
        }

        if state in colors:
            r, g, b = colors[state]
            node.set_color(r, g, b)
    except Exception as e:
        logging.debug(f"Failed to set node color: {e}")


def _group_nodes_by_level(order: List[Any], nodes_list: List[Any]) -> List[List[Any]]:
    """
    Group nodes into execution levels based on dependencies.
    Nodes at the same level can be executed in parallel.
    """
    if not order:
        return []

    # Build dependency map
    depends_on: Dict[str, Set[str]] = {}
    for node in order:
        nid = _safe_node_id(node)
        depends_on[nid] = set()

        for ip in _input_ports(node):
            for (src_node, src_port) in _connected_input_sources(ip):
                if src_node:
                    sid = _safe_node_id(src_node)
                    if sid != nid:
                        depends_on[nid].add(sid)

    # Assign levels
    levels: List[List[Any]] = []
    remaining = set(order)
    completed: Set[str] = set()

    while remaining:
        # Find nodes with all dependencies satisfied
        current_level = []
        for node in list(remaining):
            nid = _safe_node_id(node)
            if depends_on[nid].issubset(completed):
                current_level.append(node)

        if not current_level:
            # Cycle detected or error - add remaining nodes to final level
            current_level = list(remaining)

        levels.append(current_level)
        for node in current_level:
            remaining.discard(node)
            completed.add(_safe_node_id(node))

    return levels


def _execute_node_worker(node, in_data: Dict[str, Any]) -> Tuple[Any, Dict[str, Any], Optional[Exception]]:
    """
    Worker function to execute a single node. Returns (node, output, error).
    This must catch ALL exceptions to prevent thread pool crashes.
    """
    try:
        node_name = getattr(node, 'NODE_NAME', 'node')
        logging.info(f"Executing node: {node_name}")
        out = node.run(in_data, settings=None) or {}
        logging.info(f"Node {node_name} completed successfully")
        return (node, out, None)
    except KeyboardInterrupt:
        # Allow user interruption
        logging.info(f"Node execution interrupted by user")
        raise
    except Exception as e:
        node_name = getattr(node, 'NODE_NAME', 'node')
        logging.error(f"Node '{node_name}' failed: {e}", exc_info=True)
        return (node, {}, e)


def execute_graph(graph, parent_widget=None, show_progress: bool = True) -> None:
    """
    Execute the entire graph with parallel execution for nodes at the same level.

    Args:
        graph: The NodeGraphQt graph to execute
        parent_widget: Parent widget for dialogs
        show_progress: Whether to show progress dialog
    """
    progress_dialog = None

    try:
        nodes = graph.all_nodes()
    except Exception as e:
        logging.error(f"Graph error: {e}", exc_info=True)
        if QtWidgets is not None:
            QtWidgets.QMessageBox.warning(
                parent_widget, "Run Flow", f"Graph error: {e}")
        return

    order = topological_order(nodes)

    # Filter to executable nodes only
    exec_nodes = [n for n in order if hasattr(
        n, "run") and callable(getattr(n, "run"))]

    # Create progress dialog if requested
    if show_progress and QtWidgets is not None:
        try:
            from .progress_dialog import FlowProgressDialog
            progress_dialog = FlowProgressDialog(
                parent_widget, total_nodes=len(exec_nodes))
            progress_dialog.show()
            progress_dialog.set_status("Preparing to execute flow...")
            QtCore.QCoreApplication.processEvents()
        except Exception as e:
            logging.error(
                f"Could not create progress dialog: {e}", exc_info=True)

    # Mark all executable nodes as pending
    for node in exec_nodes:
        _set_node_state(node, 'pending')
        if progress_dialog:
            node_name = getattr(node, 'NODE_NAME', 'node')
            progress_dialog.add_node_status(node_name, "Pending", "gray")

    # Process QT events to update UI
    if QtWidgets is not None and QtCore is not None:
        QtCore.QCoreApplication.processEvents()

    # Group nodes by dependency level for parallel execution
    levels = _group_nodes_by_level(exec_nodes, nodes)
    results: Dict[Tuple[str, str], Any] = {}

    execution_failed = False

    try:
        for level_idx, level_nodes in enumerate(levels):
            # Check for cancellation
            if progress_dialog and progress_dialog.is_cancelled():
                logging.info("Flow execution cancelled by user")
                if progress_dialog:
                    progress_dialog.execution_complete(success=False)
                return

            logging.info(
                f"Executing level {level_idx + 1}/{len(levels)} with {len(level_nodes)} node(s)")

            if progress_dialog:
                if len(level_nodes) == 1:
                    progress_dialog.set_status(
                        f"Executing node {level_idx + 1}/{len(exec_nodes)}...")
                else:
                    progress_dialog.set_status(
                        f"Executing {len(level_nodes)} nodes in parallel (level {level_idx + 1}/{len(levels)})...")

            if len(level_nodes) == 1:
                # Single node - execute directly
                node = level_nodes[0]
                node_name = getattr(node, 'NODE_NAME', 'node')

                _set_node_state(node, 'running')
                if progress_dialog:
                    progress_dialog.update_node_status(
                        node_name, "Running...", "orange")
                if QtWidgets is not None and QtCore is not None:
                    QtCore.QCoreApplication.processEvents()

                in_data = _gather_inputs_for_node(graph, node, results)
                node_obj, out, error = _execute_node_worker(node, in_data)

                if error:
                    _set_node_state(node, 'error')
                    if progress_dialog:
                        progress_dialog.update_node_status(
                            node_name, f"✗ Error: {str(error)[:50]}", "red")
                    # Log error but don't show blocking dialog during execution
                    logging.error(f"Node '{node_name}' failed: {error}")
                else:
                    _set_node_state(node, 'completed')
                    if progress_dialog:
                        progress_dialog.update_node_status(
                            node_name, "✓ Completed", "green")
                        progress_dialog.increment_progress()

                # Store outputs
                for op in _output_ports(node):
                    oname = _port_name(op)
                    if oname in out:
                        results[(_safe_node_id(node), oname)] = out[oname]
            else:
                # Multiple nodes - execute in parallel using ThreadPoolExecutor
                logging.info(f"Executing {len(level_nodes)} nodes in parallel")

                # Mark all as running
                for node in level_nodes:
                    node_name = getattr(node, 'NODE_NAME', 'node')
                    _set_node_state(node, 'running')
                    if progress_dialog:
                        progress_dialog.update_node_status(
                            node_name, "Running...", "orange")
                if QtWidgets is not None and QtCore is not None:
                    QtCore.QCoreApplication.processEvents()

                # Prepare inputs for each node
                node_inputs = [(node, _gather_inputs_for_node(
                    graph, node, results)) for node in level_nodes]

                # Execute in parallel
                with ThreadPoolExecutor(max_workers=min(len(level_nodes), 5)) as executor:
                    futures = {executor.submit(_execute_node_worker, node, in_data): node
                               for node, in_data in node_inputs}

                    for future in as_completed(futures):
                        node = futures[future]
                        node_name = getattr(node, 'NODE_NAME', 'node')

                        try:
                            node_obj, out, error = future.result(
                                timeout=600)  # 10 minute timeout per node for LLM calls
                        except Exception as future_error:
                            # If future.result() itself fails, treat it as a node error
                            logging.error(
                                f"Failed to get result from node '{node_name}': {future_error}", exc_info=True)
                            node_obj = node
                            out = {}
                            error = future_error

                        if error:
                            _set_node_state(node_obj, 'error')
                            if progress_dialog:
                                progress_dialog.update_node_status(
                                    node_name, f"✗ Error: {str(error)[:50]}", "red")
                            # Log error but don't show blocking dialog during execution
                            logging.error(
                                f"Node '{node_name}' failed: {error}")
                        else:
                            _set_node_state(node_obj, 'completed')
                            if progress_dialog:
                                progress_dialog.update_node_status(
                                    node_name, "✓ Completed", "green")
                                progress_dialog.increment_progress()

                        # Process UI events after each node completes
                        if QtWidgets is not None and QtCore is not None:
                            QtCore.QCoreApplication.processEvents()

                        # Store outputs
                        for op in _output_ports(node_obj):
                            oname = _port_name(op)
                            if oname in out:
                                results[(_safe_node_id(node_obj), oname)
                                        ] = out[oname]

            # Process QT events after each level
            if QtWidgets is not None and QtCore is not None:
                QtCore.QCoreApplication.processEvents()

    except Exception as e:
        logging.error(
            f"Flow execution failed with exception: {e}", exc_info=True)
        execution_failed = True
        if progress_dialog:
            progress_dialog.execution_complete(success=False)
        if QtWidgets is not None:
            QtWidgets.QMessageBox.critical(
                parent_widget, "Flow Execution Error",
                f"Flow execution failed with error:\n\n{str(e)}\n\nCheck the logs for more details.")
        return
    finally:
        # Always mark execution complete
        if progress_dialog and not execution_failed:
            progress_dialog.execution_complete(success=True)
