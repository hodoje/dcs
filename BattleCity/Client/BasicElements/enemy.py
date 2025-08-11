from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem

import random

from BasicElements.bullet import Bullet
from BasicElements.directionEnum import Direction
from Block.block import Block
from Block.blockTypeEnum import BlockType
from DeusEx.deusex import DeusEx


class Enemy(QGraphicsItem):
    def __init__(self,
                 tankId,
                 tankDetails,
                 isFlashing,
                 color,
                 field,
                 movementTimer,
                 shootingTimer,
                 animationTimer,
                 bulletTimer,
                 targetType,
                 killEmitter,
                 gameOverEmitter):
        super().__init__()
        self.id = tankId
        self.tankDetails = tankDetails
        self.isFlashing = isFlashing
        self.color = color
        self.field = field
        self.directions = [Direction.RIGHT, Direction.LEFT, Direction.DOWN, Direction.UP]
        self.movementTimer = movementTimer
        self.shootingTimer = shootingTimer
        self.textureTimer = animationTimer
        # these properties get sent to Bullet objects
        self.bulletTimer = bulletTimer
        self.targetType = targetType
        self.killEmitter = killEmitter
        self.gameOverEmitter = gameOverEmitter
        self.bulletSpeed = self.tankDetails.bulletSpeed

        # initial cannon direction
        self.canonDirection = Direction.DOWN

        # used to determine if player can shoot
        # initially is true, set to false when a bullet is fired, then set to true after bullet is destroyed
        # will probably be changed in the future
        # NOTE: this flag is NOT necessary to work properly but will stay here for possible future uses
        self.canShoot = True

        self.__init_ui__()

        # TIMERS
        # set up animation timer
        self.textureTimer.timeout.connect(self.updateUi)
        # set up movement timer
        self.movementTimer.timeout.connect(self.randomMovement)
        # set up shooting timer
        self.shootingTimer.timeout.connect(self.randomShooting)

    def __init_ui__(self):
        # set up player textures, refresh rate and transformation origin point
        self.textures = []
        self.textures.append(QImage(f"Resources/Images/Tanks/{self.color}/{self.color}FP.v{self.tankDetails.tankType}.png"))
        self.textures.append(QImage(f"Resources/Images/Tanks/{self.color}/{self.color}SP.v{self.tankDetails.tankType}.png"))
        if self.isFlashing:
            self.textures.append(QImage(f"Resources/Images/Tanks/red/redFP.v{self.tankDetails.tankType}.png"))
            self.textures.append(QImage(f"Resources/Images/Tanks/red/redSP.v{self.tankDetails.tankType}.png"))
        self.currentTexture = 0
        self.width = self.textures[0].width()
        self.height = self.textures[0].height()
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)
        self.setTransformOriginPoint(QPoint(int(self.boundingRect().width() / 2), int(self.boundingRect().height() / 2)))
        self.rotate(self.canonDirection)

    # override default bounding rect
    def boundingRect(self):
        return self.m_boundingRect

    # override default paint
    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget):
        QPainter.drawImage(0, 0, self.textures[self.currentTexture])


    def updateUi(self):
        self.currentTexture += 1
        if self.currentTexture == len(self.textures):
            self.currentTexture = 0
        # self.update() will schedule a paint event on the parent QGraphicsView
        # so paint won't execute immediately but if i expect correctly when the
        # QGraphicsView.viewport.repaint is called (<- NOTE about this line: that's not how to force the repaint)
        self.update()

    # movements
    def moveRight(self):
        self.setX(self.x() + 1)

    def moveLeft(self):
        self.setX(self.x() - 1)

    def moveDown(self):
        self.setY(self.y() + 1)

    def moveUp(self):
        self.setY(self.y() - 1)

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
            # don't camper to self and field
            oType = type(obj)
            if self != obj and oType != QGraphicsRectItem:
                if type(obj) == Block:
                    # omit bushes and ice
                    if obj.type == BlockType.bush or obj.type == BlockType.ice:
                        continue
                if type(obj) == DeusEx:
                    continue
                objParent = obj.parentItem()
                objX1 = 0
                objY1 = 0
                if objParent is None:
                    objX1 = obj.x()
                    objY1 = obj.y()
                else:
                    objSceneCoords = obj.mapToScene(obj.pos())
                    objX1 = objSceneCoords.x()
                    objY1 = objSceneCoords.y()
                objX2 = objX1 + obj.boundingRect().width()
                objY2 = objY1 + obj.boundingRect().height()
                if x1 < objX2 and x2 > objX1 and y1 < objY2 and y2 > objY1:
                    canMove = False
                    break
        return canMove

    # NOTE: magic '-1' for the same reason as on the player
    def updatePosition(self, direction):
        # before each move check if move is possible
        if direction == Direction.RIGHT:
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
        elif direction == Direction.LEFT:
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
        elif direction == Direction.DOWN:
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
        elif direction == Direction.UP:
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
        # announce that the enemy can't shoot until the bullet calls this function again
        self.announceCanShoot(False)
        # set the bullet in the center of the tank
        # 0.37 is the 37% aspect ration of the width/height of the tank so the bullet
        # (with its width/height will be in the middle)
        # magic numbers are based on the size of the image itself and the black margin
        # between the image's end and the tank object itself in that image
        if self.canonDirection == Direction.UP:
            bullet.setPos(self.x() + self.boundingRect().width() * 0.37, self.y() - 15)
        elif self.canonDirection == Direction.DOWN:
            bullet.setPos(self.x() + self.boundingRect().width() * 0.37, self.y() + self.boundingRect().height() + 5)
        elif self.canonDirection == Direction.LEFT:
            bullet.setPos(self.x() - 15, self.y() + self.boundingRect().height() * 0.37)
        elif self.canonDirection == Direction.RIGHT:
            bullet.setPos(self.x() + self.boundingRect().width() + 5, self.y() + self.boundingRect().height() * 0.37)
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
