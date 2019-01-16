from PyQt5.QtCore import pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsRectItem

from directionEnum import Direction
from bullet import Bullet
from block import Block
from blockTypeEnum import BlockType


class CanShootSignalData:
    def __init__(self, playerId, canEmit):
        self.playerId = playerId
        self.canEmit = canEmit


class Player(QGraphicsObject):
    canShootSignal = pyqtSignal(CanShootSignalData)

    def __init__(self,
                 id,
                 color,
                 playerLevels,
                 firingKey,
                 movementKeys,
                 field,
                 killEmitter,
                 bulletTimer,
                 targetType,
                 animationTimer,
                 gameOverEmitter,
                 playerDeadEmitter):
        super().__init__()
        self.id = id
        self.color = color
        self.playerLevels = playerLevels
        self.firingKey = firingKey
        self.movementKeys = movementKeys
        self.field = field
        self.killEmitter = killEmitter
        self.gameOverEmitter = gameOverEmitter
        self.bulletTimer = bulletTimer
        self.targetType = targetType
        self.playerDeadEmitter = playerDeadEmitter
        self.startingPos = None
        self.lives = 2

        # initial player stats
        self.points = 0
        self.level = 4
        self.health = self.playerLevels[f"star{self.level}"]["health"]
        self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]

        # initial cannon direction
        self.canonDirection = Direction.UP

        # used to determine if player can shoot
        # initially is true, set to false when a bullet is fired, then set to true after bullet is destroyed
        # will probably be changed in the future
        # NOTE: this flag is NOT necessary to work properly but will stay here for possible future uses
        self.canShoot = True

        self.__init_ui__()

        self.textureTimer = animationTimer
        self.textureTimer.timeout.connect(self.updateUi)

    def __init_ui__(self):
        # set up player textures, refresh rate and transformation origin point
        # textures are .png images 40px x 40px
        self.texture1 = QImage(f"Resources/Images/Tanks/{self.color}/{self.color}FP.v{self.level}.png")
        self.texture2 = QImage(f"Resources/Images/Tanks/{self.color}/{self.color}SP.v{self.level}.png")
        self.height = self.texture1.height()
        self.width = self.texture1.width()
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)
        self.textures = [self.texture2, self.texture1]
        self.isFirstTexture = 1
        self.setTransformOriginPoint(QPoint(self.boundingRect().width() / 2, self.boundingRect().height() / 2))

    # override default bounding rect
    def boundingRect(self):
        return self.m_boundingRect

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

    def levelUp(self):
        if not self.level == 4:
            self.level += 1
            self.health = self.playerLevels[f"star{self.level}"]["health"]
            self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]
            self.updateTextures()

    def levelDown(self):
        self.level -= 1
        # if it was first level now will be 0, and if it was second now will be first, so in both cases, player is dead
        if self.level in [0, 1]:
            self.lives -= 1
            if self.lives == 0:
                self.playerDeadEmitter.playerDeadSignal.emit(self.id)
                return
            self.setPos(self.startingPos)
        else:
            self.health = self.playerLevels[f"star{self.level}"]["health"]
            self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]
            self.updateTextures()

    def updateTextures(self):
        self.__init_ui__()


    # movements
    def moveRight(self):
        self.setX(self.x() + 1)

    def moveLeft(self):
        self.setX(self.x() - 1)

    def moveDown(self):
        self.setY(self.y() + 1)

    def moveUp(self):
        self.setY(self.y() - 1)

    # rotations, absolute degrees
    def rotate(self, direction):
        if direction == Direction.RIGHT:
            self.setRotation(90)
        elif direction == Direction.LEFT:
            self.setRotation(-90)
        elif direction == Direction.DOWN:
            self.setRotation(180)
        elif direction == Direction.UP:
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
                objX1 = obj.x()
                objY1 = obj.y()
                objX2 = objX1 + obj.boundingRect().width()
                objY2 = objY1 + obj.boundingRect().height()
                if x1 < objX2 and x2 > objX1 and y1 < objY2 and y2 > objY1:
                    canMove = False
                    break
        return canMove

    # NOTE: on 'Right' and 'Down' you will notice that there is a magic '-1'
    # it's there because there is some reason the bounding rect of the field will be
    # one pixel larger than the defined size
    def updatePosition(self, key):
        # before each move check if move is possible
        if key == self.movementKeys["Right"]:
            # check if the element is on the edge of the field
            if self.pos().x() + self.width < self.field.x() + self.field.boundingRect().width() - 1:
                if self.canMove(Direction.RIGHT):
                    # else move in the desired direction
                    self.moveRight()
            # check if the canon is facing the desired direction
            # if not, rotate to it and set the direction
            if not self.canonDirection == Direction.RIGHT:
                self.rotate(Direction.RIGHT)
            self.canonDirection = Direction.RIGHT
        elif key == self.movementKeys["Left"]:
            if self.pos().x() > self.field.x():
                if self.canMove(Direction.LEFT):
                    self.moveLeft()
            if not self.canonDirection == Direction.LEFT:
                self.rotate(Direction.LEFT)
            self.canonDirection = Direction.LEFT
        elif key == self.movementKeys["Down"]:
            if self.pos().y() + self.height < self.field.y() + self.field.boundingRect().height() - 1:
                if self.canMove(Direction.DOWN):
                    self.moveDown()
            if not self.canonDirection == Direction.DOWN:
                self.rotate(Direction.DOWN)
            self.canonDirection = Direction.DOWN
        elif key == self.movementKeys["Up"]:
            if self.pos().y() > self.field.y():
                if self.canMove(Direction.UP):
                    self.moveUp()
            if not self.canonDirection == Direction.UP:
                self.rotate(Direction.UP)
            self.canonDirection = Direction.UP

    def shoot(self, key):
        if self.canShoot:
            if key == self.firingKey:
                # create the bullet
                bullet = Bullet(self.canonDirection, self)
                # announce that the player can't shoot until the bullet calls this function again
                self.announceCanShoot(False)
                # set the bullet in the center of the tank
                # 0.37 is the 37% aspect ration of the width/height of the tank so the bullet
                # (with its width/height will be in the middle)
                # magic numbers are based on the size of the image itself and the black margin
                # between the image end and the tank object itself in that image
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

    # this function will signal the board that the player can shoot
    # which will then set up the firing notifier flag that it can emit shooting keys
    # back to the board and the board will call the players fire function
    def announceCanShoot(self, canShoot):
        self.canShoot = canShoot
        self.canShootSignal.emit(CanShootSignalData(self.id, canShoot))
