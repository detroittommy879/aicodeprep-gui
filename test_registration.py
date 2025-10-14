#!/usr/bin/env python3
"""Test script to understand NodeGraphQt registration."""

from NodeGraphQt import NodeGraph, BaseNode
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)


g = NodeGraph()

print("=== Before registration ===")
print("registered_nodes():", g.registered_nodes())
print("Type:", type(g.registered_nodes()))

# Create a test node class


class TestNode(BaseNode):
    NODE_NAME = 'Test Node'
    __identifier__ = 'test.flow'


# Register it
print("\n=== Registering TestNode ===")
g.register_node(TestNode)

print("\n=== After registration ===")
registered = g.registered_nodes()
print("registered_nodes():", registered)
print("Type:", type(registered))
if registered:
    print("First item type:", type(registered[0]))
    print("First item value:", registered[0])

# Try to create a node
print("\n=== Testing node creation ===")
try:
    node = g.create_node('test.flow.Test Node')
    print("✅ Created node successfully:", node)
except Exception as e:
    print("❌ Failed to create node:", e)

# Test if already registered
print("\n=== Testing double registration ===")
try:
    g.register_node(TestNode)
    print("❌ Double registration succeeded (should have failed)")
except Exception as e:
    print("✅ Double registration failed as expected:", e)
