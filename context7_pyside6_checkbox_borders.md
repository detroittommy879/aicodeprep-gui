# PySide6 / Qt: Checkbox Borders — How to Disable or Remove Them (Context7 Research Digest)

Scope: Gather ANY and ALL relevant documentation and patterns from Context7-accessible sources about removing/controlling checkbox borders in PySide6/Qt widgets, with emphasis on QCheckBox indicators in forms and item views (QTreeView/QTreeWidget). Includes QSS selectors, delegate approaches, and known pitfalls.

Note: The PySide6 examples corpus on Context7 (/fernicar/pyside6_examples_doc_2025_v6.9.1) contains no direct stylesheet snippets for checkbox borders; however, Qt style sheet (QSS) targeting is the canonical approach. Below consolidates working selectors and techniques based on Qt’s QSS model and typical implementations for both widgets and item views.

## 1) QCheckBox (Widget) — Remove Border via QSS

To remove the visible “border” or box outline of a standard QCheckBox indicator:

```css
/* Applies to all QCheckBox indicator states */
QCheckBox::indicator {
  width: 16px; /* adjust as needed */
  height: 16px;
  border: none; /* remove border/outline */
  background: transparent; /* ensure no background block shows */
  /* optionally provide custom image or leave empty to show nothing */
  /* image: none; */
}

/* State-specific tweaks (optional) */
QCheckBox::indicator:unchecked {
  border: none;
  background: transparent;
  image: none; /* hide glyph entirely */
}

QCheckBox::indicator:checked {
  border: none;
  background: transparent;
  /* Provide only a checkmark image, no border box */
  image: url(
    data:image/svg + xml;utf8,
    <svgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"><pathd="M2 6l2.5 2.5L10 3"stroke="%230078D4"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/></svg>
  );
}

QCheckBox::indicator:indeterminate {
  border: none;
  background: transparent;
  image: none;
}

/* Remove focus ring around the indicator (some styles draw it) */
QCheckBox::indicator:focus {
  outline: none;
  border: none;
}

/* Optional hover/pressed states if the style paints a ring on interaction */
QCheckBox::indicator:hover,
QCheckBox::indicator:pressed {
  border: none;
  background: transparent;
}
```

Apply to a specific widget:

```python
checkbox.setStyleSheet("""
QCheckBox::indicator { border: none; background: transparent; }
QCheckBox::indicator:checked { image: none; }
""")
```

Apply app-wide:

```python
app.setStyleSheet(open("style.qss","r",encoding="utf-8").read())
```

## 2) QTreeView / QTreeWidget Checkboxes — Remove Indicator Border via QSS

Item views render a checkbox indicator for checkable items (Qt.ItemIsUserCheckable / Qt.CheckStateRole). You can style their indicators similarly:

```css
/* Works for both QTreeView and QTreeWidget (use either selector or both) */
QTreeView::indicator,
QTreeWidget::indicator {
  width: 16px;
  height: 16px;
  border: none; /* remove border */
  background: transparent; /* avoid any background block */
  image: none; /* if you want no glyph shown at all */
}

/* Explicit states */
QTreeView::indicator:unchecked,
QTreeWidget::indicator:unchecked {
  border: none;
  background: transparent;
  image: none;
}

QTreeView::indicator:checked,
QTreeWidget::indicator:checked {
  border: none;
  background: transparent;
  /* Custom check glyph without a box border */
  image: url(
    data:image/svg + xml;utf8,
    <svgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"><pathd="M2 6l2.5 2.5L10 3"stroke="%230078D4"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/></svg>
  );
}

/* Remove focus/hover outlines some styles may add */
QTreeView::indicator:focus,
QTreeWidget::indicator:focus,
QTreeView::indicator:hover,
QTreeWidget::indicator:hover,
QTreeView::indicator:pressed,
QTreeWidget::indicator:pressed {
  border: none;
  background: transparent;
  outline: none;
}
```

Notes:

- If your platform style paints a ring around the row rather than the indicator, also consider view-level selectors (e.g., QTreeView::item:focus { outline: none; }).
- In complex themes, set both border and outline to none, and make sure no background shows on state changes.

## 3) If QSS Is Not Enough: Custom Delegate Rendering

Qt’s built-in checkbox rendering in item views can still draw elements depending on QStyle and platform. If QSS fails to remove the box, override painting with a delegate:

Minimal pattern:

```python
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter

class CheckboxNoBorderDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):
        # Let base draw the item text/background
        QStyledItemDelegate.paint(self, painter, option, index)

        # Handle check state and draw a custom glyph without any border
        state = index.data(Qt.CheckStateRole)
        if state is not None:
            # Compute indicator rect; reuse option rect or compute a 16x16 rect with padding
            r = option.rect
            size = 16
            x = r.left() + 4
            y = r.center().y() - size // 2
            target = QRect(x, y, size, size)

            painter.save()
            painter.setRenderHint(QPainter.Antialiasing, True)

            # No border box: we draw only a checkmark when checked
            if state == Qt.Checked:
                pen = painter.pen()
                pen.setColor(option.palette.highlight().color())  # or a fixed QColor
                pen.setWidth(2)
                painter.setPen(pen)
                # Simple check glyph
                painter.drawLine(target.left()+3, target.center().y(), target.center().x()-1, target.bottom()-3)
                painter.drawLine(target.center().x()-1, target.bottom()-3, target.right()-3, target.top()+3)
            # If unchecked, draw nothing

            painter.restore()

    # Allow toggling if needed; or keep default editorEvent behavior
```

Attach to a view/column:

```python
tree.setItemDelegateForColumn(0, CheckboxNoBorderDelegate(tree))
```

For multi-state custom checkbox visuals (unchecked/checked/indeterminate or additional custom states), store integers in Qt.CheckStateRole and cycle them in editorEvent while drawing custom icons in paint().

## 4) View-Level Outline Removal (Row Focus/Hover)

Some environments show a focus rectangle at the row/item level rather than around the indicator. Disable it:

```css
QTreeView::item:focus,
QTreeWidget::item:focus {
  outline: none;
}

QTreeView::item:selected:active,
QTreeView::item:selected:!active {
  outline: none;
}

QTreeView {
  outline: 0; /* sometimes required on certain styles */
}
```

Also consider:

```css
QCheckBox:focus {
  outline: none;
}
```

if standard widgets exhibit a focus ring.

## 5) Dark Mode Considerations

If you supply a checkmark image without a box, ensure contrast:

```css
/* Dark mode variant */
QTreeView::indicator:checked,
QTreeWidget::indicator:checked {
  image: url(
    data:image/svg + xml;utf8,
    <svgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"><pathd="M2 6l2.5 2.5L10 3"stroke="%23FFFFFF"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/></svg>
  );
}
```

Or swap images conditionally when your theme toggles.

## 6) Related Context7 Evidence (PySide6 corpus)

The PySide6 examples corpus accessible via Context7 does not include direct QSS for checkbox borders, but it shows:

- Check state usage via Qt.CheckStateRole in item views.
- Patterns for QStyledItemDelegate subclassing for custom painting (e.g., “stardelegate”).
- QTreeView API usage and item roles.

Key snippets retrieved (IDs point to /fernicar/pyside6_examples_doc_2025_v6.9.1):

- QTreeView API reference and model/view roles (dirview README #\_snippet_1, tutorials/modelview snippets)
- Check state role usage within model data() (tutorials/modelview README #\_snippet_1)
- QStyledItemDelegate customization (stardelegate README #\_snippet_5)

These confirm standard mechanisms for showing/hiding and customizing check state visuals which we leverage with QSS or delegates to remove borders.

## 7) Troubleshooting

- Border still shows:

  - Ensure you target the correct selector: QCheckBox::indicator vs QTreeView::indicator/QTreeWidget::indicator.
  - Remove both border and outline; set background: transparent.
  - Some platform styles ignore parts of QSS for indicators in item views; in that case, use a delegate to draw only a checkmark without a box.

- Image vs no image:

  - If you set image: none; for checked state, users will not see any glyph when checked. Prefer a checkmark-only image if you need visual feedback but no box.

- Hit area too small after removing box:
  - QSS width/height of the indicator controls click target in item views. Keep it reasonable (e.g., 16–20 px).

## 8) Quick Copy-Paste Blocks

All checkboxes everywhere (widgets + tree/list):

```css
QCheckBox::indicator,
QTreeView::indicator,
QTreeWidget::indicator {
  width: 16px;
  height: 16px;
  border: none;
  outline: none;
  background: transparent;
}

QCheckBox::indicator:unchecked,
QTreeView::indicator:unchecked,
QTreeWidget::indicator:unchecked {
  image: none;
}

QCheckBox::indicator:checked,
QTreeView::indicator:checked,
QTreeWidget::indicator:checked {
  border: none;
  background: transparent;
  image: url(
    data:image/svg + xml;utf8,
    <svgxmlns="http://www.w3.org/2000/svg"width="12"height="12"viewBox="0 0 12 12"><pathd="M2 6l2.5 2.5L10 3"stroke="%230078D4"stroke-width="2"fill="none"stroke-linecap="round"stroke-linejoin="round"/></svg>
  );
}

QTreeView::item:focus,
QTreeWidget::item:focus,
QCheckBox:focus {
  outline: none;
}
```

Delegate fallback (item views):

- Use a QStyledItemDelegate to draw only a checkmark for Qt.Checked and nothing for Qt.Unchecked. This bypasses style-driven box borders entirely.

## 9) Summary

- Primary approach: QSS selectors on ::indicator with border:none; background:transparent; image:none or a checkmark-only image.
- For QTreeView/QTreeWidget checkboxes, use QTreeView::indicator / QTreeWidget::indicator with the same properties.
- If a platform style still paints a border, override paint() in a QStyledItemDelegate to render your own glyphs.
- Remove view-level focus outlines if they visually appear as “borders.”
