"""
Flow execution engine for NodeGraphQt-based workflows.
Provides topological sorting and sequential execution of executable nodes.
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple, Set, Optional
import logging

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
                return str(getattr(port, name_attr))
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


def execute_graph(graph, parent_widget=None) -> None:
    """
    Execute the entire graph once in topological order.
    """
    try:
        nodes = graph.all_nodes()
    except Exception as e:
        if QtWidgets is not None:
            QtWidgets.QMessageBox.warning(parent_widget, "Run Flow", f"Graph error: {e}")
        return

    order = topological_order(nodes)
    results: Dict[Tuple[str, str], Any] = {}

    for node in order:
        # Some nodes are BaseExecNode; check for run()
        if not hasattr(node, "run") or not callable(getattr(node, "run")):
            # Skip non-exec nodes (cosmetic)
            continue

        # Build inputs from upstream outputs
        in_data = _gather_inputs_for_node(graph, node, results)
        try:
            out = node.run(in_data, settings=None) or {}
        except Exception as e:
            logging.error(f"Node '{getattr(node, 'NODE_NAME', 'node')}' failed: {e}")
            if QtWidgets is not None:
                QtWidgets.QMessageBox.warning(parent_widget, "Run Flow", f"Node failed: {e}")
            out = {}

        # Store outputs
        for op in _output_ports(node):
            oname = _port_name(op)
            if oname in out:
                results[(_safe_node_id(node), oname)] = out[oname]