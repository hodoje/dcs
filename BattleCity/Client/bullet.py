from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from directionEnum import Direction
from killEmitter import KillEmitData
from block import Block
from blockTypeEnum import BlockType
from base import Base

import sip


class Bullet(QGraphicsPixmapItem):
    def __init__(self, movingDirection, owner):
        super().__init__()
        # moving direction determines what picture is used for the bullet
        self.movingDirection = movingDirection
        # reference to a player so a bullet can call player.announceCanShoot function
        # to signal that will signal the board that the player can shoot again
        self.owner = owner

        # movement timer
        self.timer = self.owner.bulletTimer
        self.timer.timeout.connect(self.move)

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
        self.setPos(self.x() + self.owner.bulletSpeed, self.y())

    def moveLeft(self):
        self.setPos(self.x() - self.owner.bulletSpeed, self.y())

    def moveDown(self):
        self.setPos(self.x(), self.y() + self.owner.bulletSpeed)

    def moveUp(self):
        self.setPos(self.x(), self.y() - self.owner.bulletSpeed)

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
            if self.pos().x() > self.owner.field.x() + self.owner.field.boundingRect().width():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        # react only if it's an owners targetType or a Bullet
                        if oType == self.owner.targetType or oType == Bullet or oType == Block or oType == Base:
                            # remove the object and do additional job according to the object type
                            if oType == self.owner.targetType:
                                # if it's a target then emit a kill
                                killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                                self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                                # remove the bullet
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Bullet:
                                # if it's a bullet tell the other side that it can shoot
                                self.scene().removeItem(obj)
                                obj.owner.announceCanShoot(True)
                                # remove the bullet
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Block:
                                # handle different types of blocks
                                if obj.type == BlockType.brick:
                                    self.scene().removeItem(obj)
                                    del obj
                                    # remove the bullet
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                                elif obj.type == BlockType.steel:
                                    # remove the bullet
                                    if type(self.owner).__name__ == "Player":
                                        if self.owner.level in [3, 4]:
                                            self.scene().removeItem(obj)
                                            del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                                else:
                                    pass
                            elif oType == Base:
                                self.owner.gameOverEmitter.gameOverSignal.emit(1)
                            return
        elif self.movingDirection == Direction.LEFT:
            if self.pos().x() + self.boundingRect().width() < self.owner.field.x():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet or oType == Block or oType == Base:
                            if oType == self.owner.targetType:
                                killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                                self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Bullet:
                                self.scene().removeItem(obj)
                                obj.owner.announceCanShoot(True)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Block:
                                if obj.type == BlockType.brick:
                                    self.scene().removeItem(obj)
                                    sip.delete(obj)
                                    del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                                elif obj.type == BlockType.steel:
                                    if type(self.owner).__name__ == "Player":
                                        if self.owner.level in [3, 4]:
                                            self.scene().removeItem(obj)
                                            del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                            elif oType == Base:
                                self.owner.gameOverEmitter.gameOverSignal.emit(1)
                            return
        elif self.movingDirection == Direction.DOWN:
            if self.pos().y() > self.owner.field.y() + self.owner.field.boundingRect().height():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet or oType == Block or oType == Base:
                            if oType == self.owner.targetType:
                                killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                                self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Bullet:
                                self.scene().removeItem(obj)
                                obj.owner.announceCanShoot(True)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Block:
                                if obj.type == BlockType.brick:
                                    self.scene().removeItem(obj)
                                    sip.delete(obj)
                                    del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                                elif obj.type == BlockType.steel:
                                    if type(self.owner).__name__ == "Player":
                                        if self.owner.level in [3, 4]:
                                            self.scene().removeItem(obj)
                                            del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                            elif oType == Base:
                                self.owner.gameOverEmitter.gameOverSignal.emit(1)
                            return
        elif self.movingDirection == Direction.UP:
            if self.pos().y() + self.boundingRect().height() < self.owner.field.y():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet or oType == Block or oType == Base:
                            if oType == self.owner.targetType:
                                killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                                self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Bullet:
                                self.scene().removeItem(obj)
                                obj.owner.announceCanShoot(True)
                                self.scene().removeItem(self)
                                self.owner.announceCanShoot(True)
                                sip.delete(self)
                                del self
                            elif oType == Block:
                                if obj.type == BlockType.brick:
                                    self.scene().removeItem(obj)
                                    del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                                elif obj.type == BlockType.steel:
                                    if type(self.owner).__name__ == "Player":
                                        if self.owner.level in [3, 4]:
                                            self.scene().removeItem(obj)
                                            del obj
                                    self.scene().removeItem(self)
                                    self.owner.announceCanShoot(True)
                                    sip.delete(self)
                                    del self
                            elif oType == Base:
                                self.owner.gameOverEmitter.gameOverSignal.emit(1)
                            return
