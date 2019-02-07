from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem


class HudHiscoreNumber(QGraphicsItem):
    def __init__(self, parent, color, initialNumber, config):
        super().__init__(parent=parent)
        self.number = initialNumber
        self.color = color
        self.config = config
        self.textures = []
        for i in range(10):
            self.textures.append(QImage(self.config.hiscoreNumbers[self.color][f"number{i}"]))
        self.width = self.textures[0].width()
        self.height = self.textures[0].height()
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.textures[self.number])

    def updateNumber(self, number):
        self.number = number
        self.update()
