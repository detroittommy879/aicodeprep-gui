import logging
from PySide6 import QtWidgets, QtGui, QtCore

# Custom data role used to store the integer level in the model
LEVEL_ROLE = QtCore.Qt.UserRole + 1


class ComboBoxLevelDelegate(QtWidgets.QStyledItemDelegate):
    """
    A simple delegate that shows an editable combo box for the Level column.
    Stores the integer index in LEVEL_ROLE and stores a human-readable label
    in Qt.DisplayRole so the cell shows text when not editing.
    """

    LEVEL_LABELS = [
        # visually blank instead of "None" (3 spaces)
        "   ",
        "path/to/fileName.only",     # changed from "Paths only"
        "Skeleton (partial)",        # unchanged
        "Full File Contents"         # changed from "Full content"
    ]

    def __init__(self, parent=None, is_dark_mode: bool = False):
        super().__init__(parent)
        self.is_dark_mode = bool(is_dark_mode)

    def createEditor(self, parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.addItems(self.LEVEL_LABELS)
        combo.setEditable(False)
        combo.setFocusPolicy(QtCore.Qt.StrongFocus)

        combo.currentIndexChanged.connect(lambda: self.commitData.emit(combo))
        combo.currentIndexChanged.connect(lambda: self.closeEditor.emit(
            combo, QtWidgets.QAbstractItemDelegate.NoHint))

        return combo

    def setEditorData(self, editor, index):
        try:
            val = index.data(LEVEL_ROLE)
            if val is None:
                val = 0
            val = int(val)
        except Exception:
            val = 0
        if 0 <= val < len(self.LEVEL_LABELS):
            editor.setCurrentIndex(val)
        else:
            editor.setCurrentIndex(0)

    def setModelData(self, editor, model, index):
        idx = editor.currentIndex()
        model.setData(index, idx, LEVEL_ROLE)
        text = self.LEVEL_LABELS[idx] if 0 <= idx < len(
            self.LEVEL_LABELS) else ""
        model.setData(index, text, QtCore.Qt.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                view = option.widget
                if view:
                    view.edit(index)
                    return True
        return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        text = index.data(QtCore.Qt.DisplayRole)
        if not text:
            try:
                level_val = index.data(LEVEL_ROLE)
                level_val = 0 if level_val is None else int(level_val)
                text = self.LEVEL_LABELS[level_val] if 0 <= level_val < len(
                    self.LEVEL_LABELS) else ""
            except Exception:
                text = ""
        opt = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = str(text) if text is not None else ""
        style = QtWidgets.QApplication.style() if opt.widget is None else opt.widget.style()
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem,
                          opt, painter, opt.widget)
