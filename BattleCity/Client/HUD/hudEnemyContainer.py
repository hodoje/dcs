from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudEnemy import HudEnemy


class HudEnemyContainer(QGraphicsItem):
    def __init__(self, config):
        super().__init__()

        self.config = config
        self.texture = QImage(self.config.hudEnemyContainer)
        self.width = self.config.hudEnemyContainerWidth
        self.height = self.config.hudEnemyContainerHeight
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)
        self.enemies = []
        self.setUpContainer()

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def setUpContainer(self):
        for i in range(10):
            hudEnemy1 = HudEnemy(self, self.config)
            hudEnemy2 = HudEnemy(self, self.config)
            hudEnemy1.setX(0)
            hudEnemy1.setY(0 + i * hudEnemy1.m_boundingRect.height())
            hudEnemy2.setX(2 + hudEnemy2.m_boundingRect.width())
            hudEnemy2.setY(0 + i * hudEnemy2.m_boundingRect.height())
            self.enemies.append(hudEnemy1)
            self.enemies.append(hudEnemy2)

    def removeEnemy(self):
        return self.enemies.pop(len(self.enemies) - 1)
