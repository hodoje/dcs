from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsRectItem


class Block(QGraphicsRectItem):
    def __init__(self, x, y, imagePath):
        super().__init__()
        self.setX(x)
        self.setY(y)
        self.image = QImage(imagePath)

    def boundingRect(self):
        return QRectF(0, 0, self.image.width(), self.image.height())

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.image)
