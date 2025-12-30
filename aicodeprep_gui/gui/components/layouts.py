from PySide6 import QtWidgets, QtCore

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)
        self._hspacing = hspacing
        self._vspacing = vspacing

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)
        self.invalidate()

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        return self.smartSpacing(QtWidgets.QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        return self.smartSpacing(QtWidgets.QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            self.invalidate()
            return item
        return None
        
    def insertWidget(self, index, widget):
        self.insertItem(index, QtWidgets.QWidgetItem(widget))

    def insertItem(self, index, item):
        self._items.insert(index, item)
        self.invalidate()

    def removeWidget(self, widget):
        for i, item in enumerate(self._items):
            if item.widget() is widget:
                self.takeAt(i)
                # Do not delete the widget, the caller is responsible
                break
    
    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        m = self.contentsMargins()
        x = rect.x() + m.left()
        y = rect.y() + m.top()
        lineHeight = 0

        spaceX = self.horizontalSpacing()
        spaceY = self.verticalSpacing()

        for item in self._items:
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() - m.right() and lineHeight > 0:
                x = rect.x() + m.left()
                y = y + lineHeight + spaceY
                lineHeight = 0
            
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = x + item.sizeHint().width() + spaceX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight + m.bottom()

    def smartSpacing(self, pm):
        parent = self.parent()
        if not parent:
            return -1
        if parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()
