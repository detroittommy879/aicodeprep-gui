"""Serializer stubs for Flow Studio (Phase 1).

Phase 2 will implement real load/save using NodeGraphQt's session API.
These functions are placeholders to keep imports stable across phases.
"""

from __future__ import annotations
from typing import Optional, Any
import logging

try:
    # Not strictly needed in Phase 1, but we type-reference for later phases.
    from NodeGraphQt import NodeGraph  # type: ignore
except Exception:
    NodeGraph = Any  # type: ignore


def save_session(graph: NodeGraph, file_path: str) -> bool:
    """Phase 1 stub: log intent and return False."""
    logging.info(
        f"[Flow Serializer] save_session called for: {file_path} (Phase 1 stub)")
    return False


def load_session(graph: NodeGraph, file_path: str) -> bool:
    """Phase 1 stub: log intent and return False."""
    logging.info(
        f"[Flow Serializer] load_session called for: {file_path} (Phase 1 stub)")
    return False


def export_to_json(graph: NodeGraph, file_path: str, redact: bool = True) -> bool:
    """Phase 1 stub: log intent and return False."""
    logging.info(
        f"[Flow Serializer] export_to_json called for: {file_path}, redact={redact} (Phase 1 stub)")
    return False


def import_from_json(graph: NodeGraph, file_path: str) -> bool:
    """Phase 1 stub: log intent and return False."""
    logging.info(
        f"[Flow Serializer] import_from_json called for: {file_path} (Phase 1 stub)")
    return False
