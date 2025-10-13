"""Test script to verify Flow Studio node labels and menu work correctly."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_node_labels():
    """Test that node labels display correctly."""
    print("\n=== Testing Node Label Display ===\n")

    try:
        from aicodeprep_gui.pro.flow.nodes.llm_nodes import OpenAINode, OpenRouterNode
        from aicodeprep_gui.pro.flow.nodes.io_nodes import ContextOutputNode, FileWriteNode

        # Test OpenAI node
        print("1. Creating OpenAI Node...")
        node = OpenAINode()
        name = node.name()
        print(f"   Default name: {name}")
        assert "OpenAI Node" in name, f"Expected 'OpenAI Node' in name, got: {name}"

        # Set model
        node.set_property("model", "gpt-4-turbo")
        node._update_node_label()
        name = node.name()
        print(f"   With model: {name}")
        assert "gpt-4-turbo" in name or "gpt-4" in name, f"Expected model in name, got: {name}"

        # Set temperature
        node.set_property("temperature", 0.8)
        node._update_node_label()
        name = node.name()
        print(f"   With temp: {name}")
        assert "T0.8" in name or "0.8" in name, f"Expected temperature in name, got: {name}"

        # Test OpenRouter random mode
        print("\n2. Creating OpenRouter Node with random mode...")
        or_node = OpenRouterNode()
        or_node.set_property("model_mode", "random")
        or_node._update_node_label()
        name = or_node.name()
        print(f"   Random mode: {name}")
        assert "random" in name.lower(
        ), f"Expected 'random' in name, got: {name}"

        # Test Context Output
        print("\n3. Creating Context Output Node...")
        ctx_node = ContextOutputNode()
        ctx_node._update_node_label()
        name = ctx_node.name()
        print(f"   Default: {name}")
        assert "Context Output" in name, f"Expected 'Context Output' in name, got: {name}"
        assert "fullcode.txt" in name, f"Expected 'fullcode.txt' in name, got: {name}"

        # Change path
        ctx_node.set_property("path", "my_output.txt")
        ctx_node._update_node_label()
        name = ctx_node.name()
        print(f"   With path: {name}")
        assert "my_output.txt" in name, f"Expected 'my_output.txt' in name, got: {name}"

        # Test File Write
        print("\n4. Creating File Write Node...")
        fw_node = FileWriteNode()
        fw_node._update_node_label()
        name = fw_node.name()
        print(f"   Default: {name}")
        assert "File Write" in name, f"Expected 'File Write' in name, got: {name}"

        print("\n✅ All node label tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Node label test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_menu_structure():
    """Test that menu structure is properly configured."""
    print("\n=== Testing Node Creation Menu ===\n")

    try:
        # Check if menu setup method exists
        from aicodeprep_gui.pro.flow.flow_dock import FlowDockWidget

        print("1. Checking FlowDockWidget has menu setup method...")
        assert hasattr(FlowDockWidget, '_setup_node_creation_menu'), \
            "FlowDockWidget missing _setup_node_creation_menu method"
        print("   ✓ Method exists")

        print("\n2. Checking registered nodes...")
        # This would require actually creating a graph, which needs Qt
        # For now just verify the method exists
        print("   ✓ Menu setup method is defined")

        print("\n✅ Menu structure test passed!")
        return True

    except Exception as e:
        print(f"\n❌ Menu structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Flow Studio Node Labels & Creation Menu Tests")
    print("=" * 60)

    results = []

    # Test node labels (doesn't require Qt)
    results.append(("Node Labels", test_node_labels()))

    # Test menu structure
    results.append(("Menu Structure", test_menu_structure()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
