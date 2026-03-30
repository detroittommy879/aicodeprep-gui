from PySide6 import QtWidgets, QtCore
import sys

app = QtWidgets.QApplication(sys.argv)
cb = QtWidgets.QComboBox()
cb.addItems(["a", "b", "c"])
cb.setEditable(True)
cb.show()

def val_changed():
    print("Changed to:", cb.currentText())
cb.currentTextChanged.connect(val_changed)

def timer_update():
    idx = cb.findText("d", QtCore.Qt.MatchExactly)
    if idx >= 0:
        cb.setCurrentIndex(idx)
    else:
        cb.setCurrentText("d")
    print("Set programmatically to:", cb.currentText())

QtCore.QTimer.singleShot(500, timer_update)
QtCore.QTimer.singleShot(1000, app.quit)
sys.exit(app.exec())
