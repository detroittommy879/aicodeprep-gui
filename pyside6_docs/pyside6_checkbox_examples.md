# PySide6 Checkbox Examples and Customization Guide

This document contains examples and techniques for working with checkboxes in PySide6, including tri-state checkboxes, multiple checkboxes on the same line, and custom multi-state checkbox implementations.

## Table of Contents

1. [Basic Tri-State Checkbox](#basic-tri-state-checkbox)
2. [Multiple Checkboxes on Same Line](#multiple-checkboxes-on-same-line)
3. [Custom Multi-State Checkbox Implementation](#custom-multi-state-checkbox-implementation)
4. [Advanced Checkbox Layouts](#advanced-checkbox-layouts)
5. [Custom Checkbox Groups](#custom-checkbox-groups)

## Basic Tri-State Checkbox

The simplest way to create a tri-state checkbox in PySide6 is using the built-in `QCheckBox` with `setTristate(True)`:

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QWidget
import sys

class TriStateExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Create tri-state checkbox
        checkbox = QCheckBox("Tri-state check box")
        checkbox.setTristate(True)
        checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        
        # Connect to state change signal
        checkbox.stateChanged.connect(self.on_state_changed)
        
        layout.addWidget(checkbox)
        
    def on_state_changed(self, state):
        if state == Qt.CheckState.Unchecked:
            print("Unchecked")
        elif state == Qt.CheckState.PartiallyChecked:
            print("Partially Checked")
        elif state == Qt.CheckState.Checked:
            print("Checked")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TriStateExample()
    window.show()
    sys.exit(app.exec())
```

## Multiple Checkboxes on Same Line

Here are several ways to place multiple checkboxes on the same line with different functionalities:

### Method 1: Using QHBoxLayout

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel
import sys

class MultipleCheckboxExample(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        
        # Example 1: Binary + Tri-state on same line
        row1_layout = QHBoxLayout()
        
        binary_checkbox = QCheckBox("Binary")
        binary_checkbox.stateChanged.connect(lambda state: print(f"Binary: {state == Qt.CheckState.Checked}"))
        
        tristate_checkbox = QCheckBox("Tri-state")
        tristate_checkbox.setTristate(True)
        tristate_checkbox.setCheckState(Qt.CheckState.PartiallyChecked)
        tristate_checkbox.stateChanged.connect(self.on_tristate_changed)
        
        row1_layout.addWidget(QLabel("Options:"))
        row1_layout.addWidget(binary_checkbox)
        row1_layout.addWidget(tristate_checkbox)
        row1_layout.addStretch()  # Push checkboxes to the left
        
        # Example 2: Multiple binary checkboxes
        row2_layout = QHBoxLayout()
        
        option1 = QCheckBox("Option 1")
        option2 = QCheckBox("Option 2")
        option3 = QCheckBox("Option 3")
        
        row2_layout.addWidget(QLabel("Features:"))
        row2_layout.addWidget(option1)
        row2_layout.addWidget(option2)
        row2_layout.addWidget(option3)
        row2_layout.addStretch()
        
        main_layout.addLayout(row1_layout)
        main_layout.addLayout(row2_layout)
        
    def on_tristate_changed(self, state):
        states = {
            Qt.CheckState.Unchecked: "Unchecked",
            Qt.CheckState.PartiallyChecked: "Partially Checked", 
            Qt.CheckState.Checked: "Checked"
        }
        print(f"Tri-state: {states[state]}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultipleCheckboxExample()
    window.show()
    sys.exit(app.exec())
```

### Method 2: Using QGridLayout for More Control

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QGridLayout, QWidget, QLabel
import sys

class GridCheckboxExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        
        # Row 1: Different types of checkboxes
        layout.addWidget(QLabel("Mixed Types:"), 0, 0)
        
        normal_cb = QCheckBox("Normal")
        layout.addWidget(normal_cb, 0, 1)
        
        tristate_cb = QCheckBox("Tri-state")
        tristate_cb.setTristate(True)
        layout.addWidget(tristate_cb, 0, 2)
        
        disabled_cb = QCheckBox("Disabled")
        disabled_cb.setEnabled(False)
        disabled_cb.setChecked(True)
        layout.addWidget(disabled_cb, 0, 3)
        
        # Row 2: Grouped functionality
        layout.addWidget(QLabel("Permissions:"), 1, 0)
        
        read_cb = QCheckBox("Read")
        write_cb = QCheckBox("Write")
        execute_cb = QCheckBox("Execute")
        
        layout.addWidget(read_cb, 1, 1)
        layout.addWidget(write_cb, 1, 2)
        layout.addWidget(execute_cb, 1, 3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GridCheckboxExample()
    window.show()
    sys.exit(app.exec())
```

## Custom Multi-State Checkbox Implementation

For more than 3 states, you'll need to create a custom widget. Here's an example of a 5-state checkbox:

```python
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from enum import IntEnum
import sys

class FiveState(IntEnum):
    STATE_0 = 0  # Empty
    STATE_1 = 1  # Quarter filled
    STATE_2 = 2  # Half filled  
    STATE_3 = 3  # Three quarters filled
    STATE_4 = 4  # Fully filled

class FiveStateCheckbox(QWidget):
    stateChanged = Signal(int)
    
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._state = FiveState.STATE_0
        self._text = text
        self.setMinimumSize(200, 30)
        self.setMaximumHeight(30)
        
    def state(self):
        return self._state
        
    def setState(self, state):
        if self._state != state:
            self._state = state
            self.stateChanged.emit(state)
            self.update()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Cycle through states
            next_state = (self._state + 1) % 5
            self.setState(next_state)
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw checkbox square
        checkbox_rect = QRect(5, 5, 20, 20)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(checkbox_rect)
        
        # Fill based on state
        if self._state > FiveState.STATE_0:
            fill_height = int((checkbox_rect.height() - 4) * self._state / 4)
            fill_rect = QRect(
                checkbox_rect.x() + 2,
                checkbox_rect.bottom() - 2 - fill_height,
                checkbox_rect.width() - 4,
                fill_height
            )
            
            # Color gradient from red to green
            colors = [
                QColor(255, 0, 0),      # Red
                QColor(255, 128, 0),    # Orange  
                QColor(255, 255, 0),    # Yellow
                QColor(0, 255, 0)       # Green
            ]
            painter.setBrush(QBrush(colors[self._state - 1]))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(fill_rect)
        
        # Draw text
        if self._text:
            text_rect = QRect(35, 0, self.width() - 35, self.height())
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self._text)

class FiveStateExample(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("State: 0 (Empty)")
        layout.addWidget(self.status_label)
        
        checkbox = FiveStateCheckbox("5-State Progress Checkbox")
        checkbox.stateChanged.connect(self.on_state_changed)
        layout.addWidget(checkbox)
        
        # Multiple 5-state checkboxes
        for i in range(3):
            cb = FiveStateCheckbox(f"Item {i+1}")
            cb.stateChanged.connect(lambda state, idx=i: print(f"Item {idx+1}: State {state}"))
            layout.addWidget(cb)
        
    def on_state_changed(self, state):
        state_names = ["Empty", "Quarter", "Half", "Three Quarters", "Full"]
        self.status_label.setText(f"State: {state} ({state_names[state]})")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FiveStateExample()
    window.show()
    sys.exit(app.exec())
```

This implementation provides:
- 5 distinct visual states with color-coded filling
- Click cycling through all states
- Signal emission for state changes
- Custom painting for visual representation
- Text label support

The custom checkbox can be easily extended to support even more states by modifying the enum and painting logic.