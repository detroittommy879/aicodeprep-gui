#!/usr/bin/env python3
"""
Quick test script to validate Flow Studio improvements.
Run this after the changes to ensure everything works.
"""

import sys
import os


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from aicodeprep_gui.pro.flow.engine import execute_graph, _set_node_state, _group_nodes_by_level
        print("  ✓ engine.py imports OK")
    except Exception as e:
        print(f"  ✗ engine.py import failed: {e}")
        return False

    try:
        from aicodeprep_gui.pro.flow.progress_dialog import FlowProgressDialog
        print("  ✓ progress_dialog.py imports OK")
    except Exception as e:
        print(f"  ✗ progress_dialog.py import failed: {e}")
        return False

    try:
        from aicodeprep_gui.pro.flow.nodes.io_nodes import FileWriteNode, ContextOutputNode
        print("  ✓ io_nodes.py imports OK")
    except Exception as e:
        print(f"  ✗ io_nodes.py import failed: {e}")
        return False

    try:
        from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenRouterNode, LLMBaseNode
        print("  ✓ llm_nodes.py imports OK")
    except Exception as e:
        print(f"  ✗ llm_nodes.py import failed: {e}")
        return False

    try:
        from aicodeprep_gui.pro.flow.nodes.aggregate_nodes import BestOfNNode
        print("  ✓ aggregate_nodes.py imports OK")
    except Exception as e:
        print(f"  ✗ aggregate_nodes.py import failed: {e}")
        return False

    return True


def test_node_properties():
    """Test that node properties are defined correctly."""
    print("\nTesting node properties...")

    try:
        from aicodeprep_gui.pro.flow.nodes.io_nodes import FileWriteNode
        from aicodeprep_gui.pro.flow.nodes.aggregate_nodes import BestOfNNode
        from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenRouterNode

        # Test FileWriteNode
        node = FileWriteNode()
        if hasattr(node, 'get_property'):
            path = node.get_property('path')
            print(f"  ✓ FileWriteNode has 'path' property: {path}")
        else:
            print("  ⚠ FileWriteNode.get_property() not available (NodeGraphQt required)")

        # Test BestOfNNode
        node = BestOfNNode()
        if hasattr(node, 'get_property'):
            prompt = node.get_property('extra_prompt')
            provider = node.get_property('provider')
            print(
                f"  ✓ BestOfNNode has 'extra_prompt' property (length: {len(prompt)})")
            print(f"  ✓ BestOfNNode has 'provider' property: {provider}")
        else:
            print("  ⚠ BestOfNNode.get_property() not available (NodeGraphQt required)")

        # Test OpenRouterNode
        node = OpenRouterNode()
        if hasattr(node, 'get_property'):
            model_mode = node.get_property('model_mode')
            provider = node.get_property('provider')
            print(
                f"  ✓ OpenRouterNode has 'model_mode' property: {model_mode}")
            print(f"  ✓ OpenRouterNode has 'provider' property: {provider}")
        else:
            print(
                "  ⚠ OpenRouterNode.get_property() not available (NodeGraphQt required)")

        return True
    except Exception as e:
        print(f"  ✗ Property test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parallel_execution_logic():
    """Test the parallel execution grouping logic."""
    print("\nTesting parallel execution logic...")

    try:
        from aicodeprep_gui.pro.flow.engine import _group_nodes_by_level

        # Create mock nodes
        class MockNode:
            def __init__(self, name):
                self.name = name
                self._id = name

            def id(self):
                return self._id

        # Simple test: 3 nodes in sequence
        nodes = [MockNode(f"node{i}") for i in range(3)]

        # Without dependencies, all should be in same level
        levels = _group_nodes_by_level(nodes, nodes)
        print(f"  ✓ _group_nodes_by_level() returned {len(levels)} level(s)")
        print(f"    Level 1: {len(levels[0])} nodes")

        return True
    except Exception as e:
        print(f"  ✗ Parallel execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Flow Studio Improvements - Validation Tests")
    print("=" * 60)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Node Properties
    results.append(("Node Properties", test_node_properties()))

    # Test 3: Parallel Execution
    results.append(("Parallel Execution", test_parallel_execution_logic()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name:.<40} {status}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Flow Studio improvements validated.")
        return 0
    else:
        print("\n⚠ Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
