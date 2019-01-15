from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsObject


class GameOver(QGraphicsObject):
    def __init__(self, imageUrl):
        super().__init__()
        self.image = QImage(imageUrl)
        self.m_boundingRect = QRectF(0, 0, self.image.width(), self.image.height())

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.image)
