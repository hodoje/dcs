from PyQt5.QtCore import QPoint, QRectF, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsRectItem

from BasicElements.bullet import Bullet
from BasicElements.directionEnum import Direction
from Block.block import Block
from Block.blockTypeEnum import BlockType
from DeusEx.deusex import DeusEx
from Player.canPlayerShootSignalData import CanPlayerShootSignalData


class Player(QGraphicsObject):
    canShootSignal = pyqtSignal(CanPlayerShootSignalData)

    def __init__(self,
                 playerDetails,
                 config,
                 color,
                 firingKey,
                 movementKeys,
                 playerLevels,
                 field,
                 targetType,
                 animationTimer,
                 bulletTimer,
                 killEmitter,
                 playerDeadEmitter,
                 gameOverEmitter):
        super().__init__()
        # only some of the properties from playerDetails are used
        # that are needed for logic of the player
        self.id = playerDetails.id
        self.points = playerDetails.points
        if playerDetails.lives is None:
            self.lives = 2
        else:
            self.lives = playerDetails.lives
        if playerDetails.level is None:
            self.level = 1
        else:
            self.level = playerDetails.level
        self.config = config
        self.color = color
        self.isShielded = False
        self.firingKey = firingKey
        self.movementKeys = movementKeys
        self.playerLevels = playerLevels
        self.field = field
        self.targetType = targetType
        self.animationTimer = animationTimer
        self.bulletTimer = bulletTimer
        self.killEmitter = killEmitter
        self.playerDeadEmitter = playerDeadEmitter
        self.gameOverEmitter = gameOverEmitter
        self.startingPos = None

        # used to determine if the player can shoot
        self.firedBullets = 0

        self.rateOfFire = self.playerLevels[f"star{self.level}"]["rateOfFire"]
        self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]

        # initial cannon direction
        self.canonDirection = Direction.UP

        self.__init_ui__()

        # texture animation
        self.textureTimer = animationTimer
        self.textureTimer.timeout.connect(self.updateUi)

        # sounds
        self.shotSound = QSound(self.config.sounds["playerShot"])

    def __init_ui__(self):
        # set up player textures, refresh rate and transformation origin point
        self.textures = []
        self.textures.append(QImage(f"Resources/Images/Tanks/{self.color}/{self.color}FP.v{self.level}.png"))
        self.textures.append(QImage(f"Resources/Images/Tanks/{self.color}/{self.color}SP.v{self.level}.png"))
        self.currentTexture = 0
        self.height = self.textures[0].height()
        self.width = self.textures[0].width()
        self.shieldTextures = []
        self.shieldTextures.append(QImage(f"Resources/Images/Shield/shield{self.width}FP.png"))
        self.shieldTextures.append(QImage(f"Resources/Images/Shield/shield{self.width}SP.png"))
        self.currentShieldTexture = 0
        self.shieldTimer = QTimer()
        self.shieldTimer.setTimerType(Qt.PreciseTimer)
        self.shieldTimer.setInterval(50)
        self.shieldTimer.timeout.connect(self.shieldUi)
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)
        # setting transform origin point to center of the player so the rotation will be in regard to the center
        self.setTransformOriginPoint(QPoint(self.boundingRect().width() / 2, self.boundingRect().height() / 2))

    # override default bounding rect
    def boundingRect(self):
        return self.m_boundingRect

    # override default paint
    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget):
        QPainter.drawImage(0, 0, self.textures[self.currentTexture])
        if self.isShielded:
            QPainter.drawImage(0, 0, self.shieldTextures[self.currentShieldTexture])

    def updateUi(self):
        self.currentTexture = 1 if self.currentTexture == 0 else 0
        self.update()

    def shieldUi(self):
        self.currentShieldTexture = 1 if self.currentShieldTexture == 0 else 0
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
        if self.firedBullets < self.rateOfFire:
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
                self.shotSound.play()

    def announceCanShoot(self, canShoot):
        # if canShoot is true, that means the bullet is destroyed, decrease fired bullets number and emit it can shoot
        # if canShoot is false, that means the the player fired a bullet, but don't emit the player can shoot
        # immediately but first check if fired bullets reached rate of fire, if reached, emit player cannot shoot
        # else, don't emit anything (which means that the firing notifier will still have canEmit flag set to True)
        if canShoot:
            self.firedBullets -= 1
            self.canShootSignal.emit(CanPlayerShootSignalData(self.id, canShoot))
        else:
            self.firedBullets += 1
            if self.firedBullets == self.rateOfFire:
                self.canShootSignal.emit(CanPlayerShootSignalData(self.id, canShoot))

# will be used for DeusEx and will be wrapped in player wrapper
    def levelUp(self):
        if not self.level == 4:
            self.level += 1
            self.rateOfFire = self.playerLevels[f"star{self.level}"]["rateOfFire"]
            self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]
            self.updateTextures()

    def levelDown(self):
        if self.level != 1:
            self.level -= 1
            self.rateOfFire = self.playerLevels[f"star{self.level}"]["rateOfFire"]
            self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]
            self.updateTextures()

    def resetPlayer(self):
        self.lives -= 1
        if self.lives < 0:
            self.playerDeadEmitter.playerDeadSignal.emit(self.id)
            return
        self.level = 1
        self.rateOfFire = self.playerLevels[f"star{self.level}"]["rateOfFire"]
        self.bulletSpeed = self.playerLevels[f"star{self.level}"]["bulletSpeed"]
        self.updateTextures()
        self.setPos(self.startingPos)

    def updateTextures(self):
        self.__init_ui__()
