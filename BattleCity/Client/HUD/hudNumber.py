from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem


class HudNumber(QGraphicsItem):
    def __init__(self, parent, initialNumber, config):
        super().__init__(parent=parent)

        self.number = initialNumber
        self.config = config
        self.texture = QImage(self.config.numbers[f"number{self.number}"])
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def updateNumber(self, number):
        self.number = number
        self.texture = QImage(self.config.numbers[f"number{self.number}"])
