# PySide6 Checkbox Layout Techniques and Patterns

This document covers various layout techniques for organizing checkboxes in PySide6 applications, based on patterns found in the repository examples.

## Table of Contents

1. [Horizontal Checkbox Arrangements](#horizontal-checkbox-arrangements)
2. [Grid-Based Checkbox Layouts](#grid-based-checkbox-layouts)
3. [Grouped Checkbox Layouts](#grouped-checkbox-layouts)
4. [Dynamic Checkbox Generation](#dynamic-checkbox-generation)
5. [Responsive Checkbox Layouts](#responsive-checkbox-layouts)

## Horizontal Checkbox Arrangements

### Basic Horizontal Layout

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                               QCheckBox, QLabel, QGroupBox, QSpacerItem, QSizePolicy)
import sys

class HorizontalCheckboxExample(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Example 1: Simple horizontal arrangement
        group1 = QGroupBox("Basic Options")
        layout1 = QHBoxLayout(group1)
        
        layout1.addWidget(QLabel("Enable:"))
        layout1.addWidget(QCheckBox("Feature A"))
        layout1.addWidget(QCheckBox("Feature B"))
        layout1.addWidget(QCheckBox("Feature C"))
        layout1.addStretch()  # Push everything to the left
        
        # Example 2: Mixed types with spacing
        group2 = QGroupBox("Mixed Checkbox Types")
        layout2 = QHBoxLayout(group2)
        
        binary_cb = QCheckBox("Binary")
        tristate_cb = QCheckBox("Tri-state")
        tristate_cb.setTristate(True)
        tristate_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        
        layout2.addWidget(QLabel("Options:"))
        layout2.addSpacing(10)
        layout2.addWidget(binary_cb)
        layout2.addSpacing(20)
        layout2.addWidget(tristate_cb)
        layout2.addStretch()
        
        # Example 3: Evenly distributed
        group3 = QGroupBox("Evenly Distributed")
        layout3 = QHBoxLayout(group3)
        
        checkboxes = [QCheckBox(f"Option {i+1}") for i in range(4)]
        for cb in checkboxes:
            layout3.addWidget(cb)
            layout3.addStretch()  # Equal spacing between items
        
        main_layout.addWidget(group1)
        main_layout.addWidget(group2)
        main_layout.addWidget(group3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HorizontalCheckboxExample()
    window.show()
    sys.exit(app.exec())
```

### Compact Horizontal Layout with Labels

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                               QCheckBox, QLabel, QFrame)
import sys

class CompactHorizontalLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Create multiple rows of horizontal checkboxes
        data = [
            ("File Operations", ["Read", "Write", "Execute", "Delete"]),
            ("Display Options", ["Show Hidden", "Show System", "Show Extensions"]),
            ("Network Settings", ["Auto-connect", "Use Proxy", "Enable SSL", "Cache Data"])
        ]
        
        for title, options in data:
            # Create a frame for each row
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel)
            frame_layout = QHBoxLayout(frame)
            
            # Add title label
            title_label = QLabel(f"{title}:")
            title_label.setMinimumWidth(120)
            title_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            frame_layout.addWidget(title_label)
            
            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.VLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            frame_layout.addWidget(separator)
            
            # Add checkboxes
            for option in options:
                cb = QCheckBox(option)
                cb.stateChanged.connect(lambda state, t=title, o=option: 
                                      print(f"{t} - {o}: {'Checked' if state else 'Unchecked'}"))
                frame_layout.addWidget(cb)
            
            frame_layout.addStretch()
            main_layout.addWidget(frame)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompactHorizontalLayout()
    window.show()
    sys.exit(app.exec())
```

## Grid-Based Checkbox Layouts

### Structured Grid Layout

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                               QCheckBox, QLabel, QGroupBox, QButtonGroup)
import sys

class GridCheckboxLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Example 1: Permission matrix
        permissions_group = QGroupBox("File Permissions Matrix")
        grid_layout = QGridLayout(permissions_group)
        
        # Headers
        grid_layout.addWidget(QLabel(""), 0, 0)  # Empty corner
        grid_layout.addWidget(QLabel("Read"), 0, 1)
        grid_layout.addWidget(QLabel("Write"), 0, 2)
        grid_layout.addWidget(QLabel("Execute"), 0, 3)
        
        # Row headers and checkboxes
        users = ["Owner", "Group", "Others"]
        self.permission_checkboxes = {}
        
        for row, user in enumerate(users, 1):
            grid_layout.addWidget(QLabel(user), row, 0)
            
            for col, permission in enumerate(["read", "write", "execute"], 1):
                cb = QCheckBox()
                cb.stateChanged.connect(lambda state, u=user, p=permission: 
                                      self.on_permission_changed(u, p, state))
                grid_layout.addWidget(cb, row, col)
                self.permission_checkboxes[f"{user}_{permission}"] = cb
        
        # Example 2: Feature matrix
        features_group = QGroupBox("Feature Selection Grid")
        features_layout = QGridLayout(features_group)
        
        categories = ["Basic", "Advanced", "Professional"]
        features = ["Export", "Import", "Sync", "Backup"]
        
        # Headers
        for col, feature in enumerate(features, 1):
            features_layout.addWidget(QLabel(feature), 0, col)
            
        for row, category in enumerate(categories, 1):
            features_layout.addWidget(QLabel(category), row, 0)
            
            for col, feature in enumerate(features, 1):
                cb = QCheckBox()
                cb.setToolTip(f"{category} {feature}")
                features_layout.addWidget(cb, row, col)
        
        main_layout.addWidget(permissions_group)
        main_layout.addWidget(features_group)
        
    def on_permission_changed(self, user, permission, state):
        status = "granted" if state else "denied"
        print(f"{user} {permission} permission {status}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GridCheckboxLayout()
    window.show()
    sys.exit(app.exec())
```

### Responsive Grid Layout

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout,
                               QCheckBox, QLabel, QScrollArea)
import sys

class ResponsiveGridLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Create scrollable area for large grids
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Generate a large grid of checkboxes
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        
        # Create a 10x10 grid of checkboxes
        self.checkboxes = []
        for row in range(10):
            checkbox_row = []
            for col in range(10):
                cb = QCheckBox(f"({row},{col})")
                cb.stateChanged.connect(lambda state, r=row, c=col: 
                                      self.on_checkbox_changed(r, c, state))
                grid_layout.addWidget(cb, row, col)
                checkbox_row.append(cb)
            self.checkboxes.append(checkbox_row)
        
        # Add control buttons
        controls_layout = QGridLayout()
        
        select_all_btn = QCheckBox("Select All")
        select_all_btn.stateChanged.connect(self.select_all_changed)
        controls_layout.addWidget(select_all_btn, 0, 0)
        
        select_row_btn = QCheckBox("Select Row 0")
        select_row_btn.stateChanged.connect(lambda state: self.select_row(0, state))
        controls_layout.addWidget(select_row_btn, 0, 1)
        
        select_col_btn = QCheckBox("Select Column 0")
        select_col_btn.stateChanged.connect(lambda state: self.select_column(0, state))
        controls_layout.addWidget(select_col_btn, 0, 2)
        
        scroll_layout.addLayout(controls_layout)
        scroll_layout.addWidget(grid_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        
        main_layout.addWidget(QLabel("Responsive Grid Layout (10x10)"))
        main_layout.addWidget(scroll_area)
        
    def on_checkbox_changed(self, row, col, state):
        if state:
            print(f"Checkbox ({row},{col}) checked")
            
    def select_all_changed(self, state):
        checked = state == Qt.CheckState.Checked
        for row in self.checkboxes:
            for cb in row:
                cb.setChecked(checked)
                
    def select_row(self, row_index, state):
        checked = state == Qt.CheckState.Checked
        if 0 <= row_index < len(self.checkboxes):
            for cb in self.checkboxes[row_index]:
                cb.setChecked(checked)
                
    def select_column(self, col_index, state):
        checked = state == Qt.CheckState.Checked
        for row in self.checkboxes:
            if 0 <= col_index < len(row):
                row[col_index].setChecked(checked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ResponsiveGridLayout()
    window.show()
    sys.exit(app.exec())
```

## Grouped Checkbox Layouts

### Hierarchical Checkbox Groups

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QCheckBox, QLabel, QGroupBox, QTreeWidget, 
                               QTreeWidgetItem, QFrame)
import sys

class HierarchicalCheckboxLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Example 1: Nested group boxes
        main_group = QGroupBox("Application Settings")
        main_group_layout = QVBoxLayout(main_group)
        
        # UI Settings subgroup
        ui_group = QGroupBox("User Interface")
        ui_layout = QVBoxLayout(ui_group)
        
        ui_checkboxes = [
            QCheckBox("Show toolbar"),
            QCheckBox("Show status bar"),
            QCheckBox("Show line numbers"),
            QCheckBox("Enable syntax highlighting")
        ]
        
        for cb in ui_checkboxes:
            ui_layout.addWidget(cb)
            
        # Performance Settings subgroup
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        perf_checkboxes = [
            QCheckBox("Enable caching"),
            QCheckBox("Preload files"),
            QCheckBox("Background processing"),
            QCheckBox("Auto-save")
        ]
        
        for cb in perf_checkboxes:
            perf_layout.addWidget(cb)
            
        main_group_layout.addWidget(ui_group)
        main_group_layout.addWidget(perf_group)
        
        # Example 2: Tree-style layout with indentation
        tree_group = QGroupBox("Feature Tree")
        tree_layout = QVBoxLayout(tree_group)
        
        # Parent checkbox
        parent_cb = QCheckBox("Enable All Features")
        parent_cb.stateChanged.connect(self.parent_checkbox_changed)
        tree_layout.addWidget(parent_cb)
        
        # Child checkboxes with indentation
        self.child_checkboxes = []
        child_features = [
            "Advanced Search",
            "Export Functions", 
            "Import Functions",
            "Batch Processing"
        ]
        
        for feature in child_features:
            # Create indented layout
            child_layout = QHBoxLayout()
            child_layout.addSpacing(30)  # Indentation
            
            cb = QCheckBox(feature)
            cb.stateChanged.connect(self.child_checkbox_changed)
            self.child_checkboxes.append(cb)
            
            child_layout.addWidget(cb)
            child_layout.addStretch()
            
            tree_layout.addLayout(child_layout)
            
        self.parent_checkbox = parent_cb
        
        main_layout.addWidget(main_group)
        main_layout.addWidget(tree_group)
        
    def parent_checkbox_changed(self, state):
        checked = state == Qt.CheckState.Checked
        for cb in self.child_checkboxes:
            cb.setChecked(checked)
            
    def child_checkbox_changed(self, state):
        # Update parent checkbox based on children
        checked_count = sum(1 for cb in self.child_checkboxes if cb.isChecked())
        total_count = len(self.child_checkboxes)
        
        if checked_count == 0:
            self.parent_checkbox.setCheckState(Qt.CheckState.Unchecked)
        elif checked_count == total_count:
            self.parent_checkbox.setCheckState(Qt.CheckState.Checked)
        else:
            self.parent_checkbox.setTristate(True)
            self.parent_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HierarchicalCheckboxLayout()
    window.show()
    sys.exit(app.exec())
```

## Dynamic Checkbox Generation

### Dynamic Layout Based on Data

```python
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QCheckBox, QLabel, QPushButton, QLineEdit, 
                               QGroupBox, QScrollArea)
import sys

class DynamicCheckboxLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Controls for adding new checkboxes
        controls_group = QGroupBox("Dynamic Controls")
        controls_layout = QHBoxLayout(controls_group)
        
        self.new_item_edit = QLineEdit()
        self.new_item_edit.setPlaceholderText("Enter new item name")
        
        add_button = QPushButton("Add Checkbox")
        add_button.clicked.connect(self.add_checkbox)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_all)
        
        controls_layout.addWidget(QLabel("New item:"))
        controls_layout.addWidget(self.new_item_edit)
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(clear_button)
        
        # Scrollable area for dynamic checkboxes
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        # Status display
        self.status_label = QLabel("No items added yet")
        
        main_layout.addWidget(controls_group)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(self.status_label)
        
        self.checkboxes = []
        
        # Add some initial items
        initial_items = ["Item 1", "Item 2", "Item 3"]
        for item in initial_items:
            self._create_checkbox(item)
            
    def add_checkbox(self):
        text = self.new_item_edit.text().strip()
        if text:
            self._create_checkbox(text)
            self.new_item_edit.clear()
            self.update_status()
            
    def _create_checkbox(self, text):
        # Create a frame for each checkbox with remove button
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame_layout = QHBoxLayout(frame)
        
        checkbox = QCheckBox(text)
        checkbox.stateChanged.connect(self.update_status)
        
        remove_button = QPushButton("×")
        remove_button.setMaximumWidth(30)
        remove_button.clicked.connect(lambda: self.remove_checkbox(frame, checkbox))
        
        frame_layout.addWidget(checkbox)
        frame_layout.addStretch()
        frame_layout.addWidget(remove_button)
        
        self.scroll_layout.addWidget(frame)
        self.checkboxes.append((frame, checkbox))
        
    def remove_checkbox(self, frame, checkbox):
        # Remove from layout and list
        self.scroll_layout.removeWidget(frame)
        frame.deleteLater()
        
        # Remove from tracking list
        self.checkboxes = [(f, cb) for f, cb in self.checkboxes if cb != checkbox]
        self.update_status()
        
    def clear_all(self):
        # Remove all checkboxes
        for frame, checkbox in self.checkboxes:
            self.scroll_layout.removeWidget(frame)
            frame.deleteLater()
            
        self.checkboxes.clear()
        self.update_status()
        
    def update_status(self):
        total = len(self.checkboxes)
        checked = sum(1 for _, cb in self.checkboxes if cb.isChecked())
        self.status_label.setText(f"Total items: {total}, Checked: {checked}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DynamicCheckboxLayout()
    window.show()
    sys.exit(app.exec())
```

## Responsive Checkbox Layouts

### Flow Layout for Checkboxes

```python
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QCheckBox, 
                               QLabel, QLayout, QLayoutItem, QWidgetItem)
import sys

class FlowLayout(QLayout):
    """A layout that arranges widgets in a flowing manner, wrapping to new lines as needed."""
    
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self.item_list:
            wid = item.widget()
            space_x = self.spacing() + wid.style().layoutSpacing(
                wid.sizePolicy().controlType(),
                wid.sizePolicy().controlType(),
                Qt.Orientation.Horizontal
            )
            space_y = self.spacing() + wid.style().layoutSpacing(
                wid.sizePolicy().controlType(),
                wid.sizePolicy().controlType(),
                Qt.Orientation.Vertical
            )

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

class ResponsiveCheckboxLayout(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(QLabel("Responsive Flow Layout - Resize window to see wrapping"))
        
        # Create flow layout widget
        flow_widget = QWidget()
        flow_layout = FlowLayout(flow_widget)
        
        # Add many checkboxes that will wrap based on window size
        checkbox_texts = [
            "Short", "Medium Length", "Very Long Checkbox Text", "A", "Another One",
            "Feature Alpha", "Feature Beta", "Feature Gamma", "Quick", "Settings",
            "Advanced Options", "Basic", "Professional", "Enterprise", "Custom",
            "Import", "Export", "Sync", "Backup", "Restore", "Configure", "Setup"
        ]
        
        for text in checkbox_texts:
            cb = QCheckBox(text)
            cb.stateChanged.connect(lambda state, t=text: print(f"{t}: {'Checked' if state else 'Unchecked'}"))
            flow_layout.addWidget(cb)
        
        main_layout.addWidget(flow_widget)
        main_layout.addStretch()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ResponsiveCheckboxLayout()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
```

These layout techniques provide:

1. **Horizontal Arrangements**: Various ways to place checkboxes side by side
2. **Grid Layouts**: Structured arrangements for complex checkbox matrices
3. **Grouped Layouts**: Hierarchical organization with parent-child relationships
4. **Dynamic Generation**: Runtime creation and management of checkboxes
5. **Responsive Layouts**: Adaptive arrangements that respond to window resizing

Each technique can be combined and customized for specific application needs.