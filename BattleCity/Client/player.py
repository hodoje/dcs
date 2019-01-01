from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtWidgets import QGraphicsObject

from bullet import Bullet
from directionEnum import Direction


class Player(QGraphicsObject):
    canShootSignal = pyqtSignal(int)

    def __init__(self, color, firingKey, movementKeys):
        super().__init__()
        # set up interaction keys
        self.firingKey = firingKey
        self.movementKeys = movementKeys

        # player color
        self.color = color

        # initial cannon direction
        self.canonDirection = Direction.UP

        # used to determine if player can shoot
        # initially is true, set to false when a bullet is fired, then set to true after bullet is destroyed
        # will probably be changed in the future
        # NOTE: this flag is NOT necessary to work properly but will stay here for possible future uses
        self.canShoot = True

        # initial player that will (hope so) be used in the future
        self.level = 1

        self.__init_ui__()

    def __init_ui__(self):
        # set up player textures, refresh rate and transformation origin point
        self.texture1 = QImage(f"Resources/Images/Tanks/{self.color}/{self.color}FP.v{self.level}.png")
        self.texture2 = QImage(f"Resources/Images/Tanks/{self.color}/{self.color}SP.v{self.level}.png")
        self.textures = [self.texture2, self.texture1]
        self.isFirstTexture = 1
        self.textureTimer = QTimer()
        self.textureTimer.setTimerType(Qt.PreciseTimer)
        self.textureTimer.timeout.connect(self.updateUi)
        self.textureTimer.start(100)
        self.setTransformOriginPoint(QPoint(self.boundingRect().width() / 2, self.boundingRect().height() / 2))

    # override default bounding rect
    def boundingRect(self):
        return QRectF(0, 0, self.texture1.width(), self.texture1.height())

    # override default paint
    def paint(self, QPainter: QPainter, QStyleOptionGraphicsItem, QWidget):
        if self.isFirstTexture:
            QPainter.drawImage(0, 0, self.texture1)
        else:
            QPainter.drawImage(0, 0, self.texture2)

    def updateUi(self):
        self.isFirstTexture = not self.isFirstTexture
        # self.update() will schedule a paint event on the parent QGraphicsView
        # so paint won't execute immediately
        self.update()

    # movements
    def moveRight(self):
        self.setX(self.x() + 5)

    def moveLeft(self):
        self.setX(self.x() - 5)

    def moveDown(self):
        self.setY(self.y() + 5)

    def moveUp(self):
        self.setY(self.y() - 5)

    # rotations
    def rotate(self, nextDirection):
        if nextDirection == Direction.RIGHT:
            self.setRotation(90)
        elif nextDirection == Direction.LEFT:
            self.setRotation(-90)
        elif nextDirection == Direction.DOWN:
            self.setRotation(180)
        elif nextDirection == Direction.UP:
            self.setRotation(0)

    def updatePosition(self, key):
        # before each move check if move is possible
        if key == self.movementKeys["Right"]:
            if self.pos().x() + self.boundingRect().width() < self.scene().width():
                self.moveRight()
                if not self.canonDirection == Direction.RIGHT:
                    self.rotate(Direction.RIGHT)
                self.canonDirection = Direction.RIGHT
        elif key == self.movementKeys["Left"]:
            if self.pos().x() > 0:
                self.moveLeft()
                if not self.canonDirection == Direction.LEFT:
                    self.rotate(Direction.LEFT)
                self.canonDirection = Direction.LEFT
        elif key == self.movementKeys["Down"]:
            if self.pos().y() + self.boundingRect().height() < self.scene().height():
                self.moveDown()
                if not self.canonDirection == Direction.DOWN:
                    self.rotate(Direction.DOWN)
                self.canonDirection = Direction.DOWN
        elif key == self.movementKeys["Up"]:
            if self.pos().y() > 0:
                self.moveUp()
                if not self.canonDirection == Direction.UP:
                    self.rotate(Direction.UP)
                self.canonDirection = Direction.UP

    def fire(self, key):
        if self.canShoot:
            if key == self.firingKey:
                # create the bullet
                bullet = Bullet(self.canonDirection, self)
                # announce that the player can't shoot until the bullet calls this function again
                self.announceCanShoot(False)
                # set the bullet in the center of the tank
                # 0.4 is the 40% aspect ration of the width/height of the tank so the bullet
                # (with its width/height will be in the middle)
                # magic numbers are based on the size of the image itself and the black margin
                # between the image end and the tank object itself in that image
                if self.canonDirection == Direction.UP:
                    bullet.setPos(self.x() + self.boundingRect().width() * 0.4, self.y() - 15)
                elif self.canonDirection == Direction.DOWN:
                    bullet.setPos(self.x() + self.boundingRect().width() * 0.4, self.y() + self.boundingRect().height() + 5)
                elif self.canonDirection == Direction.LEFT:
                    bullet.setPos(self.x() - 15, self.y() + self.boundingRect().height() * 0.4)
                elif self.canonDirection == Direction.RIGHT:
                    bullet.setPos(self.x() + self.boundingRect().width() + 5, self.y() + self.boundingRect().height() * 0.4)
                # add the bullet to the scene
                self.scene().addItem(bullet)

    # this function will signal the board that the player can shoot
    # which will then set up the firing notifier flag that it can emit shooting keys
    # back to the board and the board will call the players fire function
    def announceCanShoot(self, canShoot):
        self.canShoot = canShoot
        self.canShootSignal.emit(canShoot)
