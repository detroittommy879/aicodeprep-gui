#!/usr/bin/env python3
"""Test the full node registration and creation flow."""

from aicodeprep_gui.pro.flow.nodes.aggregate_nodes import BestOfNNode
from aicodeprep_gui.pro.flow.nodes.io_nodes import ContextOutputNode, ClipboardNode, FileWriteNode, OutputDisplayNode
from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenRouterNode, OpenAINode, GeminiNode, OpenAICompatibleNode
from NodeGraphQt import NodeGraph
from PySide6.QtWidgets import QApplication
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

app = QApplication(sys.argv)


print("=== Creating NodeGraph ===")
g = NodeGraph()

print("\n=== Before registration ===")
print(f"Registered: {g.registered_nodes()}")

print("\n=== Registering nodes ===")
nodes_to_register = [
    ContextOutputNode,
    ClipboardNode,
    FileWriteNode,
    OutputDisplayNode,
    OpenRouterNode,
    OpenAINode,
    GeminiNode,
    OpenAICompatibleNode,
    BestOfNNode,
]

for node_cls in nodes_to_register:
    try:
        g.register_node(node_cls)
        node_identifier = f"{node_cls.__identifier__}.{node_cls.__name__}"
        print(f"✅ Registered: {node_identifier}")
    except Exception as e:
        print(f"❌ Failed to register {node_cls.__name__}: {e}")

print("\n=== After registration ===")
registered = g.registered_nodes()
print(f"Total registered: {len(registered)}")
for r in registered:
    print(f"  {r}")

print("\n=== Testing node creation ===")
test_nodes = [
    ("aicp.flow.OpenAINode", "OpenAI"),
    ("aicp.flow.OpenRouterNode", "OpenRouter"),
    ("aicp.flow.GeminiNode", "Gemini"),
    ("aicp.flow.OpenAICompatibleNode", "OpenAI-Compatible"),
    ("aicp.flow.ContextOutputNode", "Context Output"),
    ("aicp.flow.ClipboardNode", "Clipboard"),
    ("aicp.flow.FileWriteNode", "File Write"),
    ("aicp.flow.OutputDisplayNode", "Output Display"),
    ("aicp.flow.BestOfNNode", "Best-of-N"),
]

for ident, display_name in test_nodes:
    try:
        node = g.create_node(ident, pos=(0, 0))
        print(f"✅ {display_name:20s} -> Created successfully")
        g.delete_node(node)
    except Exception as e:
        print(f"❌ {display_name:20s} -> {e}")

print("\n=== Test complete ===")
