"""Flow Studio serializer (Phase 2).

Implements load/save/import/export using NodeGraphQt session API with basic redaction.
- Uses graph.save_session(file_path) / graph.load_session(file_path) when available.
- Falls back gracefully and logs descriptive errors.
"""

from __future__ import annotations
from typing import Any, Dict
import logging
import json
import os
import tempfile

try:
    from NodeGraphQt import NodeGraph  # type: ignore
except Exception:
    NodeGraph = Any  # type: ignore


def _has_method(obj: Any, name: str) -> bool:
    return hasattr(obj, name) and callable(getattr(obj, name))


def _normalize_json_object(value: Any) -> Dict[str, Any]:
    """Coerce serialized object payloads back into dictionaries."""
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {}


def _normalize_string(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _clear_graph(graph: NodeGraph) -> None:
    """Best-effort clear of all nodes if load requires an empty scene."""
    try:
        if _has_method(graph, "clear_session"):
            graph.clear_session()
            # Force Qt to process events and flush UI state
            try:
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            except Exception:
                pass
            return
    except Exception as e:
        logging.warning(f"[Flow Serializer] clear_session failed: {e}")
    try:
        nodes = list(getattr(graph, "all_nodes", lambda: [])())
        logging.info(f"[Flow Serializer] Clearing {len(nodes)} nodes...")
        for n in nodes:
            try:
                if _has_method(graph, "delete_node"):
                    graph.delete_node(n)
                elif hasattr(n, "delete"):
                    n.delete()  # type: ignore
            except Exception as e:
                logging.error(f"[Flow Serializer] Failed to delete node: {e}")
        # Force Qt to process events after manual deletion
        try:
            from PySide6.QtCore import QCoreApplication
            QCoreApplication.processEvents()
        except Exception:
            pass
    except Exception as e:
        logging.error(f"[Flow Serializer] Failed to enumerate nodes: {e}")


def save_session(graph: NodeGraph, file_path: str) -> bool:
    """Save the current graph session to JSON file."""
    try:
        if not graph:
            logging.error("[Flow Serializer] save_session: graph is None")
            return False
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        if _has_method(graph, "save_session"):
            graph.save_session(file_path)  # type: ignore
            logging.info(f"[Flow Serializer] Saved session to: {file_path}")
            return True
        logging.error(
            "[Flow Serializer] save_session: graph.save_session not available")
        return False
    except Exception as e:
        logging.error(f"[Flow Serializer] save_session failed: {e}")
        return False


def _normalize_node_data(data: dict) -> dict:
    """
    Normalize node data to ensure 'custom' and 'subgraph_session' fields are dicts.
    NodeGraphQt expects these to be dict objects, not JSON strings.
    If they are JSON strings, parse them back to dicts.
    """
    if "nodes" in data and isinstance(data["nodes"], dict):
        for node_id, node_data in data["nodes"].items():
            if isinstance(node_data, dict):
                node_data["custom"] = _normalize_json_object(
                    node_data.get("custom", {}))
                node_data["subgraph_session"] = _normalize_json_object(
                    node_data.get("subgraph_session", {}))

                custom = node_data["custom"]
                for key in ("model", "model_mode", "provider", "base_url", "path", "output_file"):
                    if key in custom:
                        custom[key] = _normalize_string(custom[key])

    graph_data = data.get("graph")
    if not isinstance(graph_data, dict):
        data["graph"] = {}
    else:
        for key in ("accept_connection_types", "reject_connection_types"):
            if not isinstance(graph_data.get(key), dict):
                graph_data[key] = {}

    if not isinstance(data.get("connections"), list):
        data["connections"] = []

    return data


def validate_flow_structure(data: Any) -> list[str]:
    """Return validation errors for a Flow Studio session payload."""
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Top-level flow payload must be a JSON object."]

    graph = data.get("graph")
    if not isinstance(graph, dict):
        errors.append("'graph' must be an object.")

    nodes = data.get("nodes")
    if not isinstance(nodes, dict) or not nodes:
        errors.append("'nodes' must be a non-empty object.")
        nodes = {}

    for node_id, node_data in nodes.items():
        if not isinstance(node_id, str) or not node_id:
            errors.append("Node ids must be non-empty strings.")
            continue
        if not isinstance(node_data, dict):
            errors.append(f"Node '{node_id}' must be an object.")
            continue
        type_name = node_data.get("type_")
        if not isinstance(type_name, str) or not type_name.strip():
            errors.append(f"Node '{node_id}' is missing a valid 'type_'.")
        if not isinstance(node_data.get("custom", {}), dict):
            errors.append(f"Node '{node_id}' has non-object 'custom'.")
        if not isinstance(node_data.get("subgraph_session", {}), dict):
            errors.append(
                f"Node '{node_id}' has non-object 'subgraph_session'.")

    connections = data.get("connections")
    if not isinstance(connections, list):
        errors.append("'connections' must be a list.")
        connections = []

    for index, connection in enumerate(connections):
        if not isinstance(connection, dict):
            errors.append(f"Connection #{index + 1} must be an object.")
            continue
        for side in ("out", "in"):
            endpoint = connection.get(side)
            if not isinstance(endpoint, list) or len(endpoint) != 2:
                errors.append(
                    f"Connection #{index + 1} field '{side}' must be a 2-item array.")
                continue
            node_id, port_name = endpoint
            if node_id not in nodes:
                errors.append(
                    f"Connection #{index + 1} references missing node '{node_id}'.")
            if not isinstance(port_name, str) or not port_name.strip():
                errors.append(
                    f"Connection #{index + 1} field '{side}' has an invalid port name.")

    return errors


def load_session(graph: NodeGraph, file_path: str) -> bool:
    """Load a graph session from JSON file, replacing current graph."""
    try:
        if not graph:
            logging.error("[Flow Serializer] load_session: graph is None")
            return False
        if not os.path.isfile(file_path):
            logging.error(
                f"[Flow Serializer] load_session: file not found: {file_path}")
            return False

        # Validate JSON before attempting to load
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                logging.error(
                    f"[Flow Serializer] Invalid JSON structure in {file_path}")
                return False
            logging.info(
                f"[Flow Serializer] JSON validation passed for {file_path}")

            # Normalize the data to ensure proper format
            data = _normalize_node_data(data)

            validation_errors = validate_flow_structure(data)
            if validation_errors:
                logging.error(
                    "[Flow Serializer] Invalid flow structure in %s: %s",
                    file_path,
                    "; ".join(validation_errors),
                )
                return False

            # Write normalized data to a temp file for NodeGraphQt to load
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tf:
                json.dump(data, tf, indent=2)
                temp_file = tf.name

            # Update file_path to the normalized temp file
            original_file = file_path
            file_path = temp_file
            logging.info(
                f"[Flow Serializer] Normalized JSON written to temp file: {temp_file}")

        except json.JSONDecodeError as e:
            logging.error(
                f"[Flow Serializer] JSON decode error in {file_path}: {e}")
            return False
        except Exception as e:
            logging.error(
                f"[Flow Serializer] Failed to read/validate {file_path}: {e}")
            return False

        if _has_method(graph, "load_session"):
            # Clear graph and ensure UI is fully updated before loading
            logging.info(
                f"[Flow Serializer] Clearing graph before loading {file_path}...")
            _clear_graph(graph)

            # Additional event processing to ensure clear is complete
            try:
                from PySide6.QtCore import QCoreApplication
                import time
                QCoreApplication.processEvents()
                time.sleep(0.05)  # Small delay to ensure clear is complete
                QCoreApplication.processEvents()
            except Exception:
                pass

            # Now load the session
            logging.info(
                f"[Flow Serializer] Loading session from: {file_path}")
            graph.load_session(file_path)  # type: ignore

            # Clean up temp file if we created one
            if 'temp_file' in locals() and 'original_file' in locals() and temp_file != original_file:
                try:
                    os.unlink(temp_file)
                    logging.info(
                        f"[Flow Serializer] Cleaned up temp file: {temp_file}")
                except Exception as cleanup_err:
                    logging.warning(
                        f"[Flow Serializer] Failed to cleanup temp file: {cleanup_err}")

            # Process events after loading
            try:
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            except Exception:
                pass

            logging.info(
                f"[Flow Serializer] Successfully loaded session from: {original_file if 'original_file' in locals() else file_path}")
            return True
        logging.error(
            "[Flow Serializer] load_session: graph.load_session not available")
        return False
    except Exception as e:
        # Clean up temp file on error
        if 'temp_file' in locals() and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass
        logging.error(
            f"[Flow Serializer] load_session failed: {e}", exc_info=True)
        return False


def _redact_in_place(data: Any) -> Any:
    """
    Recursively remove sensitive fields from a NodeGraphQt session dict.
    Conservative: strip keys commonly used for secrets/headers.
    """
    if isinstance(data, dict):
        redacted: Dict[str, Any] = {}
        for k, v in data.items():
            lk = str(k).lower()
            if lk in {"api_key", "apikey", "secret", "secrets"}:
                continue
            # Optionally strip raw headers if present
            if lk in {"headers", "headers_json"}:
                continue
            redacted[k] = _redact_in_place(v)
        return redacted
    if isinstance(data, list):
        return [_redact_in_place(x) for x in data]
    return data


def export_to_json(graph: NodeGraph, file_path: str, redact: bool = True) -> bool:
    """
    Export the current graph to JSON on disk.
    If redact=True, write to a temp file first, then remove sensitive keys and write the final file.
    """
    try:
        if not graph:
            logging.error("[Flow Serializer] export_to_json: graph is None")
            return False

        if not redact:
            return save_session(graph, file_path)

        # Save into a temp file first
        with tempfile.TemporaryDirectory() as td:
            tmp_path = os.path.join(td, "flow_session.json")
            if not save_session(graph, tmp_path):
                logging.error(
                    "[Flow Serializer] export_to_json: save to temp failed")
                return False
            try:
                with open(tmp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                logging.error(
                    f"[Flow Serializer] export_to_json: failed reading temp JSON: {e}")
                return False

            data = _redact_in_place(data)

            try:
                os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                logging.info(
                    f"[Flow Serializer] Exported (redacted) JSON to: {file_path}")
                return True
            except Exception as e:
                logging.error(
                    f"[Flow Serializer] export_to_json: failed writing final JSON: {e}")
                return False
    except Exception as e:
        logging.error(f"[Flow Serializer] export_to_json failed: {e}")
        return False


def import_from_json(graph: NodeGraph, file_path: str) -> bool:
    """
    Import a graph from a JSON session file (same as load_session).
    """
    return load_session(graph, file_path)
