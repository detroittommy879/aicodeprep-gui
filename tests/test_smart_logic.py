import os
import types

from PySide6 import QtWidgets, QtGui, QtCore

from aicodeprep_gui import smart_logic
from aicodeprep_gui.gui.components.tree_widget import FileTreeManager


def test_collect_all_files_refreshes_project_config(tmp_path):
    project_one = tmp_path / "project_one"
    project_two = tmp_path / "project_two"

    (project_one / "nested").mkdir(parents=True)
    (project_two / "nested").mkdir(parents=True)

    (project_one / "nested" / "keep.py").write_text("print('one')\n", encoding="utf-8")
    (project_two / "nested" / "skip.py").write_text("print('two')\n", encoding="utf-8")
    (project_two / "root.py").write_text("print('root')\n", encoding="utf-8")
    (project_two / "aicodeprep-gui.toml").write_text(
        "exclude_patterns = [\n  \"nested/\",\n]\n",
        encoding="utf-8",
    )

    files_one = smart_logic.collect_all_files(str(project_one))
    rel_paths_one = {rel_path for _, rel_path, _ in files_one}
    assert "nested" in rel_paths_one
    assert os.path.join("nested", "keep.py") in rel_paths_one

    files_two = smart_logic.collect_all_files(str(project_two))
    rel_paths_two = {rel_path for _, rel_path, _ in files_two}
    assert "root.py" in rel_paths_two
    assert "nested" not in rel_paths_two
    assert os.path.join("nested", "skip.py") not in rel_paths_two
    assert smart_logic.exclude_spec.match_file("nested/")


def test_populate_tree_blocks_item_changed_signals(tmp_path, qapp_session):
    root = tmp_path / "project"
    root.mkdir()
    file_path = root / "app.py"
    file_path.write_text("print('hello')\n", encoding="utf-8")

    tree_widget = QtWidgets.QTreeWidget()
    tree_widget.setColumnCount(2)

    main_window = types.SimpleNamespace(
        tree_widget=tree_widget,
        path_to_item={},
        preferences_manager=types.SimpleNamespace(
            prefs_loaded=False,
            checked_files_from_prefs=set(),
        ),
        folder_icon=QtGui.QIcon(),
        file_icon=QtGui.QIcon(),
    )

    manager = FileTreeManager(main_window)
    changed_items = []
    tree_widget.itemChanged.connect(
        lambda item, column: changed_items.append((item.text(0), column)))

    manager.populate_tree([(str(file_path), "app.py", True)])

    assert changed_items == []
    assert "app.py" in main_window.path_to_item
    assert main_window.path_to_item["app.py"].checkState(
        0) == QtCore.Qt.Checked
