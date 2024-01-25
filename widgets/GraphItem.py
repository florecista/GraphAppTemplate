from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsPixmapItem, QApplication

from widgets.GraphEdgePoint import GraphEdgePoint


class GraphItem(QGraphicsPixmapItem):
    pen = QtGui.QPen(Qt.red, 2)
    brush = QtGui.QBrush(QtGui.QColor(31, 176, 224))
    controlBrush = QtGui.QBrush(QtGui.QColor(214, 13, 36))

    def __init__(self, parent, left=False, right=False):
        super().__init__(parent)

        self._is_hovered = False

        self.startPosition = None

        self.controls = []

        for onLeft, create in enumerate((right, left)):
            if create:
                control = GraphEdgePoint(self, onLeft)
                self.controls.append(control)
                control.setPen(self.pen)
                control.setBrush(self.controlBrush)
                if onLeft:
                    control.setX(50)
                control.setY(20)

    ## Adding hover
    ## Reference - https://stackoverflow.com/questions/56266185/painting-qgraphicspixmapitem-border-on-hover
    def hoverEnterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self._is_hovered or self.isSelected():
            painter.save()
            pen = QtGui.QPen(QtGui.QColor("red"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())
            painter.restore()

    def _get_label(self):
        return self.label

    def _set_label(self, _label):
        self.label = _label

    def _get_attributes(self):
        return self.attributes

    def _set_attributes(self, _attributes):
        self.attributes = _attributes

    def _get_pixmap(self):
        return self.pixmap

    def _set_pixmap(self, _pixmap):
        self.pixmap = _pixmap

    # Reference - https://stackoverflow.com/questions/72535825/pyqt5-qgraphicsscene-mouse-item-with-click-and-drop-without-holding-press
    moving = False
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.type() == Qt.MouseButton.LeftButton:
            # by defaults, mouse press events are not accepted/handled,
            # meaning that no further mouseMoveEvent or mouseReleaseEvent
            # will *ever* be received by this item; with the following,
            # those events will be properly dispatched
            event.accept()
            self.startPosition = event.screenPos()
            self.setPos(self.startPosition)

    def mouseMoveEvent(self, event):
        if self.moving:
            # map the position to the parent in order to ensure that the
            # transformations are properly considered:
            currentParentPos = self.mapToParent(
                self.mapFromScene(event.scenePos()))
            originParentPos = self.mapToParent(
                self.mapFromScene(event.buttonDownScenePos(Qt.LeftButton)))
            self.setPos(self.startPosition + currentParentPos - originParentPos)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.type() == Qt.MouseButton.LeftButton or event.pos() not in self.boundingRect():
            return

        # the following code block is to allow compatibility with the
        # ItemIsMovable flag: if the item has the flag set and was moved while
        # keeping the left mouse button pressed, we proceed with our
        # no-mouse-button-moved approach only *if* the difference between the
        # pressed and released mouse positions is smaller than the application
        # default value for drag movements; in this way, small, involuntary
        # movements usually created between pressing and releasing the mouse
        # button will still be considered as candidates for our implementation;
        # if you are *not* interested in this flag, just ignore this code block
        distance = (event.screenPos() - self.pos()).manhattanLength()
        startDragDistance = QApplication.startDragDistance()
        if not self.moving and distance > startDragDistance:
            return
        # end of ItemIsMovable support

        self.moving = not self.moving
        # the following is *mandatory*
        self.setAcceptHoverEvents(self.moving)
        if self.moving:
            self.startPosition = self.pos()
            self.grabMouse()
        else:
            self.ungrabMouse()