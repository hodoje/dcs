from PyQt5.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem
from bullet import Bullet
from directionEnum import Direction


class Player(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        self.canonDirection = Direction.UP
        self.m_boundingRect = QRectF(0, 0, 40.0, 40.0)
        self.__init_ui__()

    def __init_ui__(self):
        # set up player textures and refresh rate
        self.texture1 = QPixmap("Resources/Images/yellowFP.v8.png")
        self.texture2 = QPixmap("Resources/Images/yellowSP.v8.png")
        self.textures = [self.texture2, self.texture1]
        self.isFirstTexture = True
        self.textureTimer = QTimer()
        self.textureTimer.timeout.connect(self.updateUi)
        self.textureTimer.start(100)

        self.setPixmap(self.texture1)
        self.setTransformOriginPoint(QPoint(self.boundingRect().width() / 2, self.boundingRect().height() / 2))

    # override default bounding rect
    def boundingRect(self):
        return self.m_boundingRect

    def updateUi(self):
        self.setPixmap(self.textures[self.isFirstTexture])
        self.isFirstTexture = ~self.isFirstTexture

    # movement
    def moveRight(self):
        self.setX(self.x() + 5)

    def moveLeft(self):
        self.setX(self.x() - 5)

    def moveDown(self):
        self.setY(self.y() + 5)

    def moveUp(self):
        self.setY(self.y() - 5)

    # rotate to a direction
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
        if key == Qt.Key_Right:
            if self.pos().x() + self.boundingRect().width() < self.scene().width():
                self.moveRight()
                if not self.canonDirection == Direction.RIGHT:
                    self.rotate(Direction.RIGHT)
                self.canonDirection = Direction.RIGHT
        elif key == Qt.Key_Left:
            if self.pos().x() > 0:
                self.moveLeft()
                if not self.canonDirection == Direction.LEFT:
                    self.rotate(Direction.LEFT)
                self.canonDirection = Direction.LEFT
        elif key == Qt.Key_Down:
            if self.pos().y() + self.boundingRect().height() < self.scene().height():
                self.moveDown()
                if not self.canonDirection == Direction.DOWN:
                    self.rotate(Direction.DOWN)
                self.canonDirection = Direction.DOWN
        elif key == Qt.Key_Up:
            if self.pos().y() > 0:
                self.moveUp()
                if not self.canonDirection == Direction.UP:
                    self.rotate(Direction.UP)
                self.canonDirection = Direction.UP

    def fireCanon(self, key):
        if key == Qt.Key_Space:
            # create the bullet
            bullet = Bullet(self.canonDirection)
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
