from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudEndOfStageSeparateTankCount(QGraphicsItem):
    def __init__(self, config, count):
        super().__init__()
        self.config = config
        self.currentCount = 0
        self.count = count
        self.texture = QImage(self.config.endStageTanksPerPlayerCounterContainer)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        self.digits = []
        for i in range(2):
            self.digits.append(i)
        self.extractDigitsFromCurrentCount()
        self.numbers = []
        for i in range(len(self.digits)):
            number = HudNumber(self,
                               self.config.numberColors["white"],
                               self.config.numberSize["big"],
                               self.digits[i],
                               self.config)
            number.setPos(self.x() + i * number.width, self.y())
            self.numbers.append(number)
        self.m_boundingRect = QRectF(0, 0, self.numbers[0].width, self.numbers[0].height)

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def extractDigitsFromCurrentCount(self):
        number_string = str(self.currentCount).zfill(len(self.digits))
        for idx, string_digit in enumerate(number_string):
            self.digits[idx] = int(string_digit)

    def updateCurrentCount(self, currentCount=None):
        if currentCount is not None:
            self.currentCount = currentCount
        self.extractDigitsFromCurrentCount()
        for i in range(len(self.digits)):
            self.numbers[i].updateNumber(self.digits[i])

    def updateCount(self, count):
        self.currentCount = 0
        self.count = count
