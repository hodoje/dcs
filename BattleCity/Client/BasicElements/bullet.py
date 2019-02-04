from PyQt5 import sip
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from Block.base import Base
from BasicElements.directionEnum import Direction
from Block.block import Block
from Block.blockTypeEnum import BlockType
from Emitters.killEmitData import KillEmitData


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
                self.owner.announceCanShoot(True)
                # remove the bullet from the scene and delete call the c++ destructor
                self.scene().removeItem(self)
                sip.delete(self)
                del self
            else:
                self.checkForCollidingItems()
        elif self.movingDirection == Direction.LEFT:
            if self.pos().x() + self.boundingRect().width() < self.owner.field.x():
                self.owner.announceCanShoot(True)
                self.scene().removeItem(self)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                self.checkForCollidingItems()
        elif self.movingDirection == Direction.DOWN:
            if self.pos().y() > self.owner.field.y() + self.owner.field.boundingRect().height():
                self.owner.announceCanShoot(True)
                self.scene().removeItem(self)
                sip.delete(self)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                self.checkForCollidingItems()
        elif self.movingDirection == Direction.UP:
            if self.pos().y() + self.boundingRect().height() < self.owner.field.y():
                self.owner.announceCanShoot(True)
                self.scene().removeItem(self)
                sip.delete(self)
                del self
            else:
                self.checkForCollidingItems()

    def checkForCollidingItems(self):
        collidingItems = self.collidingItems()
        if len(collidingItems) > 1:
            for obj in collidingItems:
                oType = type(obj)
                # react only if it's an owners targetType or a Bullet
                if oType == self.owner.targetType or oType == Bullet or oType == Block or oType == Base:
                    # remove the object and do additional job according to the object type
                    if oType == self.owner.targetType:
                        # if it's a target and it's not shielded then emit a kill
                        if hasattr(obj, "isShielded"):
                            if not obj.isShielded:
                                killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                                self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                        else:
                            killEmitData = KillEmitData(self.owner.id, obj.id, oType)
                            self.owner.killEmitter.emitKillSignal.emit(killEmitData)
                        # remove the bullet
                        self.scene().removeItem(self)
                        self.owner.announceCanShoot(True)
                        sip.delete(self)
                        del self
                    elif oType == Bullet:
                        # if it's a bullet tell the other side that it can shoot
                        obj.owner.announceCanShoot(True)
                        self.scene().removeItem(obj)
                        # remove the bullet
                        self.scene().removeItem(self)
                        self.owner.announceCanShoot(True)
                        sip.delete(self)
                        del self
                    elif oType == Block:
                        # handle different types of blocks
                        if obj.type == BlockType.brick:
                            obj.isHidden = True
                            self.scene().removeItem(obj)
                            # remove the bullet
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            sip.delete(self)
                            del self
                        elif obj.type == BlockType.steel:
                            # only player level 4 can destroy steel
                            if type(self.owner).__name__ == "Player":
                                if self.owner.level == 4:
                                    obj.isHidden = True
                                    self.scene().removeItem(obj)
                            # remove the bullet
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            sip.delete(self)
                            del self
                        else:
                            pass
                    elif oType == Base:
                        self.owner.gameOverEmitter.gameOverSignal.emit(1)
                        self.scene().removeItem(self)
                        sip.delete(self)
                        del self
                    return
