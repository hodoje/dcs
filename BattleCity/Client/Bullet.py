from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from Client.directionEnum import Direction


class Bullet(QGraphicsPixmapItem):
    def __init__(self, movingDirection):
        super().__init__()
        self.movingDirection = movingDirection
        self.__init_ui__()
        # call 'move' every 50ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.move)
        self.timer.start(10)

    def __init_ui__(self):
        # draw the bullet
        if self.movingDirection == Direction.RIGHT:
            self.setPixmap(QPixmap("Resources/Images/bulletRight.png"))
        elif self.movingDirection == Direction.LEFT:
            self.setPixmap(QPixmap("Resources/Images/bulletLeft.png"))
        elif self.movingDirection == Direction.DOWN:
            self.setPixmap(QPixmap("Resources/Images/bulletDown.png"))
        elif self.movingDirection == Direction.UP:
            self.setPixmap(QPixmap("Resources/Images/bulletUp.png"))

    # movements
    def moveRight(self):
        self.setPos(self.x() + 2, self.y())

    def moveLeft(self):
        self.setPos(self.x() - 2, self.y())

    def moveDown(self):
        self.setPos(self.x(), self.y() + 2)

    def moveUp(self):
        self.setPos(self.x(), self.y() - 2)

    # call particular move
    def move(self):
        # set movement
        if self.movingDirection == Direction.RIGHT:
            self.moveRight()
        elif self.movingDirection == Direction.LEFT:
            self.moveLeft()
        elif self.movingDirection == Direction.DOWN:
            self.moveDown()
        elif self.movingDirection == Direction.UP:
            self.moveUp()

        # delete the bullet after it goes of the scene
        # NOTE the different shape of the bullet based on the direction
        if self.movingDirection == Direction.RIGHT:
            if self.pos().x() > self.scene().width():
                self.scene().removeItem(self)
                del self
                print("delete right")
        elif self.movingDirection == Direction.LEFT:
            if self.pos().x() + self.boundingRect().width() < 0:
                self.scene().removeItem(self)
                del self
                print("delete left")
        elif self.movingDirection == Direction.DOWN:
            if self.pos().y() > self.scene().height():
                self.scene().removeItem(self)
                del self
                print("delete down")
        elif self.movingDirection == Direction.UP:
            if self.pos().y() + self.boundingRect().height() < 0:
                self.scene().removeItem(self)
                del self
                print("delete up")