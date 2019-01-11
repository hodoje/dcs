from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsRectItem


class Block(QGraphicsRectItem):
    def __init__(self, x, y, type, imagePath):
        super().__init__()
        self.xCoord = x
        self.yCoord = y
        self.type = type
        self.texture = QImage(imagePath)
        self.setX(x)
        self.setY(y)

    def boundingRect(self):
        return QRectF(0, 0, self.texture.width(), self.texture.height())

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)
