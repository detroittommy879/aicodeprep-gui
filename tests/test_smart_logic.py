import os
import types

from PySide6 import QtWidgets, QtGui, QtCore

from aicodeprep_gui import smart_logic
from aicodeprep_gui import gui as gui_module
from aicodeprep_gui.gui.components.tree_widget import DIRECTORY_LOADED_ROLE, FileTreeManager


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


def test_collect_seed_paths_uses_top_level_entries_and_saved_files(tmp_path):
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (root / "src" / "helper.py").write_text("print('helper')\n", encoding="utf-8")
    (root / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")

    files = smart_logic.collect_seed_paths(
        str(root), {os.path.join("src", "main.py")})
    rel_paths = {rel_path: is_checked for _, rel_path, is_checked in files}

    assert "src" in rel_paths
    assert "docs" in rel_paths
    assert os.path.join("src", "main.py") in rel_paths
    assert rel_paths[os.path.join("src", "main.py")] is True
    assert os.path.join("src", "helper.py") not in rel_paths
    assert os.path.join("docs", "guide.md") not in rel_paths


def test_sparse_tree_expansion_merges_missing_children(tmp_path, qapp_session):
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    (root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (root / "src" / "helper.py").write_text("print('helper')\n", encoding="utf-8")

    tree_widget = QtWidgets.QTreeWidget()
    tree_widget.setColumnCount(2)

    main_window = types.SimpleNamespace(
        tree_widget=tree_widget,
        path_to_item={},
        preferences_manager=types.SimpleNamespace(
            prefs_loaded=True,
            checked_files_from_prefs={os.path.join("src", "main.py")},
        ),
        folder_icon=QtGui.QIcon(),
        file_icon=QtGui.QIcon(),
        project_root=str(root),
        level_delegate=None,
        is_pro_level_column_enabled=lambda: False,
    )

    manager = FileTreeManager(main_window)
    manager.populate_tree(
        smart_logic.collect_seed_paths(
            str(root), {os.path.join("src", "main.py")}),
        fully_loaded=False,
    )

    src_item = main_window.path_to_item["src"]
    assert src_item.data(0, DIRECTORY_LOADED_ROLE) is False
    assert src_item.childIndicatorPolicy() == QtWidgets.QTreeWidgetItem.ShowIndicator

    manager.on_item_expanded(src_item)

    assert src_item.data(0, DIRECTORY_LOADED_ROLE) is True
    assert src_item.childIndicatorPolicy(
    ) == QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless
    assert os.path.join("src", "helper.py") in main_window.path_to_item
    assert src_item.checkState(0) == QtCore.Qt.PartiallyChecked
    assert main_window.path_to_item[os.path.join("src", "main.py")].checkState(
        0) == QtCore.Qt.Checked


def test_sparse_tree_top_level_directory_remains_expandable(tmp_path, qapp_session):
    root = tmp_path / "project"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "guide.md").write_text("# guide\n", encoding="utf-8")

    tree_widget = QtWidgets.QTreeWidget()
    tree_widget.setColumnCount(2)

    main_window = types.SimpleNamespace(
        tree_widget=tree_widget,
        path_to_item={},
        preferences_manager=types.SimpleNamespace(
            prefs_loaded=True,
            checked_files_from_prefs=set(),
        ),
        folder_icon=QtGui.QIcon(),
        file_icon=QtGui.QIcon(),
        project_root=str(root),
        level_delegate=None,
        is_pro_level_column_enabled=lambda: False,
    )

    manager = FileTreeManager(main_window)
    manager.populate_tree(
        smart_logic.collect_seed_paths(str(root), set()),
        fully_loaded=False,
    )

    docs_item = main_window.path_to_item["docs"]
    assert docs_item.childCount() == 0
    assert docs_item.data(0, DIRECTORY_LOADED_ROLE) is False
    assert docs_item.childIndicatorPolicy() == QtWidgets.QTreeWidgetItem.ShowIndicator

    manager.on_item_expanded(docs_item)

    assert docs_item.data(0, DIRECTORY_LOADED_ROLE) is True
    assert os.path.join("docs", "guide.md") in main_window.path_to_item


def test_show_file_selection_gui_forwards_sparse_startup_flag(monkeypatch):
    calls = {}

    class DummyGui:
        def __init__(self, files, project_root=None, initial_tree_fully_loaded=True):
            calls["files"] = files
            calls["project_root"] = project_root
            calls["initial_tree_fully_loaded"] = initial_tree_fully_loaded
            self.action = 'quit'

        def show(self):
            calls["show_called"] = True

        def get_selected_files(self):
            return []

    class DummyApp:
        def exec(self):
            calls["exec_called"] = True

    monkeypatch.setattr(gui_module, "FileSelectionGUI", DummyGui)
    monkeypatch.setattr(
        gui_module.QtWidgets.QApplication,
        "instance",
        staticmethod(lambda: DummyApp()),
    )

    action, selected = gui_module.show_file_selection_gui(
        [("/tmp/project/app.py", "app.py", True)],
        project_root="/tmp/project",
        initial_tree_fully_loaded=False,
    )

    assert action == 'quit'
    assert selected == []
    assert calls["project_root"] == "/tmp/project"
    assert calls["initial_tree_fully_loaded"] is False
    assert calls["show_called"] is True
    assert calls["exec_called"] is True


def test_sparse_tree_auto_expand_reveals_saved_selection(tmp_path, qapp_session):
    root = tmp_path / "project"
    (root / "src" / "nested").mkdir(parents=True)
    (root / "src" / "nested" /
     "chosen.py").write_text("print('chosen')\n", encoding="utf-8")
    (root / "src" / "nested" / "other.py").write_text("print('other')\n", encoding="utf-8")

    tree_widget = QtWidgets.QTreeWidget()
    tree_widget.setColumnCount(2)

    main_window = types.SimpleNamespace(
        tree_widget=tree_widget,
        path_to_item={},
        preferences_manager=types.SimpleNamespace(
            prefs_loaded=True,
            checked_files_from_prefs={
                os.path.join("src", "nested", "chosen.py")},
        ),
        folder_icon=QtGui.QIcon(),
        file_icon=QtGui.QIcon(),
        project_root=str(root),
        level_delegate=None,
        is_pro_level_column_enabled=lambda: False,
        update_token_counter=lambda: None,
    )

    manager = FileTreeManager(main_window)
    tree_widget.itemExpanded.connect(manager.on_item_expanded)
    manager.populate_tree(
        smart_logic.collect_seed_paths(
            str(root), {os.path.join("src", "nested", "chosen.py")}),
        fully_loaded=False,
    )

    chosen_path = os.path.join("src", "nested", "chosen.py")
    src_item = main_window.path_to_item["src"]
    nested_item = main_window.path_to_item[os.path.join("src", "nested")]

    assert main_window.path_to_item[chosen_path].checkState(
        0) == QtCore.Qt.Checked
    assert src_item.checkState(0) == QtCore.Qt.PartiallyChecked
    assert nested_item.checkState(0) == QtCore.Qt.PartiallyChecked

    manager._expand_folders_for_paths({chosen_path})

    assert src_item.isExpanded() is True
    assert nested_item.isExpanded() is True
    assert os.path.join(
        "src", "nested", "other.py") in main_window.path_to_item
    assert src_item.checkState(0) == QtCore.Qt.PartiallyChecked
    assert nested_item.checkState(0) == QtCore.Qt.PartiallyChecked
    assert main_window.path_to_item[chosen_path].checkState(
        0) == QtCore.Qt.Checked
