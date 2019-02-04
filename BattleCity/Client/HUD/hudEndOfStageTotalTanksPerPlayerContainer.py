from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudEndOfStageTotalTanksPerPlayerContainer(QGraphicsItem):
    def __init__(self, config, totalTanksPerPlayer):
        super().__init__()

        self.config = config
        self.totalTanksPerPlayer = totalTanksPerPlayer
        self.texture = QImage(self.config.endOfStageTotalTanksContainer)
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        # handles only numbers from 0 to 99
        self.digits = []
        for i in range(2):
            self.digits.append(i)
        self.extractDigitsFromTotalTanksPerPlayer()
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

    def extractDigitsFromTotalTanksPerPlayer(self):
        number_string = str(self.totalTanksPerPlayer).zfill(len(self.digits))
        for idx, string_digit in enumerate(number_string):
            self.digits[idx] = int(string_digit)

    def updateTotalTanksPerPlayer(self, totalTanksPerPlayer=None):
        if totalTanksPerPlayer is not None:
            self.totalTanksPerPlayer = totalTanksPerPlayer
        self.extractDigitsFromTotalTanksPerPlayer()
        for i in range(len(self.digits)):
            self.numbers[i].updateNumber(self.digits[i])
