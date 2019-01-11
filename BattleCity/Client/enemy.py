from PyQt5.QtCore import QTimer, Qt, QPoint, QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsRectItem

from directionEnum import Direction
from bullet import Bullet

import random


class Enemy(QGraphicsItem):
    def __init__(self, type, color, movementPace, movementSpeed, shootingSpeed, field, movementTimer, bulletTimer, targetType):
        super().__init__()
        self.type = type
        self.color = color
        self.movementSpeed = movementSpeed
        self.shootingSpeed = shootingSpeed
        self.movementPace = movementPace
        self.field = field
        self.directions = [Direction.RIGHT, Direction.LEFT, Direction.DOWN, Direction.UP]
        self.bulletTimer = bulletTimer
        self.targetType = targetType

        # initial cannon direction
        self.canonDirection = Direction.DOWN

        # used to determine if player can shoot
        # initially is true, set to false when a bullet is fired, then set to true after bullet is destroyed
        # will probably be changed in the future
        # NOTE: this flag is NOT necessary to work properly but will stay here for possible future uses
        self.canShoot = True

        self.__init_ui__()

        # set up movement timer
        self.movementTimer = movementTimer
        #self.movementTimer.setTimerType(Qt.PreciseTimer)
        self.movementTimer.timeout.connect(self.randomMovement)
        #self.movementTimer.start(self.movementSpeed)

        # set up shooting timer
        self.shootingTimer = QTimer()
        self.shootingTimer.setTimerType(Qt.PreciseTimer)
        self.shootingTimer.timeout.connect(self.randomShooting)
        #self.shootingTimer.start(self.shootingSpeed)

    def __init_ui__(self):
        # set up player textures, refresh rate and transformation origin point
        self.texture1 = QImage(f"Resources/Images/Tanks/yellow/yellowFP.v1.png")
        self.texture2 = QImage(f"Resources/Images/Tanks/yellow/yellowSP.v1.png")
        self.width = 40
        self.height = 40
        self.textures = [self.texture2, self.texture1]
        self.isFirstTexture = 1
        self.textureTimer = QTimer()
        self.textureTimer.setTimerType(Qt.PreciseTimer)
        self.textureTimer.timeout.connect(self.updateUi)
        self.textureTimer.start(100)
        self.setTransformOriginPoint(QPoint(self.boundingRect().width() / 2, self.boundingRect().height() / 2))
        self.rotate(self.canonDirection)

    def getDirections(self):
        directions = []
        for k in Direction:
            directions.append(k)
        return directions

    # override default bounding rect
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    # override default paint
    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget):
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
        self.setX(self.x() + self.movementPace)

    def moveLeft(self):
        self.setX(self.x() - self.movementPace)

    def moveDown(self):
        self.setY(self.y() + self.movementPace)

    def moveUp(self):
        self.setY(self.y() - self.movementPace)

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

    def canMove(self, direction):
        canMove = True
        allObjects = self.scene().items()
        x1 = self.x()
        y1 = self.y()
        if direction == Direction.RIGHT:
            x1 += 1
        elif direction == Direction.LEFT:
            x1 -= 1
        elif direction == Direction.DOWN:
            y1 += 1
        elif direction == Direction.UP:
            y1 -= 1
        x2 = x1 + self.width
        y2 = y1 + self.height

        for obj in allObjects:
            if type(obj) != QGraphicsRectItem and self != obj:
                objX1 = obj.x()
                objY1 = obj.y()
                objX2 = objX1 + obj.boundingRect().width()
                objY2 = objY1 + obj.boundingRect().height()
                if x1 < objX2 and x2 > objX1 and y1 < objY2 and y2 > objY1:
                    canMove = False
                    break
        return canMove

    # NOTE: magic '-1' for the same reason as on the player
    def updatePosition(self, direction):
        # before each move check if move is possible
        if direction is Direction.RIGHT:
            if self.pos().x() + self.width < self.field.x() + self.field.boundingRect().width() - 1:
                if self.canMove(Direction.RIGHT):
                    self.moveRight()
                    if not self.canonDirection == Direction.RIGHT:
                        self.rotate(Direction.RIGHT)
                    self.canonDirection = Direction.RIGHT
                    return True
                else:
                    return False
            else:
                return False
        elif direction is Direction.LEFT:
            if self.pos().x() > self.field.x():
                if self.canMove(Direction.LEFT):
                    self.moveLeft()
                    if not self.canonDirection == Direction.LEFT:
                        self.rotate(Direction.LEFT)
                    self.canonDirection = Direction.LEFT
                    return True
                else:
                    return False
            else:
                return False
        elif direction is Direction.DOWN:
            if self.pos().y() + self.height < self.field.y() + self.field.boundingRect().height() - 1:
                if self.canMove(Direction.DOWN):
                    self.moveDown()
                    if not self.canonDirection == Direction.DOWN:
                        self.rotate(Direction.DOWN)
                    self.canonDirection = Direction.DOWN
                    return True
                else:
                    return False
            else:
                return False
        elif direction is Direction.UP:
            if self.pos().y() > self.field.y():
                if self.canMove(Direction.UP):
                    self.moveUp()
                    if not self.canonDirection == Direction.UP:
                        self.rotate(Direction.UP)
                    self.canonDirection = Direction.UP
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def shoot(self):
        # create the bullet
        bullet = Bullet(self.canonDirection, self)
        self.announceCanShoot(False)
        # announce that the player can't shoot until the bullet calls this function again
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

    def randomMovement(self):
        if not self.updatePosition(self.canonDirection):
            tempDirections = [direction for direction in self.directions if direction not in [self.canonDirection]]
            nextDirection = random.choice(tempDirections)
            self.canonDirection = nextDirection
            self.rotate(self.canonDirection)

    def randomShooting(self):
        if self.canShoot:
            self.shoot()

    def announceCanShoot(self, canShoot):
        self.canShoot = canShoot
