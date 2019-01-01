from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from Client.directionEnum import Direction


class Bullet(QGraphicsPixmapItem):
    def __init__(self, movingDirection, player):
        super().__init__()
        # moving direction determines what picture is used for the bullet
        self.movingDirection = movingDirection
        # reference to a player so a bullet can call player.announceCanShoot function
        # to signal that will signal the board that the player can shoot again
        self.player = player

        # call 'move' every 50ms
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.move)
        self.timer.start(10)

        self.__init_ui__()

    def __init_ui__(self):
        # draw the bullet based on direction
        if self.movingDirection == Direction.RIGHT:
            self.setPixmap(QPixmap("Resources/Images/Bullets/bulletRight.png"))
        elif self.movingDirection == Direction.LEFT:
            self.setPixmap(QPixmap("Resources/Images/Bullets/bulletLeft.png"))
        elif self.movingDirection == Direction.DOWN:
            self.setPixmap(QPixmap("Resources/Images/Bullets/bulletDown.png"))
        elif self.movingDirection == Direction.UP:
            self.setPixmap(QPixmap("Resources/Images/Bullets/bulletUp.png"))

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
                self.player.announceCanShoot(True)
                del self
        elif self.movingDirection == Direction.LEFT:
            if self.pos().x() + self.boundingRect().width() < 0:
                self.scene().removeItem(self)
                self.player.announceCanShoot(True)
                del self
        elif self.movingDirection == Direction.DOWN:
            if self.pos().y() > self.scene().height():
                self.scene().removeItem(self)
                self.player.announceCanShoot(True)
                del self
        elif self.movingDirection == Direction.UP:
            if self.pos().y() + self.boundingRect().height() < 0:
                self.scene().removeItem(self)
                self.player.announceCanShoot(True)
                del self
