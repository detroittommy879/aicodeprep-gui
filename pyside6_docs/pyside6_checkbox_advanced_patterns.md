# Advanced PySide6 Checkbox Patterns and Techniques

This document covers advanced patterns for checkbox customization, including examples found in the PySide6 repository and custom implementations for complex use cases.

## Table of Contents

1. [DialogOptionsWidget Pattern](#dialogoptionswidget-pattern)
2. [Custom Checkbox Groups with State Management](#custom-checkbox-groups-with-state-management)
3. [Checkbox Integration with Models](#checkbox-integration-with-models)
4. [Custom Styled Checkboxes](#custom-styled-checkboxes)
5. [Interactive Checkbox Widgets](#interactive-checkbox-widgets)

## DialogOptionsWidget Pattern

Based on the `examples/widgets/dialogs/standarddialogs/standarddialogs.py` example, here's a reusable pattern for managing groups of checkboxes that represent option flags:

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QGroupBox, QVBoxLayout, QWidget, QPushButton, QLabel
import sys
from enum import Flag, auto

class FileOptions(Flag):
    NONE = 0
    READ_ONLY = auto()
    HIDDEN = auto()
    SYSTEM = auto()
    ARCHIVE = auto()
    COMPRESSED = auto()

class DialogOptionsWidget(QGroupBox):
    """Widget displaying a number of check boxes representing dialog options."""
    
    def __init__(self, title, zero_value, parent=None):
        super().__init__(title, parent)
        self._zero_value = zero_value
        self._layout = QVBoxLayout(self)
        self._mapping = {}

    def value(self):
        """Returns the combined value of all checked options."""
        result = self._zero_value
        for checkbox, value in self._mapping.items():
            if checkbox.isChecked():
                result |= value
        return result

    def setValue(self, value):
        """Sets checkboxes based on the provided flag value."""
        for checkbox, flag_value in self._mapping.items():
            checkbox.setChecked(bool(value & flag_value))

    def add_checkbox(self, text, value):
        """Adds a checkbox with associated flag value."""
        checkbox = QCheckBox(text)
        self._layout.addWidget(checkbox)
        self._mapping[checkbox] = value
        return checkbox

    def add_tristate_checkbox(self, text, value):
        """Adds a tri-state checkbox with associated flag value."""
        checkbox = QCheckBox(text)
        checkbox.setTristate(True)
        self._layout.addWidget(checkbox)
        self._mapping[checkbox] = value
        return checkbox

class AdvancedOptionsExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # File options group
        self.file_options = DialogOptionsWidget("File Options", FileOptions.NONE)
        self.file_options.add_checkbox("Read Only", FileOptions.READ_ONLY)
        self.file_options.add_checkbox("Hidden", FileOptions.HIDDEN)
        self.file_options.add_checkbox("System", FileOptions.SYSTEM)
        self.file_options.add_checkbox("Archive", FileOptions.ARCHIVE)
        self.file_options.add_checkbox("Compressed", FileOptions.COMPRESSED)
        
        # Permission options (using integers)
        self.permission_options = DialogOptionsWidget("Permissions", 0)
        self.permission_options.add_checkbox("Read (4)", 4)
        self.permission_options.add_checkbox("Write (2)", 2)
        self.permission_options.add_checkbox("Execute (1)", 1)
        
        # Control buttons
        test_button = QPushButton("Test Current Values")
        test_button.clicked.connect(self.test_values)
        
        preset_button = QPushButton("Set Preset (Read Only + Archive)")
        preset_button.clicked.connect(self.set_preset)
        
        self.result_label = QLabel("Current values will appear here")
        
        layout.addWidget(self.file_options)
        layout.addWidget(self.permission_options)
        layout.addWidget(test_button)
        layout.addWidget(preset_button)
        layout.addWidget(self.result_label)
        
    def test_values(self):
        file_value = self.file_options.value()
        perm_value = self.permission_options.value()
        
        file_flags = []
        for flag in FileOptions:
            if flag != FileOptions.NONE and file_value & flag:
                file_flags.append(flag.name)
        
        result_text = f"File Options: {file_flags}\nPermissions: {perm_value} (binary: {bin(perm_value)})"
        self.result_label.setText(result_text)
        
    def set_preset(self):
        preset_value = FileOptions.READ_ONLY | FileOptions.ARCHIVE
        self.file_options.setValue(preset_value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdvancedOptionsExample()
    window.show()
    sys.exit(app.exec())
```

## Custom Checkbox Groups with State Management

Here's a pattern for managing interdependent checkboxes with complex state relationships:

```python
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QLabel
import sys

class CheckboxGroup(QObject):
    """Manages a group of checkboxes with interdependent states."""
    
    stateChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkboxes = {}
        self.dependencies = {}
        self._updating = False
        
    def add_checkbox(self, name, checkbox, dependencies=None):
        """Add a checkbox with optional dependencies."""
        self.checkboxes[name] = checkbox
        if dependencies:
            self.dependencies[name] = dependencies
        checkbox.stateChanged.connect(lambda: self._on_checkbox_changed(name))
        
    def _on_checkbox_changed(self, changed_name):
        if self._updating:
            return
            
        self._updating = True
        
        # Handle dependencies
        if changed_name in self.dependencies:
            checkbox = self.checkboxes[changed_name]
            deps = self.dependencies[changed_name]
            
            if checkbox.isChecked():
                # If this checkbox is checked, check all dependencies
                for dep_name in deps:
                    if dep_name in self.checkboxes:
                        self.checkboxes[dep_name].setChecked(True)
            else:
                # If this checkbox is unchecked, handle reverse dependencies
                for name, dep_list in self.dependencies.items():
                    if changed_name in dep_list and name in self.checkboxes:
                        self.checkboxes[name].setChecked(False)
        
        self._updating = False
        self.stateChanged.emit()
        
    def get_checked_items(self):
        """Returns list of checked checkbox names."""
        return [name for name, cb in self.checkboxes.items() if cb.isChecked()]

class DependentCheckboxExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Create checkbox group
        group_box = QGroupBox("Software Features (with dependencies)")
        group_layout = QVBoxLayout(group_box)
        
        # Create checkboxes
        basic_cb = QCheckBox("Basic Features")
        advanced_cb = QCheckBox("Advanced Features")
        pro_cb = QCheckBox("Professional Features")
        enterprise_cb = QCheckBox("Enterprise Features")
        
        # Add to layout
        group_layout.addWidget(basic_cb)
        group_layout.addWidget(advanced_cb)
        group_layout.addWidget(pro_cb)
        group_layout.addWidget(enterprise_cb)
        
        # Set up dependency management
        self.checkbox_group = CheckboxGroup()
        self.checkbox_group.add_checkbox("basic", basic_cb)
        self.checkbox_group.add_checkbox("advanced", advanced_cb, ["basic"])
        self.checkbox_group.add_checkbox("pro", pro_cb, ["basic", "advanced"])
        self.checkbox_group.add_checkbox("enterprise", enterprise_cb, ["basic", "advanced", "pro"])
        
        self.checkbox_group.stateChanged.connect(self.update_status)
        
        self.status_label = QLabel("Select features above")
        
        layout.addWidget(group_box)
        layout.addWidget(self.status_label)
        
    def update_status(self):
        checked = self.checkbox_group.get_checked_items()
        self.status_label.setText(f"Selected: {', '.join(checked) if checked else 'None'}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DependentCheckboxExample()
    window.show()
    sys.exit(app.exec())
```

## Checkbox Integration with Models

Based on the model/view examples in the repository, here's how to integrate checkboxes with Qt's model/view framework:

```python
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QPushButton
import sys

class CheckboxTableModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Name", "Enabled", "Priority", "Tri-State"]
        
    def rowCount(self, parent=QModelIndex()):
        return len(self._data)
        
    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)
        
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._headers[section]
        return None
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
            
        row, col = index.row(), index.column()
        item = self._data[row]
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # Name
                return item["name"]
            elif col == 2:  # Priority
                return str(item["priority"])
        elif role == Qt.ItemDataRole.CheckStateRole:
            if col == 1:  # Enabled (binary checkbox)
                return Qt.CheckState.Checked if item["enabled"] else Qt.CheckState.Unchecked
            elif col == 3:  # Tri-state
                return item["tristate"]
                
        return None
        
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
            
        row, col = index.row(), index.column()
        
        if role == Qt.ItemDataRole.CheckStateRole:
            if col == 1:  # Enabled
                self._data[row]["enabled"] = value == Qt.CheckState.Checked
                self.dataChanged.emit(index, index)
                return True
            elif col == 3:  # Tri-state
                self._data[row]["tristate"] = value
                self.dataChanged.emit(index, index)
                return True
        elif role == Qt.ItemDataRole.EditRole:
            if col == 0:  # Name
                self._data[row]["name"] = value
                self.dataChanged.emit(index, index)
                return True
            elif col == 2:  # Priority
                try:
                    self._data[row]["priority"] = int(value)
                    self.dataChanged.emit(index, index)
                    return True
                except ValueError:
                    return False
                    
        return False
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
            
        col = index.column()
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        
        if col in [1, 3]:  # Checkbox columns
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        if col in [0, 2]:  # Editable columns
            flags |= Qt.ItemFlag.ItemIsEditable
            
        return flags

class ModelCheckboxExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Sample data
        data = [
            {"name": "Feature A", "enabled": True, "priority": 1, "tristate": Qt.CheckState.Checked},
            {"name": "Feature B", "enabled": False, "priority": 2, "tristate": Qt.CheckState.PartiallyChecked},
            {"name": "Feature C", "enabled": True, "priority": 3, "tristate": Qt.CheckState.Unchecked},
        ]
        
        # Create model and view
        self.model = CheckboxTableModel(data)
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        
        # Button to print current state
        print_button = QPushButton("Print Current State")
        print_button.clicked.connect(self.print_state)
        
        layout.addWidget(self.table_view)
        layout.addWidget(print_button)
        
    def print_state(self):
        print("Current model state:")
        for i, item in enumerate(self.model._data):
            tristate_names = {
                Qt.CheckState.Unchecked: "Unchecked",
                Qt.CheckState.PartiallyChecked: "Partial", 
                Qt.CheckState.Checked: "Checked"
            }
            print(f"  {item['name']}: enabled={item['enabled']}, "
                  f"priority={item['priority']}, tristate={tristate_names[item['tristate']]}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModelCheckboxExample()
    window.show()
    sys.exit(app.exec())
```

This advanced patterns document shows how to:

1. **DialogOptionsWidget Pattern**: Manage groups of checkboxes representing flag values
2. **Dependent Checkboxes**: Handle complex interdependencies between checkboxes
3. **Model Integration**: Use checkboxes within Qt's model/view framework for data-driven applications

These patterns can be combined and extended to create sophisticated checkbox-based interfaces for complex applications.