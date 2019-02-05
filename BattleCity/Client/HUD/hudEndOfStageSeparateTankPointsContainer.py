from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudEndOfStageSeparateTankPointsContainer(QGraphicsItem):
    def __init__(self, config, tankDetails):
        super().__init__()
        self.config = config
        self.currentPoints = 0
        self.pointsStep = tankDetails["pointsStep"]
        self.texture = QImage(self.config.endOfStageSeparateTankPointsContainer)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        self.digits = []
        for i in range(4):
            self.digits.append(i)
        self.extractDigitsFromPlayerPoints()
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

    def extractDigitsFromPlayerPoints(self):
        number_string = str(self.currentPoints).zfill(len(self.digits))
        for idx, string_digit in enumerate(number_string):
            self.digits[idx] = int(string_digit)

    def updatePlayerPoints(self):
        self.extractDigitsFromPlayerPoints()
        for i in range(len(self.digits)):
            self.numbers[i].updateNumber(self.digits[i])

    def updateTankDetails(self, tankDetails):
        self.currentPoints = 0
        self.pointsStep = tankDetails["pointsStep"]

    def reset(self):
        self.currentPoints = 0
        self.pointsStep = 0
        self.updatePlayerPoints()
