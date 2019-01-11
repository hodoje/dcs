from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem

from directionEnum import Direction


class Bullet(QGraphicsPixmapItem):
    def __init__(self, movingDirection, owner):
        super().__init__()
        # moving direction determines what picture is used for the bullet
        self.movingDirection = movingDirection
        # reference to a player so a bullet can call player.announceCanShoot function
        # to signal that will signal the board that the player can shoot again
        self.owner = owner

        # call 'move' every 50ms
        #self.timer = QTimer()
        #self.timer.setTimerType(Qt.PreciseTimer)
        self.timer = self.owner.bulletTimer
        self.timer.timeout.connect(self.move)
        #self.timer.start(10)

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
        self.setPos(self.x() + 3, self.y())

    def moveLeft(self):
        self.setPos(self.x() - 3, self.y())

    def moveDown(self):
        self.setPos(self.x(), self.y() + 3)

    def moveUp(self):
        self.setPos(self.x(), self.y() - 3)

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
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        # react only if it's an owners targetType or a Bullet
                        if oType == self.owner.targetType or oType == Bullet:
                            self.scene().removeItem(obj)
                            # if it's a target then emit a kill
                            if oType == self.owner.targetType:
                                self.owner.killEmitter.emitKillSignal.emit(obj)
                            # if it's a bullet tell the other side that it can shoot
                            if oType == Bullet:
                                obj.owner.announceCanShoot(True)
                            del obj
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            del self
                            return
        elif self.movingDirection == Direction.LEFT:
            if self.pos().x() + self.boundingRect().width() < self.owner.field.x():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet:
                            self.scene().removeItem(obj)
                            if oType == self.owner.targetType:
                                self.owner.killEmitter.emitKillSignal.emit(obj)
                            if oType == Bullet:
                                obj.owner.announceCanShoot(True)
                            del obj
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            del self
                            return
        elif self.movingDirection == Direction.DOWN:
            if self.pos().y() > self.owner.field.y() + self.owner.field.boundingRect().height():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet:
                            self.scene().removeItem(obj)
                            if oType == self.owner.targetType:
                                self.owner.killEmitter.emitKillSignal.emit(obj)
                            if oType == Bullet:
                                obj.owner.announceCanShoot(True)
                            del obj
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            del self
                            return
        elif self.movingDirection == Direction.UP:
            if self.pos().y() + self.boundingRect().height() < self.owner.field.y():
                self.scene().removeItem(self)
                self.owner.announceCanShoot(True)
                del self
            # if 1 colliding item will always be the scene's field property
            else:
                collidingItems = self.collidingItems()
                if len(collidingItems) > 1:
                    for obj in collidingItems:
                        oType = type(obj)
                        if oType == self.owner.targetType or oType == Bullet:
                            self.scene().removeItem(obj)
                            if oType == self.owner.targetType:
                                self.owner.killEmitter.emitKillSignal.emit(obj)
                            if oType == Bullet:
                                obj.owner.announceCanShoot(True)
                            del obj
                            self.scene().removeItem(self)
                            self.owner.announceCanShoot(True)
                            del self
                            return
