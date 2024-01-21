import io
import os

from managers import js_manager
from PIL import Image
from PyQt5.QtCore import Qt, QBuffer, QByteArray, QPoint
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPixmapItem, \
    QGraphicsItem

from widgets.GraphItem import GraphItem


class GraphScene(QGraphicsScene):

    def __init__(self, parent):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        print('GraphScene.initUI')

    def add_node(self, position, attributes):
        offset = 50
        position = QPoint(position.x()-offset, position.y()-offset)

        image = ''
        for item in js_manager.data[attributes["Group"]]:
            if item['label'] == attributes["Type"]:
                image = item['icon']
                break

        attributes["Label"] = "Node Name"
        attributes["Position"] = self.__pos_to_str([position.x(), position.y()])
        attributes["Image"] = {"name": "", "image": ""}
        attributes["Image Scale"] = True

        # build pixmap
        icon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r"\images\\" + image
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio)

        # build graph item
        graphItem = GraphItem(pixmap)
        graphItem.attributes = attributes
        graphItem.setPos(position)
        graphItem.setFlags(QGraphicsPixmapItem.ItemIsMovable)

        fullscreen_canvas_width = self.parent().width()
        fullscreen_canvas_height = self.parent().height()
        # The reason for this is that by default, QGraphicsScene computes its sceneRect
        # by adding all the item rectangles together. When you add the first item, it
        # automatically uses it as the scene rect. And by default QGraphicsView scales
        # and centers on the scene rect.
        # Reference : https://stackoverflow.com/questions/11825722/why-do-the-first-added-item-always-appear-at-the-center-in-a-graphics-scene-view
        self.setSceneRect(0, 0, fullscreen_canvas_width-offset, fullscreen_canvas_height-offset)

        # add item to scene
        self.addItem(graphItem)

    @staticmethod
    def __pos_to_str(position):
        return ";".join(map(str, position))

    @staticmethod
    def __str_to_pos(text):
        return list(map(float, text.split(";")))

    @staticmethod
    def __str_to_image(val: str) -> Image:
        img = QImage.fromData(GraphScene.__str_to_q_byte_array(val))
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        img.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        buffer.close()
        # pil_im.thumbnail(size, Image.ANTIALIAS) # keeping aspect ratio
        # pil_im = pil_im.resize((20, 20), Image.Resampling.LANCZOS)
        return pil_im

    @staticmethod
    def __str_to_q_byte_array(val: str) -> QByteArray:
        q_byte_array = QByteArray(val.encode())
        q_byte_array = QByteArray.fromBase64(q_byte_array)
        return q_byte_array

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print('PlotWidget.dropEvent')
        pos = event.pos()
        mimeData = event.mimeData()
        pixMap = QPixmap(mimeData)
        print('dropEvent2')
        # rectItem = QGraphicsRectItem(0, 0, 20, 20)
        # rectItem.setPos(event.pos())
        # self.addItem(rectItem)

        #item = QGraphicsItem()
        newPix = QGraphicsPixmapItem(pixMap)
        # newPix.setPos(event.pos().x(), event.pos().y())

        event.setDropAction(Qt.DropActions.MoveAction)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()