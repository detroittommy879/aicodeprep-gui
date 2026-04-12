from aicodeprep_gui.gui.components.tree_widget import FileTreeManager
import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PySide6 import QtWidgets, QtCore

# Ensure QApplication exists
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)


class TestCheckFilesByPaths(unittest.TestCase):
    def setUp(self):
        """Set up a mock main_window with a real QTreeWidget."""
        self.main_window = MagicMock()
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setColumnCount(2)
        self.main_window.tree_widget = self.tree_widget
        self.main_window.path_to_item = {}
        self.main_window.level_delegate = None
        self.main_window.update_token_counter = MagicMock()
        self.main_window.is_pro_level_column_enabled = MagicMock(
            return_value=False)

        # Populate tree with some items
        self._add_file("src/main.py")
        self._add_file("src/utils/helpers.py")
        self._add_file("tests/test_main.py")
        self._add_file("README.md")
        self._add_file("setup.py")

        self.manager = FileTreeManager(self.main_window)

    def _add_file(self, rel_path):
        """Add a file item to the tree widget."""
        parts = rel_path.split("/")
        parent = self.tree_widget.invisibleRootItem()
        path_so_far = ""
        for part in parts[:-1]:
            path_so_far = f"{path_so_far}/{part}" if path_so_far else part
            # Normalize to os.sep for path_to_item keys
            norm_path = path_so_far.replace("/", os.sep)
            if norm_path not in self.main_window.path_to_item:
                item = QtWidgets.QTreeWidgetItem(parent, [part, ""])
                item.setData(0, QtCore.Qt.UserRole,
                             os.path.join(os.getcwd(), norm_path))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(0, QtCore.Qt.Unchecked)
                self.main_window.path_to_item[norm_path] = item
                parent = item
            else:
                parent = self.main_window.path_to_item[norm_path]

        # Add file
        norm_rel = rel_path.replace("/", os.sep)
        item = QtWidgets.QTreeWidgetItem(parent, [parts[-1], ""])
        item.setData(0, QtCore.Qt.UserRole,
                     os.path.join(os.getcwd(), norm_rel))
        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
        item.setCheckState(0, QtCore.Qt.Unchecked)
        self.main_window.path_to_item[norm_rel] = item

    def test_check_files_by_paths_selects_correct_files(self):
        self.manager.check_files_by_paths(["src/main.py", "README.md"])

        src_main = self.main_window.path_to_item["src/main.py".replace(
            "/", os.sep)]
        readme = self.main_window.path_to_item["README.md".replace(
            "/", os.sep)]
        setup = self.main_window.path_to_item["setup.py".replace("/", os.sep)]

        self.assertEqual(src_main.checkState(0), QtCore.Qt.Checked)
        self.assertEqual(readme.checkState(0), QtCore.Qt.Checked)
        self.assertEqual(setup.checkState(0), QtCore.Qt.Unchecked)

    def test_check_files_by_paths_deselects_others(self):
        # First check all
        for item in self.main_window.path_to_item.values():
            item.setCheckState(0, QtCore.Qt.Checked)

        self.manager.check_files_by_paths(["README.md"])

        readme = self.main_window.path_to_item["README.md".replace(
            "/", os.sep)]
        setup = self.main_window.path_to_item["setup.py".replace("/", os.sep)]

        self.assertEqual(readme.checkState(0), QtCore.Qt.Checked)
        self.assertEqual(setup.checkState(0), QtCore.Qt.Unchecked)

    def test_check_files_by_paths_handles_forward_slashes(self):
        # Force a platform-specific path in the map
        rel_path = "src/utils/helpers.py".replace("/", os.sep)
        self.manager.check_files_by_paths(["src/utils/helpers.py"])

        item = self.main_window.path_to_item[rel_path]
        self.assertEqual(item.checkState(0), QtCore.Qt.Checked)

    def test_check_files_by_paths_empty_list(self):
        # Check some first
        self.main_window.path_to_item["README.md".replace(
            "/", os.sep)].setCheckState(0, QtCore.Qt.Checked)

        self.manager.check_files_by_paths([])

        for item in self.main_window.path_to_item.values():
            self.assertEqual(item.checkState(0), QtCore.Qt.Unchecked)

    def test_check_files_by_paths_nonexistent_path(self):
        # Should not crash
        self.manager.check_files_by_paths(["non/existent/path.py"])

        # Verify nothing is checked
        for item in self.main_window.path_to_item.values():
            self.assertEqual(item.checkState(0), QtCore.Qt.Unchecked)

    def test_check_files_by_paths_calls_update_token_counter(self):
        self.manager.check_files_by_paths(["README.md"])
        self.main_window.update_token_counter.assert_called()

    def test_check_files_by_paths_lazy_loads_parents(self):
        # Remove a file from path_to_item but keep its parent
        rel_path = "src/utils/helpers.py".replace("/", os.sep)
        parent_path = "src/utils".replace("/", os.sep)

        # Ensure parent exists
        self.assertIn(parent_path, self.main_window.path_to_item)

        # Remove the child from our manual map to simulate it not being loaded yet
        child_item = self.main_window.path_to_item.pop(rel_path)

        # Mock on_item_expanded to re-add the child
        def mock_expand(item):
            if item == self.main_window.path_to_item[parent_path]:
                self.main_window.path_to_item[rel_path] = child_item

        self.manager.on_item_expanded = MagicMock(side_effect=mock_expand)

        # Call check_files_by_paths
        self.manager.check_files_by_paths(["src/utils/helpers.py"])

        # Verify on_item_expanded was called for parents
        self.manager.on_item_expanded.assert_called()
        # Verify item is now checked
        self.assertEqual(child_item.checkState(0), QtCore.Qt.Checked)
