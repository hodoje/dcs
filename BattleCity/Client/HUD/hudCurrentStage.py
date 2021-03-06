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
        self.digits = []
        for i in range(2):
            self.digits.append(i)
        self.extractDigitsFromCurrentStage()
        self.numbers = []
        for i in range(len(self.digits)):
            number = HudNumber(self,
                               self.config.numberColors["black"],
                               self.config.numberSize["small"],
                               self.digits[i],
                               self.config)
            number.setPos(self.x() + i * number.width, self.y() + 2 * self.texture.height() // 3)
            self.numbers.append(number)

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def extractDigitsFromCurrentStage(self):
        number_string = str(self.currentStage).zfill(len(self.digits))
        for idx, string_digit in enumerate(number_string):
            self.digits[idx] = int(string_digit)

    def updateStage(self, nextStage=None):
        if nextStage is not None:
            self.currentStage = nextStage
        self.extractDigitsFromCurrentStage()
        for i in range(len(self.digits)):
            self.numbers[i].updateNumber(self.digits[i])
