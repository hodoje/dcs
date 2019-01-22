from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem


class Base(QGraphicsItem):
    def __init__(self, aliveImageUrl, deadImageUrl):
        super().__init__()
        self.isAlive = True
        self.aliveImage = QImage(aliveImageUrl)
        self.deadImage = QImage(deadImageUrl)
        self.m_boundingRect = QRectF(0, 0, self.aliveImage.width(), self.aliveImage.height())

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        if self.isAlive:
            QPainter.drawImage(0, 0, self.aliveImage)
        else:
            QPainter.drawImage(0, 0, self.deadImage)

    def destroyBase(self):
        self.isAlive = False
        self.update()
