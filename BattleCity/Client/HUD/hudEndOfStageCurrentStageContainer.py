from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudEndOfStageCurrentStageContainer(QGraphicsItem):
    def __init__(self, config, currentStage):
        super().__init__()
        self.config = config
        self.currentStage = currentStage
        self.texture = QImage(self.config.endOfStageCurrentStageContainer)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        self.digits = []
        for i in range(2):
            self.digits.append(i)
        self.extractDigitsFromCurrentStage()
        self.numbers = []
        for i in range(len(self.digits)):
            number = HudNumber(self,
                               self.config.numberColors["white"],
                               self.config.numberSize["big"],
                               self.digits[i],
                               self.config)
            number.setPos(self.x() + i * number.width, self.y())
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
