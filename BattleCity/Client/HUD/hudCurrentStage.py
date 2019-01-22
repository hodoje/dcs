from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudCurrentStage(QGraphicsItem):
    def __init__(self, config, currentStage):
        super().__init__()

        self.config = config
        self.currentStage = currentStage
        self.texture = QImage(self.config.currentStageTexture)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        # handles only numbers from 0 to 99
        self.firstDigit = None
        self.secondDigit = None
        self.extractDigitsFromCurrentStage()
        self.firstNumber = HudNumber(self, self.firstDigit, self.config)
        self.firstNumber.setPos(self.x(), self.y() + 2 * self.texture.height() // 3)
        self.secondNumber = HudNumber(self, self.secondDigit, self.config)
        self.secondNumber.setPos(self.x() + self.texture.width() // 2, self.y() + 2 * self.texture.height() // 3)

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def extractDigitsFromCurrentStage(self):
        if self.currentStage < 10:
            self.firstDigit = 0
            self.secondDigit = self.currentStage
        else:
            number_string = str(self.currentStage)
            self.firstDigit = int(number_string[0])
            self.secondDigit = int(number_string[1])
