# Level Column (5-State) Delegate – Implementation & Customization Guide

This guide explains how the new 5-state “Level” column is implemented in the file/folder tree and how to customize its visuals and behavior.

## Overview

- Column 0: Existing include/exclude checkbox using Qt’s built-in ItemIsUserCheckable and CheckStateRole.
- Column 1 (“Level”): New custom 5-state indicator rendered via a QStyledItemDelegate. Clicking cycles through states 0..4. This indicator is independent of the standard checkbox logic in column 0.

The 5-state values are stored on each item in a custom data role to avoid conflicts:

- LEVEL_ROLE = Qt.UserRole + 1 (integer 0..4)

## Files

1. Delegate:

   - aicodeprep_gui/gui/components/multi_state_level_delegate.py
   - Class: MultiStateLevelDelegate
   - Role: LEVEL_ROLE (Qt.UserRole + 1)

2. Main window wiring:

   - aicodeprep_gui/gui/main_window.py
   - Adds second column and sets the delegate for column 1
   - Initializes per-item state: item.setData(1, LEVEL_ROLE, 0)

3. Lazy-loaded children:
   - aicodeprep_gui/gui/components/tree_widget.py
   - on_item_expanded(): creates children with two columns and sets LEVEL_ROLE to 0

## How It Works

### Storage

Each item’s Level state is stored as an integer:

```python
from .components.multi_state_level_delegate import LEVEL_ROLE

item.setData(1, LEVEL_ROLE, 0)  # default
```

This keeps Level state separate from the checkbox in column 0 (which uses CheckStateRole).

### Painting

The delegate paints a 16x16 rounded square centered in the cell, with color chosen based on the current state:

```python
COLORS_LIGHT = {
    0: QtGui.QColor("#A0A0A0"),  # gray
    1: QtGui.QColor("#1E90FF"),  # blue
    2: QtGui.QColor("#32CD32"),  # green
    3: QtGui.QColor("#FFD700"),  # gold
    4: QtGui.QColor("#FF4500"),  # orange-red
}
```

The size and placement are controlled by:

```python
BOX_SIZE = 16
def _indicator_rect(option) -> QRect:
    # centered rect in the cell
```

### Interaction

The delegate listens to mouse events in editorEvent(). On left click within the indicator’s rectangle, it cycles:

```
next_state = (current_state + 1) % 5
```

and writes back with:

```python
model.setData(index, next_state, LEVEL_ROLE)
```

## How to Customize the Visuals

You can replace the painted color square with:

- Custom icons (QIcon)
- Bitmaps (QPixmap)
- Programmatically generated drawings with QPainter

### Option A: Replace Fill With Icons

```python
def paint(...):
    # after computing rect
    icon = QtGui.QIcon(":/icons/level_1.png")  # Use Qt resource or file path
    # Option 1: Let icon render itself into the rect
    icon.paint(painter, rect)

    # Option 2: Use QPixmap
    pix = QtGui.QPixmap(":/icons/level_1.png")
    target = rect.adjusted(1, 1, -1, -1)  # small inset
    painter.drawPixmap(target, pix)
```

Notes:

- Provide one icon per state (e.g., level_0.png, level_1.png, …).
- For DPI scaling, prefer SVG or high-resolution PNGs, or draw programmatically.

### Option B: Programmatically Generated Graphics

Use QPainterPath, gradients, or custom shapes:

```python
path = QtGui.QPainterPath()
path.addRoundedRect(QtCore.QRectF(rect), 3, 3)
painter.fillPath(path, QtGui.QBrush(QtGui.QColor("#32CD32")))
painter.setPen(QtGui.QPen(QtGui.QColor("#666"), 1))
painter.drawPath(path)
```

You can also draw small overlays (e.g., tick, star) using QPainter.

### Size and Position

- Change BOX_SIZE to grow/shrink the indicator.
- Modify \_indicator_rect to offset it towards left/right, or to align multiple icons in the same cell.

Example:

```python
def _indicator_rect(option):
    r = option.rect
    size = 18
    x = r.x() + 6  # left pad
    y = r.y() + (r.height() - size) // 2
    return QtCore.QRect(x, y, size, size)
```

## How to Customize Interaction

By default, left mouse press/release cycles the state 0→1→2→3→4→0.

You can:

- Restrict to MouseButtonRelease only
- Ignore double-clicks
- Add keyboard handling (KeyPress)
- Add a context menu to select a specific state

Example (right-click menu):

```python
if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.RightButton:
    menu = QtWidgets.QMenu()
    for value, label in [(0, "None"), (1, "Blue"), (2, "Green"), (3, "Gold"), (4, "Orange-Red")]:
        act = menu.addAction(label)
        act.triggered.connect(lambda checked, v=value: model.setData(index, v, LEVEL_ROLE))
    # Show menu at cursor position
    menu.exec(QtGui.QCursor.pos())
    return True
```

## Wiring It Up (Summary)

In main_window.py:

```python
self.tree_widget.setHeaderLabels(["File/Folder", "Level"])
self.tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
self.tree_widget.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

# Initialize items
item = QtWidgets.QTreeWidgetItem(parent, [text, ""])
item.setData(1, LEVEL_ROLE, 0)

# Attach delegate
self.level_delegate = MultiStateLevelDelegate(self.tree_widget, is_dark_mode=self.is_dark_mode)
self.tree_widget.setItemDelegateForColumn(1, self.level_delegate)
```

In tree_widget.py (lazy load):

```python
new_item = QtWidgets.QTreeWidgetItem(parent, [name, ""])
new_item.setData(1, LEVEL_ROLE, 0)
```

## Best Practices

- Keep state in a custom role (LEVEL_ROLE) to avoid colliding with the existing checkbox state.
- Cache any heavy resources (e.g., icons, generated pixmaps) inside the delegate to avoid re-loading on every paint.
- Respect selection visuals by letting the style draw the base cell before painting your indicator.
- Consider accessibility: provide tooltips or an alternate text representation if needed.

## Troubleshooting

- Indicator not visible:
  - Ensure the delegate is set for column 1.
  - Confirm items have 2 columns and LEVEL_ROLE is initialized.
- Clicks don’t change state:
  - Verify editorEvent checks for index.column() == 1 and the indicator rectangle contains the click.
- Layout issues:
  - Adjust \_indicator_rect and BOX_SIZE.
  - Change header resize mode if the column is too narrow (ResizeToContents or Fixed with setColumnWidth).
