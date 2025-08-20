# PySide6 — Themes, Styling & Theming Guide

This guide summarizes best-practices and examples for applying themes, styles, and custom styling in PySide6 (Qt for Python). Content synthesized from the PySide6 examples documentation (examples, charts, widgets, QML modules).

## Overview

- Two main approaches:
  - QStyle / QStyleFactory (native Qt styles, platform/look-and-feel).
  - QSS (Qt Style Sheets) — CSS-like styling applied to widgets or entire application.
- Additional ways to affect visuals:
  - QPalette for color roles
  - QPainter render hints (e.g., antialiasing)
  - Module/theme APIs (e.g., QtCharts QChart.ChartTheme, Qt3D Theme3D)
  - QML-level theming using shared QML modules (e.g., UIStyle.qml, Button.qml)
  - Custom drawing and QSyntaxHighlighter for fine-grained control

## Quick examples

### Set an application style (QStyle)

```python
# python
from PySide6.QtWidgets import QApplication, QStyleFactory

app = QApplication([])
style = QStyleFactory.create("Fusion")  # e.g., "Windows", "Fusion", "GTK+", etc.
app.setStyle(style)
```

You can populate a QComboBox with available styles and call `QApplication.setStyle(QStyleFactory.create(name))` at runtime to let users switch styles dynamically.

### Apply a QSS stylesheet (global)

```python
# python
with open("mytheme.qss", "r") as f:
    app.setStyleSheet(f.read())
```

Sample QSS snippet (mytheme.qss):

```css
QPushButton {
  background: qlineargradient(
    x1: 0,
    y1: 0,
    x2: 0,
    y2: 1,
    stop: 0 #6fbf73,
    stop: 1 #2e8b57
  );
  border: 1px solid #0b6b3a;
  color: white;
  padding: 6px 10px;
  border-radius: 4px;
}
QPushButton:pressed {
  background: #1e5e3e;
}
```

### Adjust QPalette programmatically

```python
# python
from PySide6.QtGui import QPalette, QColor

palette = app.palette()
palette.setColor(QPalette.Window, QColor("#1e1e1e"))
palette.setColor(QPalette.WindowText, QColor("#e6e6e6"))
app.setPalette(palette)
```

Use QPalette when you need to change standard role colors (e.g., Window, Button, Text) and ensure widgets using palette roles update automatically.

### Enable anti-aliasing for custom painting or charts

```python
# python
chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
```

### QtCharts theme example

```python
# python
from PySide6.QtCharts import QChart

chart.setTheme(QChart.ChartTheme.ChartThemeBrownSand)  # use available QChart.ChartTheme enums
chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
```

## Widget-level customization via model/view roles

- Customize item appearance in models by returning values for Qt.ItemDataRole in `data()` (e.g., `Qt.FontRole`, `Qt.BackgroundRole`, `Qt.TextAlignmentRole`, `Qt.CheckStateRole`).
- Useful for QTableView / QListView / QTreeView styling without QSS.

## Custom painting and syntax highlighting

- Override `QWidget.paintEvent()` for bespoke visuals.
- Use `QSyntaxHighlighter` to apply formatting to QTextDocument via `setFormat(start, count, format)`.

## QML theming approach

- Create a singleton QML file (UIStyle.qml) that exports theme tokens (colors, fonts, sizes).
- Implement custom control QML files (Button.qml, TextField.qml) that consume UIStyle.qml for a consistent look.
- Bundle as a QML module (e.g., QtExampleStyle) and add the module to import path.
- For Python-backed QML components, expose classes using `@QmlElement` and add the directory to QQmlApplicationEngine import path.

QML snippets:

```qml
// UIStyle.qml (conceptual)
pragma Singleton
QtObject {
  property color primaryColor: "#3498db"
  property color accentColor: "#2ecc71"
  property int baseFontSize: 14
}
```

Instantiate and use in custom control:

```qml
import QtQuick.Controls 2.15
import QtExampleStyle 1.0

Button {
  background: Rectangle { color: UIStyle.primaryColor }
  font.pixelSize: UIStyle.baseFontSize
}
```

## Integrating Python textures / custom QML types

- Example: `GradientTexture` implemented as a `QQuick3DTextureData` subclass. Expose with `@QmlElement` and bind properties (startColor, endColor, width, height) from QML.
- Load QML modules by adding import path:

```python
engine.addImportPath(str(app_dir))
engine.loadFromModule("ProceduralTextureModule", "Main")
```

## Compiling Qt Designer .ui files

- Use the CLI to compile .ui into Python:

```bash
pyside6-uic themewidget.ui -o ui_themewidget.py
```

## Packaging a QML style module (CMake hint)

- Example CMakeLists for a QtExampleStyle QML module shows registering QML files and installing module metadata (qmldir). Useful if shipping a reusable style module.

## Practical recommendations

- Prefer QSS for visual customization when you want CSS-like control across many widgets.
- Use QStyleFactory / native styles for platform-consistent appearance.
- Combine QPalette adjustments with QSS for finer color control when needed.
- For charts and specialized modules, prefer built-in theme enums (e.g., QChart.ChartTheme, Theme3D) to maintain consistency.
- Build a single source-of-truth for tokens (colors, fonts) — either a Python module, QML singleton, or a central QSS file — to make theme changes easy.
- When using QML, centralize style values in a singleton QML (UIStyle.qml) and create custom control wrappers (Button.qml, TextField.qml) that reference those tokens.

## Useful code pointers (from examples)

- Dynamically populate combo boxes with theme/style enums (e.g., `populate_themebox()`).
- Centralize an `update_ui()` handler that reads UI controls and applies theme changes across charts/widgets.
- For high-quality rendering, toggle `QPainter.RenderHint.Antialiasing` as needed.
- Use `QApplication.widgetAt(QCursor.pos())` for context help on hover and to open docs for a widget under cursor.

## References / sources

- PySide6 examples documentation (examples demonstrating charts theme switching, widget gallery, QML styling and ColorPalette demo).
- Key example areas: charts/chartthemes, demos/colorpaletteclient (QtExampleStyle + UIStyle.qml), widgets/widgetsgallery, quick3d/proceduraltexture.

(Notes: snippets and guidance compiled from the `/fernicar/pyside6_examples_doc_2025_v6.9.1` collection of examples.)
