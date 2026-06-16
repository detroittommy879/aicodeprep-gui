import os
import logging
from typing import List
from PySide6 import QtWidgets, QtCore, QtGui
from aicodeprep_gui import smart_logic
# LEVEL_ROLE is provided dynamically from main_window when Pro Level column is installed


DIRECTORY_LOADED_ROLE = QtCore.Qt.UserRole + 1


class FileTreeManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def _project_root(self):
        return getattr(self.main_window, 'project_root', os.getcwd())

    def _safe_relative_path(self, abs_path):
        if not abs_path:
            return None
        try:
            return os.path.relpath(abs_path, self._project_root())
        except (OSError, ValueError) as exc:
            logging.warning(
                "Skipping tree item with path outside current project root: %s (%s)",
                abs_path,
                exc,
            )
            return None

    def _set_directory_loading_state(self, item, fully_loaded):
        item.setData(0, DIRECTORY_LOADED_ROLE, fully_loaded)
        if fully_loaded:
            item.setChildIndicatorPolicy(
                QtWidgets.QTreeWidgetItem.DontShowIndicatorWhenChildless)
        else:
            item.setChildIndicatorPolicy(
                QtWidgets.QTreeWidgetItem.ShowIndicator)

    def _update_parent_states_from_checked_items(self):
        def update_parents(child_item):
            parent = child_item.parent()
            while parent:
                all_children_checked = True
                all_children_unchecked = True
                has_checkable_children = False
                for index in range(parent.childCount()):
                    child = parent.child(index)
                    if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                        has_checkable_children = True
                        if child.checkState(0) == QtCore.Qt.Checked:
                            all_children_unchecked = False
                        elif child.checkState(0) == QtCore.Qt.Unchecked:
                            all_children_checked = False
                        else:
                            all_children_checked = False
                            all_children_unchecked = False
                if has_checkable_children:
                    if all_children_checked and not parent.data(0, DIRECTORY_LOADED_ROLE):
                        parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
                    elif all_children_checked:
                        parent.setCheckState(0, QtCore.Qt.Checked)
                    elif all_children_unchecked:
                        parent.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
                else:
                    parent.setCheckState(0, QtCore.Qt.Unchecked)
                parent = parent.parent()

        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.main_window.tree_widget)
        while iterator.value():
            item = iterator.value()
            abs_path = item.data(0, QtCore.Qt.UserRole)
            if abs_path and os.path.isfile(abs_path) and item.checkState(0) == QtCore.Qt.Checked:
                update_parents(item)
            iterator += 1

    def populate_tree(self, files, fully_loaded=True):
        """Populate the tree widget with the given files list."""
        tree_widget = self.main_window.tree_widget
        tree_widget.blockSignals(True)
        tree_widget.setUpdatesEnabled(False)
        try:
            tree_widget.clear()
            self.main_window.path_to_item = {}
            root_node = tree_widget.invisibleRootItem()
            import os
            from aicodeprep_gui import smart_logic

            for abs_path, rel_path, is_checked in files:
                parts = rel_path.split(os.sep)
                parent_node = root_node
                path_so_far = ""
                for part in parts[:-1]:
                    path_so_far = os.path.join(
                        path_so_far, part) if path_so_far else part
                    if path_so_far in self.main_window.path_to_item:
                        parent_node = self.main_window.path_to_item[path_so_far]
                    else:
                        new_parent = QtWidgets.QTreeWidgetItem(
                            parent_node, [part, ""])
                        new_parent.setIcon(0, self.main_window.folder_icon)
                        new_parent.setFlags(new_parent.flags()
                                            | QtCore.Qt.ItemIsUserCheckable)
                        new_parent.setCheckState(0, QtCore.Qt.Unchecked)
                        self._set_directory_loading_state(
                            new_parent, fully_loaded)
                        self.main_window.path_to_item[path_so_far] = new_parent
                        parent_node = new_parent

                item_text = parts[-1]
                item = QtWidgets.QTreeWidgetItem(parent_node, [item_text, ""])
                item.setData(0, QtCore.Qt.UserRole, abs_path)
                self.main_window.path_to_item[rel_path] = item

                if self.main_window.preferences_manager.prefs_loaded:
                    is_checked = rel_path in self.main_window.preferences_manager.checked_files_from_prefs

                if os.path.isdir(abs_path):
                    item.setIcon(0, self.main_window.folder_icon)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                    self._set_directory_loading_state(item, fully_loaded)
                else:
                    item.setIcon(0, self.main_window.file_icon)
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    if smart_logic.is_binary_file(abs_path):
                        is_checked = False

                item.setCheckState(
                    0, QtCore.Qt.Checked if is_checked else QtCore.Qt.Unchecked)

            self._update_parent_states_from_checked_items()
        finally:
            tree_widget.setUpdatesEnabled(True)
            tree_widget.blockSignals(False)
            tree_widget.viewport().update()

    def on_item_expanded(self, item):
        dir_path = item.data(0, QtCore.Qt.UserRole)
        if not dir_path or not os.path.isdir(dir_path):
            return
        if item.data(0, DIRECTORY_LOADED_ROLE):
            return
        try:
            for name in sorted(os.listdir(dir_path)):
                abs_path = os.path.join(dir_path, name)
                try:
                    rel_path = os.path.relpath(abs_path, self._project_root())
                except ValueError:
                    logging.warning(
                        f"Skipping {abs_path}: not on current drive.")
                    continue
                if rel_path in self.main_window.path_to_item:
                    continue
                # Always create with two columns since tree widget always has two columns
                new_item = QtWidgets.QTreeWidgetItem(item, [name, ""])

                new_item.setData(0, QtCore.Qt.UserRole, abs_path)
                new_item.setFlags(new_item.flags() |
                                  QtCore.Qt.ItemIsUserCheckable |
                                  QtCore.Qt.ItemIsEditable)

                # Initialize Level column state = 0 (for all children) only if Level column is enabled
                if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                        and self.main_window.is_pro_level_column_enabled()):
                    try:
                        new_item.setData(1, self.main_window.level_role, 0)
                        # Also set a visible DisplayRole string so the cell is not blank
                        labels = getattr(
                            self.main_window.level_delegate, "LEVEL_LABELS", None)
                        if labels:
                            new_item.setData(
                                1, QtCore.Qt.DisplayRole, labels[0])

                        # Make sure the item is editable in column 1
                        flags = new_item.flags()
                        new_item.setFlags(flags | QtCore.Qt.ItemIsEditable)
                    except Exception:
                        pass

                self.main_window.path_to_item[rel_path] = new_item
                is_excluded = smart_logic.exclude_spec.match_file(
                    rel_path) or smart_logic.exclude_spec.match_file(rel_path + '/')
                if os.path.isdir(abs_path):
                    new_item.setIcon(0, self.main_window.folder_icon)
                    self._set_directory_loading_state(new_item, False)
                    if is_excluded:
                        new_item.setCheckState(0, QtCore.Qt.Unchecked)
                    else:
                        new_item.setCheckState(0, item.checkState(0))
                else:
                    new_item.setIcon(0, self.main_window.file_icon)
                    if smart_logic.is_binary_file(abs_path):
                        is_excluded = True
                    if is_excluded:
                        new_item.setCheckState(0, QtCore.Qt.Unchecked)
                    elif self.main_window.preferences_manager.prefs_loaded and rel_path in self.main_window.preferences_manager.checked_files_from_prefs:
                        new_item.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        new_item.setCheckState(0, item.checkState(0))
            self._set_directory_loading_state(item, True)
            self._update_parent_states_from_checked_items()
        except OSError as e:
            logging.error(f"Error scanning directory {dir_path}: {e}")
        # After populating children, sync Skeleton Level values for this branch
        if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                and self.main_window.is_pro_level_column_enabled()):
            self._sync_levels_for_subtree(item)

    def handle_item_changed(self, item, column):
        if column == 0:
            self.main_window.tree_widget.blockSignals(True)
            try:
                new_state = item.checkState(0)

                def apply_to_children(parent_item, state):
                    for i in range(parent_item.childCount()):
                        child = parent_item.child(i)
                        if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                            abs_path = child.data(0, QtCore.Qt.UserRole)
                            if state == QtCore.Qt.Checked and abs_path and os.path.isfile(abs_path) and smart_logic.is_binary_file(abs_path):
                                child.setCheckState(0, QtCore.Qt.Unchecked)
                            else:
                                child.setCheckState(0, state)
                            if os.path.isdir(abs_path):
                                apply_to_children(child, state)
                apply_to_children(item, new_state)
                parent = item.parent()
                while parent:
                    all_children_checked = True
                    all_children_unchecked = True
                    has_checkable_children = False
                    for i in range(parent.childCount()):
                        child = parent.child(i)
                        if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                            has_checkable_children = True
                            if child.checkState(0) == QtCore.Qt.Checked:
                                all_children_unchecked = False
                            elif child.checkState(0) == QtCore.Qt.Unchecked:
                                all_children_checked = False
                            else:
                                all_children_checked = False
                                all_children_unchecked = False
                    if has_checkable_children:
                        if all_children_checked:
                            parent.setCheckState(0, QtCore.Qt.Checked)
                        elif all_children_unchecked:
                            parent.setCheckState(0, QtCore.Qt.Unchecked)
                        else:
                            parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
                    else:
                        parent.setCheckState(0, QtCore.Qt.Unchecked)
                    parent = parent.parent()
            finally:
                self.main_window.tree_widget.blockSignals(False)
            if item.checkState(0) == QtCore.Qt.Checked:
                file_path = item.data(0, QtCore.Qt.UserRole)
                if file_path and os.path.isfile(file_path):
                    QtCore.QTimer.singleShot(
                        0, lambda: self.expand_parents_of_item(item))
            # Keep Level column in sync with check states
            if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                    and self.main_window.is_pro_level_column_enabled()):
                self._sync_levels_for_subtree(item)
            self.main_window.update_token_counter()
        elif (column == 1 and hasattr(self.main_window, "level_role") and getattr(self.main_window, "level_delegate", None)
              and self.main_window.is_pro_level_column_enabled()):
            # Skeleton level column changed
            new_level = item.data(1, self.main_window.level_role)
            abs_path = item.data(0, QtCore.Qt.UserRole)
            if abs_path and os.path.isdir(abs_path):
                self._apply_level_to_children(item, new_level)
            self.main_window.update_token_counter()

    def expand_parents_of_item(self, item):
        parent = item.parent()
        while parent is not None:
            self.main_window.tree_widget.expandItem(parent)
            parent = parent.parent()

    def get_selected_files(self):
        selected = []
        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.main_window.tree_widget)
        while iterator.value():
            item = iterator.value()
            file_path = item.data(0, QtCore.Qt.UserRole)
            if file_path and os.path.isfile(file_path) and item.checkState(0) == QtCore.Qt.Checked:
                selected.append(file_path)
            iterator += 1
        return selected

    def sync_levels_to_checks(self):
        """
        Sync Level column for all FILE items to match checkbox state:
        - Unchecked -> 'Paths only' (index 1)
        - Checked   -> 'Full content' (index 3)
        Safely no-ops if Level column is not installed.
        """
        if (not hasattr(self.main_window, "level_role") or not self.main_window.level_delegate
                or not self.main_window.is_pro_level_column_enabled()):
            return
        labels = getattr(self.main_window.level_delegate, "LEVEL_LABELS", None)
        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.main_window.tree_widget)
        while iterator.value():
            item = iterator.value()
            abs_path = item.data(0, QtCore.Qt.UserRole)
            if abs_path and os.path.isfile(abs_path):
                is_checked = item.checkState(0) == QtCore.Qt.Checked
                level_index = 3 if is_checked else 1
                item.setData(1, self.main_window.level_role, level_index)
                if labels and 0 <= level_index < len(labels):
                    item.setData(1, QtCore.Qt.DisplayRole, labels[level_index])
            iterator += 1

    def _sync_levels_for_subtree(self, root_item):
        """
        Sync Level column for a subtree rooted at root_item (files only).
        Used after checkbox changes and lazy-loaded expansion.
        """
        if not hasattr(self.main_window, "level_role") or not self.main_window.level_delegate:
            return
        labels = getattr(self.main_window.level_delegate, "LEVEL_LABELS", None)

        def recurse(item):
            abs_path = item.data(0, QtCore.Qt.UserRole)
            if abs_path and os.path.isfile(abs_path):
                is_checked = item.checkState(0) == QtCore.Qt.Checked
                level_index = 3 if is_checked else 1
                item.setData(1, self.main_window.level_role, level_index)
                if labels and 0 <= level_index < len(labels):
                    item.setData(1, QtCore.Qt.DisplayRole, labels[level_index])
            for i in range(item.childCount()):
                recurse(item.child(i))

        recurse(root_item)

    def select_all(self):
        def check_all(item):
            abs_path = item.data(0, QtCore.Qt.UserRole)
            rel_path = self._safe_relative_path(abs_path)
            is_excluded = bool(abs_path and rel_path is None)
            if rel_path:
                is_excluded = smart_logic.exclude_spec.match_file(
                    rel_path) or smart_logic.exclude_spec.match_file(rel_path + '/')
                if os.path.isfile(abs_path) and smart_logic.is_binary_file(abs_path):
                    is_excluded = True
            if item.flags() & QtCore.Qt.ItemIsUserCheckable and item.flags() & QtCore.Qt.ItemIsEnabled and not is_excluded:
                item.setCheckState(0, QtCore.Qt.Checked)
            else:
                item.setCheckState(0, QtCore.Qt.Unchecked)
            for i in range(item.childCount()):
                if os.path.isdir(abs_path):
                    self.on_item_expanded(item)
                check_all(item.child(i))
        self.main_window.tree_widget.blockSignals(True)
        try:
            for i in range(self.main_window.tree_widget.topLevelItemCount()):
                check_all(self.main_window.tree_widget.topLevelItem(i))
        finally:
            self.main_window.tree_widget.blockSignals(False)
        # Sync Level column across tree after bulk selection
        if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                and self.main_window.is_pro_level_column_enabled()):
            self.sync_levels_to_checks()
        self.main_window.update_token_counter()

    def deselect_all(self):
        iterator = QtWidgets.QTreeWidgetItemIterator(
            self.main_window.tree_widget)
        self.main_window.tree_widget.blockSignals(True)
        try:
            while iterator.value():
                item = iterator.value()
                if item.flags() & QtCore.Qt.ItemIsUserCheckable:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                iterator += 1
        finally:
            self.main_window.tree_widget.blockSignals(False)
        # Sync Level column across tree after bulk deselection
        if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                and self.main_window.is_pro_level_column_enabled()):
            self.sync_levels_to_checks()
        self.main_window.update_token_counter()

    def check_files_by_paths(self, file_paths: List[str]):
        """
        Programmatically deselect all files, then check only the files whose
        relative paths match the provided list. Used by AI Smart Select.

        Args:
            file_paths: List of relative file paths (e.g., ["src/main.py", "tests/test_main.py"])
        """
        self.main_window.tree_widget.blockSignals(True)
        try:
            # 1. Deselect all items
            iterator = QtWidgets.QTreeWidgetItemIterator(
                self.main_window.tree_widget)
            while iterator.value():
                item = iterator.value()
                if item.flags() & QtCore.Qt.ItemIsUserCheckable:
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                iterator += 1

            # 2. Normalize and check specified files
            for rel_path in file_paths:
                # Normalize path
                norm_path = rel_path.replace("/", os.sep).replace("\\", os.sep)
                if norm_path.startswith("." + os.sep):
                    norm_path = norm_path[2:]

                # Try finding the item
                item = self.main_window.path_to_item.get(norm_path)

                if not item:
                    # Try lazy-loading parents
                    parts = norm_path.split(os.sep)
                    current_rel = ""
                    for part in parts[:-1]:
                        current_rel = os.path.join(
                            current_rel, part) if current_rel else part
                        if current_rel in self.main_window.path_to_item:
                            parent_item = self.main_window.path_to_item[current_rel]
                            self.on_item_expanded(parent_item)

                    # Retry after expansion
                    item = self.main_window.path_to_item.get(norm_path)

                if item:
                    item.setCheckState(0, QtCore.Qt.Checked)

            # 3. Update parent folder states
            def update_parents(child_item):
                parent = child_item.parent()
                while parent:
                    all_children_checked = True
                    all_children_unchecked = True
                    has_checkable_children = False
                    for i in range(parent.childCount()):
                        child = parent.child(i)
                        if child.flags() & QtCore.Qt.ItemIsUserCheckable and child.flags() & QtCore.Qt.ItemIsEnabled:
                            has_checkable_children = True
                            if child.checkState(0) == QtCore.Qt.Checked:
                                all_children_unchecked = False
                            elif child.checkState(0) == QtCore.Qt.Unchecked:
                                all_children_checked = False
                            else:
                                all_children_checked = False
                                all_children_unchecked = False
                    if has_checkable_children:
                        if all_children_checked:
                            parent.setCheckState(0, QtCore.Qt.Checked)
                        elif all_children_unchecked:
                            parent.setCheckState(0, QtCore.Qt.Unchecked)
                        else:
                            parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
                    else:
                        parent.setCheckState(0, QtCore.Qt.Unchecked)
                    parent = parent.parent()

            # Update parents for all top-level items recursively (or just iterate all items and if checked, update parents)
            iterator = QtWidgets.QTreeWidgetItemIterator(
                self.main_window.tree_widget)
            while iterator.value():
                item = iterator.value()
                if item.checkState(0) == QtCore.Qt.Checked:
                    update_parents(item)
                iterator += 1

        finally:
            self.main_window.tree_widget.blockSignals(False)

        # Sync Level column if enabled
        if (hasattr(self.main_window, "level_role") and self.main_window.level_delegate
                and self.main_window.is_pro_level_column_enabled()):
            self.sync_levels_to_checks()

        self.main_window.update_token_counter()

    def _expand_folders_for_paths(self, checked_paths):
        folders_to_expand = {}
        for checked_path in checked_paths:
            normalized_path = checked_path.replace(
                "/", os.sep).replace("\\", os.sep)
            path_parts = normalized_path.split(os.sep)
            current_path = ""
            for i, part in enumerate(path_parts):
                if i == 0:
                    current_path = part
                else:
                    current_path = os.path.join(current_path, part)
                if current_path in self.main_window.path_to_item and os.path.isdir(self.main_window.path_to_item[current_path].data(0, QtCore.Qt.UserRole)):
                    folders_to_expand[current_path] = self.main_window.path_to_item[current_path]
        for path, item in sorted(folders_to_expand.items(), key=lambda entry: entry[0].count(os.sep)):
            if not item.data(0, DIRECTORY_LOADED_ROLE):
                self.on_item_expanded(item)
            self.main_window.tree_widget.expandItem(item)

        self._update_parent_states_from_checked_items()

    def _apply_level_to_children(self, parent_item, level_value):
        """
        Recursively applies the specified skeleton level to all descendants of the parent_item.
        This respects the tree hierarchy and correctly handles lazy-loaded subdirectories.
        """
        labels = getattr(self.main_window.level_delegate, "LEVEL_LABELS", None)

        def recurse_and_apply(current_parent):
            # Iterate through the direct children of the current parent item.
            for i in range(current_parent.childCount()):
                child = current_parent.child(i)

                # Apply the new level to the child item
                child.setData(1, self.main_window.level_role, level_value)
                if labels and 0 <= level_value < len(labels):
                    child.setData(1, QtCore.Qt.DisplayRole,
                                  labels[level_value])

                # If the child is a directory, recurse into it
                child_path = child.data(0, QtCore.Qt.UserRole)
                if child_path and os.path.isdir(child_path):
                    # Before recursing, ensure its children are loaded
                    if child.childCount() == 0:
                        self.on_item_expanded(child)
                    recurse_and_apply(child)

        self.main_window.tree_widget.blockSignals(True)
        try:
            recurse_and_apply(parent_item)
        finally:
            self.main_window.tree_widget.blockSignals(False)

        self.main_window.tree_widget.viewport().update()

    def auto_expand_common_folders(self):
        common_folders = ['src', 'lib', 'app', 'components',
                          'utils', 'helpers', 'models', 'views', 'controllers']
        for folder_name in common_folders:
            if folder_name in self.main_window.path_to_item:
                item = self.main_window.path_to_item[folder_name]
                self.main_window.tree_widget.expandItem(item)
