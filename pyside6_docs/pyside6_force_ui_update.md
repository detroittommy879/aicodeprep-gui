# PySide6: Forcing UI Updates and Refreshes

This document summarizes key PySide6 patterns and API methods for forcing UI updates, repainting widgets, and ensuring changes are reflected in the interface. These are drawn from official examples and documentation.

---

## 1. QWidget and QQuickPaintedItem: `update()` and `repaint()`

- **`update()`** schedules a repaint of the widget. The next event loop iteration will call `paintEvent`.
- **`repaint()`** forces an immediate repaint (less common, use with care).

**Example:**

```python
self.update()  # Schedules a repaint
self.repaint() # Forces immediate repaint
```

**QQuickPaintedItem Example:**

```python
def color(self, value):
    if value != self._color:
        self._color = value
        self.update()  # Schedule repaint
        self.colorChanged.emit()
```

---

## 2. Emitting Signals to Notify Views/Bindings

- For QML or property bindings, emit a notify signal after changing a property.
- This ensures QML/UI bindings react and update.

**Example:**

```python
@Property(bool, notify=rightAlignedChanged)
def rightAligned(self):
    return self._rightAligned

@rightAligned.setter
def rightAligned(self, value: bool):
    if self._rightAligned != value:
        self._rightAligned = value
        self.rightAlignedChanged.emit()
```

---

## 3. Model/View: Emitting `dataChanged` for Table/Tree Updates

- When model data changes, emit `dataChanged` to notify views to repaint affected cells.

**Example:**

```python
def setData(self, index, value, role):
    if role == Qt.EditRole:
        self._grid_data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index, [Qt.EditRole])
        return True
    return False
```

**Dynamic Update with QTimer:**

```python
def timer_hit(self):
    top_left = self.createIndex(0, 0)
    self.dataChanged.emit(top_left, top_left, [Qt.DisplayRole])
```

---

## 4. Custom Widgets: Overriding `paintEvent` and Calling `update()`

- For custom drawing, override `paintEvent`.
- Call `update()` whenever the widget's state changes.

**Example:**

```python
def set_on(self, value):
    self._on = value
    self.update()  # Triggers repaint

def paintEvent(self, event):
    # Custom drawing logic
```

---

## 5. Forcing Canvas/Plot Redraws

- For matplotlib or custom canvas widgets, call their `draw()` method after updating data.

**Example:**

```python
self.canvas2.draw()  # Refreshes display after data change
```

---

## 6. QML Bindings: Property Binding and Signal Emission

- Bind QML properties to Python properties with notify signals.
- Changing the Python property and emitting the signal updates the QML UI.

**QML Example:**

```qml
Rectangle {
    id: chartA
    color: "red"
}
Rectangle {
    id: chartB
    color: chartA.color  // Updates automatically when chartA.color changes
}
```

---

## 7. Animation and Timers

- Use `QTimer` to periodically update widget state and call `update()` for smooth animations.

**Example:**

```python
self._timer.timeout.connect(self.next_animation_frame)
self._timer.start()

def next_animation_frame(self):
    # Update animation state
    self.update()  # Schedule repaint
```

---

## 8. Refreshing Models and Lists

- For models (e.g., QAbstractListModel), provide a method to refresh data and notify views.

**Example:**

```python
def populate(self):
    # Update internal list
    self.layoutChanged.emit()  # Notifies view to refresh
```

---

## References

- [QQuickPaintedItem.update() API](https://github.com/fernicar/pyside6_examples_doc_2025_v6.9.1/blob/6.9.1/examples/qml/tutorials/extending-qml/chapter2-methods/README.md#_snippet_6)
- [Model/View Data Update](https://github.com/fernicar/pyside6_examples_doc_2025_v6.9.1/blob/6.9.1/examples/widgets/tutorials/modelview/README.md#_snippet_2)
- [Custom Widget PaintEvent](https://github.com/fernicar/pyside6_examples_doc_2025_v6.9.1/blob/6.9.1/examples/widgets/painting/concentriccircles/README.md#_snippet_3)
- [QML Property Binding](https://github.com/fernicar/pyside6_examples_doc_2025_v6.9.1/blob/6.9.1/examples/qml/tutorials/extending-qml/chapter3-bindings/doc/chapter3-bindings.rst#_snippet_0)

---

**Troubleshooting Tips:**

- Always call `update()` after changing widget state.
- For models, emit `dataChanged` or `layoutChanged` after modifying data.
- For QML, ensure notify signals are emitted after property changes.
- For custom canvases, call their `draw()` method after updating data.
