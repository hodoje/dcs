from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem


class HudEnemy(QGraphicsItem):
    def __init__(self, parent, config):
        super().__init__(parent=parent)

        self.config = config
        self.texture = QImage(self.config.hudEnemy)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)
