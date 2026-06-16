from aicodeprep_gui.pro.flow.nodes.io_nodes import FileWriteNode


def test_file_write_node_skips_empty_input_without_truncating_existing_file(tmp_path):
    target = tmp_path / "best_of_n.txt"
    target.write_text("keep existing output", encoding="utf-8")

    node = FileWriteNode()
    node.set_property("path", str(target))

    result = node.run({})

    assert result == {}
    assert target.read_text(encoding="utf-8") == "keep existing output"
