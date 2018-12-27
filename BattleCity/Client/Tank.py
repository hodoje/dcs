from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsRectItem
from Client.Bullet import Bullet
from Client.DirectionEnum import Direction


class Tank(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.__init_ui__()

    def __init_ui__(self):
        # initial canon direction is up
        self.canonDirection = Direction.UP

    # movement
    def moveRight(self):
        self.setX(self.x() + 5)

    def moveLeft(self):
        self.setX(self.x() - 5)

    def moveDown(self):
        self.setY(self.y() + 5)

    def moveUp(self):
        self.setY(self.y() - 5)

    def updatePosition(self, key):
        # before each move check if move is possible
        if key == Qt.Key_Right:
            if self.pos().x() + self.rect().width() < self.scene().width():
                self.moveRight()
                self.canonDirection = Direction.RIGHT
        elif key == Qt.Key_Left:
            if self.pos().x() > 0:
                self.moveLeft()
                self.canonDirection = Direction.LEFT
        elif key == Qt.Key_Down:
            if self.pos().y() + self.rect().height() < self.scene().height():
                self.moveDown()
                self.canonDirection = Direction.DOWN
        elif key == Qt.Key_Up:
            if self.pos().y() > 0:
                self.moveUp()
                self.canonDirection = Direction.UP

    def fireCanon(self, key):
        if key == Qt.Key_Space:
            # create the bullet
            bullet = Bullet(self.canonDirection)
            # set the bullet in the center of the tank
            if self.canonDirection == Direction.UP or self.canonDirection == Direction.DOWN:
                bullet.setPos(self.x() + self.rect().width() * 0.4, self.y())
            elif self.canonDirection == Direction.LEFT or self.canonDirection == Direction.RIGHT:
                bullet.setPos(self.x(), self.y() + self.rect().height() * 0.4)
            # add the bullet to the scene
            self.scene().addItem(bullet)
