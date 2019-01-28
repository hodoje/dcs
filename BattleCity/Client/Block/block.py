from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem


class Block(QGraphicsItem):
    def __init__(self, x, y, type, isBaseBlock, allBlockTextures):
        super().__init__()
        self.xCoord = x
        self.yCoord = y
        self.type = type
        self.isBaseBlock = isBaseBlock
        # used for removeBase and upgradeBase effects
        self.isHidden = False
        self.allBlockTextures = allBlockTextures
        self.texture = QImage(self.allBlockTextures[type])
        self.setX(x)
        self.setY(y)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def updateTexture(self):
        self.texture = QImage(self.allBlockTextures[self.type])
