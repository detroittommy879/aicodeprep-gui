# PySide6 Qt Documentation - Checkboxes and QTreeWidget Styling

## Overview

This document contains relevant PySide6 documentation for working with QTreeWidget checkboxes and custom styling.

## QTreeWidget Checkbox Styling

### Basic QTreeWidget Setup

```python
import sys
from PySide6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem

app = QApplication()
tree = QTreeWidget()
tree.setColumnCount(2)
tree.setHeaderLabels(["Name", "Type"])
```

### Populating QTreeWidget with Checkable Items

```python
# Example data structure
data = {"Project A": ["file_a.py", "file_a.txt", "something.xls"],
        "Project B": ["file_b.csv", "photo.jpg"],
        "Project C": []}

# Populate tree with checkable items
items = []
for key, values in data.items():
    item = QTreeWidgetItem([key])
    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
    item.setCheckState(0, QtCore.Qt.Unchecked)

    for value in values:
        ext = value.split(".")[-1].upper()
        child = QTreeWidgetItem([value, ext])
        child.setFlags(child.flags() | QtCore.Qt.ItemIsUserCheckable)
        child.setCheckState(0, QtCore.Qt.Unchecked)
        item.addChild(child)
    items.append(item)

tree.insertTopLevelItems(0, items)
```

## Custom Styling with StyleSheets

### Basic QTreeWidget Indicator Styling

```css
QTreeView::indicator,
QTreeWidget::indicator {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

QTreeView::indicator:unchecked,
QTreeWidget::indicator:unchecked {
  background-color: #ffffff;
  border: 2px solid #aaaaaa;
}

QTreeView::indicator:checked,
QTreeWidget::indicator:checked {
  background-color: #ffffff;
  border: 2px solid #0078d4;
  image: url(
    data:image/svg + xml;charset=utf-8,
    %3Csvgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"%3E%3Cpathd="M2 6l2.5 2.5L10 3"stroke="%230078D4"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/%3E%3C/svg%3E
  );
}
```

### Applying Stylesheets in PySide6

```python
from PySide6.QtWidgets import QApplication

# Method 1: Apply to specific widget
tree_widget.setStyleSheet("""
    QTreeWidget::indicator:checked {
        image: url(:/icons/checkmark.png);
    }
""")

# Method 2: Apply to entire application
app = QApplication()
with open("style.qss", "r") as f:
    _style = f.read()
    app.setStyleSheet(_style)
```

## Creating Custom Checkmark Images Programmatically

### Using QPainter to Create Checkmark

```python
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt

def create_checkmark_pixmap(size=16, color="#0078D4"):
    """Create a checkmark pixmap programmatically."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    pen = QPen(QColor(color))
    pen.setWidth(2)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)

    # Draw checkmark path
    painter.drawLine(4, 8, 7, 11)
    painter.drawLine(7, 11, 12, 4)

    painter.end()
    return pixmap
```

## Common QTreeWidget Patterns

### Handling Item State Changes

```python
def handle_item_changed(self, item, column):
    if column == 0:
        new_state = item.checkState(0)
        # Apply state to children
        def apply_to_children(parent_item, state):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                if child.flags() & QtCore.Qt.ItemIsUserCheckable:
                    child.setCheckState(0, state)
                    if child.childCount() > 0:
                        apply_to_children(child, state)
        apply_to_children(item, new_state)

# Connect the signal
tree_widget.itemChanged.connect(handle_item_changed)
```

### Getting Selected Items

```python
def get_selected_files(self):
    selected = []
    iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_widget)
    while iterator.value():
        item = iterator.value()
        if item.checkState(0) == QtCore.Qt.Checked:
            file_path = item.data(0, QtCore.Qt.UserRole)
            if file_path and os.path.isfile(file_path):
                selected.append(file_path)
        iterator += 1
    return selected
```

## Dark Mode Support

### Detecting System Dark Mode

```python
def system_pref_is_dark() -> bool:
    """Detect if system is using dark mode."""
    system = platform.system()

    if system == "Darwin":  # macOS
        try:
            import subprocess
            cmd = "defaults read -g AppleInterfaceStyle"
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            return result.stdout.strip() == "Dark"
        except:
            pass

    elif system == "Windows":  # Windows 10+
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            reg_keypath = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            key = winreg.OpenKey(registry, reg_keypath)
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except:
            pass

    # Fallback: use palette heuristic
    return QApplication.palette().color(QPalette.Window).lightness() < 128
```

### Dark Mode Checkbox Styling

```css
/* Dark mode checkbox styling */
QTreeView::indicator:unchecked,
QTreeWidget::indicator:unchecked {
  background-color: #2b2b2b;
  border: 2px solid #555555;
}

QTreeView::indicator:checked,
QTreeWidget::indicator:checked {
  background-color: #2b2b2b;
  border: 2px solid #0078d4;
  image: url(
    data:image/svg + xml;charset=utf-8,
    %3Csvgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"%3E%3Cpathd="M2 6l2.5 2.5L10 3"stroke="%230078D4"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/%3E%3C/svg%3E
  );
}
```

## Best Practices

1. **Always use SVG for scalable icons** - SVG icons scale better across different DPI settings
2. **Provide both light and dark mode styles** - Modern applications should support both themes
3. **Use data URIs for simple icons** - Avoids external file dependencies
4. **Test on different operating systems** - Checkbox rendering can vary between platforms
5. **Use proper signal blocking** - Prevent infinite loops when programmatically changing states

## Troubleshooting Common Issues

### Issue: Checkboxes show solid color instead of checkmark

**Solution**: Ensure the `image` property is set in the CSS for the `:checked` state, and that the image path/data URI is valid.

### Issue: Checkmark not visible in dark mode

**Solution**: Use appropriate contrast colors and ensure the SVG stroke color is visible against the background.

### Issue: Performance issues with large trees

**Solution**: Use lazy loading and virtual scrolling for large datasets.
