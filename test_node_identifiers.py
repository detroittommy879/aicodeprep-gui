#!/usr/bin/env python3
"""Test script to verify node identifier format."""

from aicodeprep_gui.pro.flow.nodes.io_nodes import ContextOutputNode
from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenRouterNode, OpenAINode
import os
from NodeGraphQt import NodeGraph
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)


# Add project to path
sys.path.insert(0, os.path.dirname(__file__))


g = NodeGraph()

print("=== Node class attributes ===")
print(f"OpenRouterNode.__identifier__: {OpenRouterNode.__identifier__}")
print(f"OpenRouterNode.NODE_NAME: {OpenRouterNode.NODE_NAME}")
print(f"ContextOutputNode.__identifier__: {ContextOutputNode.__identifier__}")
print(f"ContextOutputNode.NODE_NAME: {ContextOutputNode.NODE_NAME}")

print("\n=== Registering nodes ===")
g.register_node(OpenRouterNode)
g.register_node(OpenAINode)
g.register_node(ContextOutputNode)

print("\n=== Registered nodes ===")
registered = g.registered_nodes()
for r in registered:
    print(f"  {r}")

print("\n=== Testing node creation ===")
test_identifiers = [
    "aicp.flow.OpenRouterNode",
    "aicp.flow.OpenAINode",
    "aicp.flow.ContextOutputNode",
]

for ident in test_identifiers:
    try:
        node = g.create_node(ident, pos=(0, 0))
        print(f"✅ '{ident}' -> Success")
        # Clean up
        g.delete_node(node)
    except Exception as e:
        print(f"❌ '{ident}' -> {e}")
