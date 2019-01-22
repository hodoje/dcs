from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem

from HUD.hudNumber import HudNumber


class HudPlayerLives(QGraphicsItem):
    def __init__(self, playerNum, config, initialLives):
        super().__init__()

        self.playerNum = playerNum
        self.config = config
        self.lives = initialLives
        self.texture = QImage(self.config.playersLives[f"player{self.playerNum}"])
        self.m_boundingRect = QRectF(0, 0, self.texture.width(), self.texture.height())
        self.firstDigit = None
        self.secondDigit = None
        self.extractDigits(self.lives)
        self.firstNumber = HudNumber(self, self.firstDigit, self.config)
        self.firstNumber.setPos(self.x() + self.texture.width() // 3, self.y() + self.texture.height() // 2)
        self.secondNumber = HudNumber(self, self.secondDigit, self.config)
        self.secondNumber.setPos(self.x() + 2 * self.texture.width() // 3, self.y() + self.texture.height() // 2)

    def boundingRect(self):
        return self.m_boundingRect

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        QPainter.drawImage(0, 0, self.texture)

    def extractDigits(self, lives):
        if lives < 10:
            self.firstDigit = 0
            self.secondDigit = lives
        else:
            number_string = str(lives)
            self.firstDigit = int(number_string[0])
            self.secondDigit = int(number_string[1])

    def updateLives(self, lives):
        self.extractDigits(lives)
        self.firstNumber.updateNumber(self.firstDigit)
        self.secondNumber.updateNumber(self.secondDigit)
        self.update()
