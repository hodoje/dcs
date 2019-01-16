from PyQt5.QtCore import Qt, QTimer, QAbstractAnimation, QPropertyAnimation, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsPixmapItem

from firingNotifier import FiringNotifier
from killEmitter import KillEmitter
from movementNotifier import MovementNotifier
from player import Player
from enemy import Enemy
from block import Block
from base import Base
from enemyTankDetailsFactory import EnemyTankDetailsFactory
from blockTypeEnum import BlockType
from gameOver import GameOver
from gameOverEmitter import GameOverEmitter
from playerDeadEmitter import PlayerDeadEmitter
from playerWrapper import PlayerWrapper

import random
import sip


class Board(QGraphicsView):
    def __init__(self, parent, config, currentMap, menuToMainWindowData):
        QGraphicsView.__init__(self, parent)

        self.config = config
        self.currentMap = currentMap
        self.menuToMainWindowData = menuToMainWindowData
        # set up player and enemy details
        self.playerColors = ["yellow", "green"]
        self.playerLevels = self.config.playerLevels
        self.numOfPlayers = self.menuToMainWindowData.numOfPlayers
        self.playerWrappers = {}
        self.enemyColor = "gray"
        self.enemiesEtds = {}
        self.enemies = {}
        self.enemySpawnRegionWidth = self.config.enemySpawnRegionWidth
        self.enemySpawnRegionHeight = self.config.enemySpawnRegionHeight
        self.enemySpawnInterval = 3000
        self.maxEnemyCnt = 20
        self.currentEnemyCnt = 0
        self.maxEnemiesCurrentlyAlive = 6
        self.enemiesCurrentlyAlive = 0

        # ENEMY MOVEMENT TIMERS
        self.enemyMovementTimers = {}
        self.slowEnemyMovementTimer = QTimer()
        self.slowEnemyMovementTimer.setTimerType(Qt.PreciseTimer)
        self.slowEnemyMovementTimer.start(self.config.enemyMovementSpeedMap["slow"])
        self.enemyMovementTimers["slow"] = self.slowEnemyMovementTimer

        self.normalEnemyMovementTimer = QTimer()
        self.normalEnemyMovementTimer.setTimerType(Qt.PreciseTimer)
        self.normalEnemyMovementTimer.start(self.config.enemyMovementSpeedMap["normal"])
        self.enemyMovementTimers["normal"] = self.normalEnemyMovementTimer

        self.fastEnemyMovementTimer = QTimer()
        self.fastEnemyMovementTimer.setTimerType(Qt.PreciseTimer)
        self.fastEnemyMovementTimer.start(self.config.enemyMovementSpeedMap["fast"])
        self.enemyMovementTimers["fast"] = self.fastEnemyMovementTimer

        # ENEMY SHOOTING TIMERS
        self.enemyShootingTimer = QTimer()
        self.enemyShootingTimer.setTimerType(Qt.PreciseTimer)
        self.enemyShootingTimer.start(self.config.enemyShootInterval)

        # SET UP RANDOM ENEMY SPAWNING TIMER
        self.enemySpawnTimer = QTimer()
        self.enemySpawnTimer.setTimerType(Qt.PreciseTimer)
        self.enemySpawnTimer.timeout.connect(self.generateEnemy)
        self.enemySpawnTimer.start(self.enemySpawnInterval)

        # BULLET REFRESH RATE
        # i've chose not to make different timers for different speeds just to save
        # on resources and computational power
        # difference from tank movement is that tanks constantly move by 1px
        # and bullets don't need to so we change the number of pixel as the movement pace for bullets
        self.bulletTimer = QTimer()
        self.bulletTimer.setTimerType(Qt.PreciseTimer)
        self.bulletTimer.start(10)

        # movement gameOverAnimation timer
        self.animationTimer = QTimer()
        self.animationTimer.setTimerType(Qt.PreciseTimer)
        self.animationTimer.start(100)

        # each player and enemy will have this emitter passed to them
        # and will give it to each bullet so the bullet can signal when an enemy has been killed
        self.killEmitter = KillEmitter()
        self.killEmitter.emitKillSignal.connect(self.killEmitterHandler)

        # initialize board ui
        self.__init_ui__()

        # 34 is the max width of the enemy tank
        self.randomEnemyPositions = [
            self.field.x(),
            self.field.x() + (self.field.boundingRect().width() - 1) / 2,
            # '-34' doesn't let enemies spawn outside the field
            self.field.x() + self.field.boundingRect().width() - 34
        ]

        # player dead emitter
        self.playerDeadEmitter = PlayerDeadEmitter()
        self.playerDeadEmitter.playerDeadSignal.connect(self.playerDeadEmitterHandler)

        # GAME OVER
        self.gameOverEmitter = GameOverEmitter()
        self.gameOverEmitter.gameOverSignal.connect(self.gameOverHandler)
        # game over animation
        # we need to keep the gameOverAnimation alive so it can animate
        self.gameOver = GameOver(self.config.gameOverTexture)
        self.gameOverAnimation = QPropertyAnimation(self.gameOver, b"pos")
        self.gameOverAnimation.setDuration(3000)
        # for some reason the first position stays so i've put it under the view boundary
        self.gameOverAnimation.setStartValue(QPointF(150, self.fieldBottom + 50))
        self.gameOverAnimation.setEndValue(QPointF(150, 150))

        self.generateEtd()
        self.generatePlayers()

    # UI INITIALIZATION
    def __init_ui__(self):
        # set up the scene
        self.scene = QGraphicsScene()
        # these 10 subtracted pixels are for the margin
        self.scene.setSceneRect(0, 0, self.config.mainWindowSize["width"] - 10, self.config.mainWindowSize["height"] - 10)
        self.scene.setBackgroundBrush(Qt.darkGray)
        # set up the view
        self.setScene(self.scene)
        self.setFixedSize(self.config.mainWindowSize["width"], self.config.mainWindowSize["height"])
        # optimization
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setViewport(QGLWidget(QGLFormat()))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        # initialize the map
        self.generateMap()
        # interface
        currentStagePixmap = QPixmap("Resources/Images/UI/current_stage.png")
        self.currentStage = QGraphicsPixmapItem(currentStagePixmap)
        self.currentStage.setX(self.field.x() + self.field.boundingRect().width() + 20)
        self.currentStage.setY(self.field.y() + self.field.boundingRect().height() - 100)
        self.scene.addItem(self.currentStage)



    def generateMap(self):
        # save block textures
        self.blockTextures = self.config.blockTextures
        # set up the field
        self.field = QGraphicsRectItem(0, 0, 520, 520)
        self.field.setZValue(-1)
        self.field.setBrush(Qt.black)
        self.field.setX(40)
        self.field.setY(20)
        self.scene.addItem(self.field)
        # save these for later use
        self.fieldCenterX = self.field.x() + (self.field.boundingRect().width() - 1) / 2
        self.fieldBottom = self.field.y() + self.field.boundingRect().height() - 1
        # set up the map
        for b in self.config.maps[f"map{self.currentMap}"]["blueprint"]:
            blockX = b["xCoord"]
            blockY = b["yCoord"]
            blockType = b["type"]
            block = Block(blockX, blockY, blockType, self.blockTextures[blockType])
            if blockType == BlockType.bush:
                block.setZValue(2)
            elif blockType == BlockType.ice:
                block.setZValue(-1)
            self.scene.addItem(block)
        # add the base
        self.base = Base(self.config.baseTextures["aliveBase"], self.config.baseTextures["deadBase"])
        self.base.setX(self.fieldCenterX - self.base.aliveImage.width() / 2)
        self.base.setY(self.fieldBottom - self.base.aliveImage.height())
        self.scene.addItem(self.base)

    def generatePlayers(self):
        if self.menuToMainWindowData.isOnline:
            pass
        else:
            for i in range(self.numOfPlayers):
                if i == 0:
                    firingKey = Qt.Key_Space
                    movementKeys = {"Up": Qt.Key_Up, "Down": Qt.Key_Down, "Left": Qt.Key_Left, "Right": Qt.Key_Right}
                    movementNotifier = MovementNotifier(self.config.playerMovementSpeed)
                    movementNotifier.movementSignal.connect(self.updatePosition)
                    firingNotifier = FiringNotifier(50)
                    firingNotifier.firingSignal.connect(self.fireCanon)
                    player = Player(
                        i,
                        self.playerColors[i],
                        self.playerLevels,
                        firingKey,
                        movementKeys,
                        self.field,
                        self.killEmitter,
                        self.bulletTimer,
                        Enemy,
                        self.animationTimer,
                        self.gameOverEmitter,
                        self.playerDeadEmitter)
                    startingPos = QPointF(self.fieldCenterX - self.base.boundingRect().width() / 2 - self.base.boundingRect().width() * 2,
                                       self.fieldBottom - player.boundingRect().height() - 5)
                    player.startingPos = startingPos
                    playerWrapper = PlayerWrapper(i, player, firingKey, movementKeys, firingNotifier, movementNotifier)
                    self.playerWrappers[i] = playerWrapper
                    self.scene.addItem(player)
                    player.setPos(startingPos)
                elif i == 1:
                    firingKey = Qt.Key_J
                    movementKeys = {"Up": Qt.Key_W, "Down": Qt.Key_S, "Left": Qt.Key_A, "Right": Qt.Key_D}
                    movementNotifier = MovementNotifier(self.config.playerMovementSpeed)
                    movementNotifier.movementSignal.connect(self.updatePosition)
                    firingNotifier = FiringNotifier(150)
                    firingNotifier.firingSignal.connect(self.fireCanon)
                    player = Player(
                        i,
                        self.playerColors[i],
                        self.playerLevels,
                        firingKey,
                        movementKeys,
                        self.field,
                        self.killEmitter,
                        self.bulletTimer,
                        Enemy,
                        self.animationTimer,
                        self.gameOverEmitter,
                        self.playerDeadEmitter)
                    startingPos = QPointF(self.fieldCenterX + self.base.boundingRect().width() / 2 + self.base.boundingRect().width(),
                                        self.fieldBottom - player.boundingRect().height() - 5)
                    player.startingPos = startingPos
                    playerWrapper = PlayerWrapper(i, player, firingKey, movementKeys, firingNotifier, movementNotifier)
                    self.playerWrappers[i] = playerWrapper
                    self.scene.addItem(player)
                    player.setPos(startingPos)

    def generateEtd(self):
        # generate enemy details
        etdFactory = EnemyTankDetailsFactory(
            self.config.enemyTypes,
            self.config.enemyTypeIds,
            self.config.maps[f"map{self.currentMap}"]["enemies"],
            self.config.bulletSpeedMap)
        self.enemiesEtds = etdFactory.generateEnemiesDetails()

    def generateEnemy(self):
        if self.currentEnemyCnt < self.maxEnemyCnt:
            if self.enemiesCurrentlyAlive < self.maxEnemiesCurrentlyAlive:
                # set enemy pos and check if it can be spawned
                posX1 = random.choice(self.randomEnemyPositions)
                posY1 = self.field.y()
                posX2 = posX1 + self.enemySpawnRegionWidth
                posY2 = posY1 + self.enemySpawnRegionHeight
                middleX = posX1 + self.enemySpawnRegionWidth / 2
                middleY = posY1 + self.enemySpawnRegionHeight / 2
                item = self.scene.itemAt(posX1, posY1, self.transform())
                if type(item) != QGraphicsRectItem and item is not None:
                    return
                else:
                    item = self.scene.itemAt(posX1, posY2, self.transform())
                    if type(item) != QGraphicsRectItem and item is not None:
                        return
                    else:
                        item = self.scene.itemAt(posX2, posY1, self.transform())
                        if type(item) != QGraphicsRectItem and item is not None:
                            return
                        else:
                            item = self.scene.itemAt(posX2, posY2, self.transform())
                            if type(item) != QGraphicsRectItem and item is not None:
                                return
                            else:
                                item = self.scene.itemAt(middleX, middleY, self.transform())
                                if type(item) != QGraphicsRectItem and item is not None:
                                    return
                                else:
                                    pass
                enemyEtd = self.enemiesEtds[self.currentEnemyCnt]
                # set if tank is flashing or not
                isFlashing = False
                if self.currentEnemyCnt == 3 or self.currentEnemyCnt == 11 or self.currentEnemyCnt == 17:
                    isFlashing = True
                enemy = Enemy(self.currentEnemyCnt,
                      enemyEtd,
                      isFlashing,
                      self.enemyColor,
                      self.field,
                      self.enemyMovementTimers[enemyEtd.movementSpeed],
                      self.enemyShootingTimer,
                      self.animationTimer,
                      self.bulletTimer,
                      Player,
                      self.killEmitter,
                      self.gameOverEmitter)
                self.scene.addItem(enemy)
                enemy.setPos(posX1, posY1)
                self.enemies[enemy.id] = enemy
                self.currentEnemyCnt += 1
                self.enemiesCurrentlyAlive += 1

    def keyPressEvent(self, event):
        key = event.key()
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            if key == playerWrapper.firingKey:
                playerWrapper.firingNotifier.add_key(key)
            elif key in playerWrapper.movementKeys.values():
                playerWrapper.movementNotifier.add_key(key)

    def keyReleaseEvent(self, event):
        key = event.key()
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            if key == playerWrapper.firingKey:
                playerWrapper.firingNotifier.remove_key(key)
            elif key in playerWrapper.movementKeys.values():
                playerWrapper.movementNotifier.remove_key(key)

    def updatePosition(self, key):
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            if key in playerWrapper.movementKeys.values():
                playerWrapper.player.updatePosition(key)

    def fireCanon(self, key):
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            if key == playerWrapper.firingKey:
                playerWrapper.player.shoot(key)

    def killEmitterHandler(self, ked):
        if ked.targetType is Enemy:
            # add points, check if it's flashing so there's a powerup now on the field
            enemy = self.enemies[ked.targetId]
            player = self.playerWrappers[ked.shooterId].player
            player.points += enemy.tankDetails.points

            # remove the tank and delete it for good
            del self.enemiesEtds[ked.targetId]
            self.scene.removeItem(self.enemies[ked.targetId])
            sip.delete(self.enemies[ked.targetId])
            del self.enemies[ked.targetId]
            self.enemiesCurrentlyAlive -= 1
        elif ked.targetType is Player:
            player = self.playerWrappers[ked.targetId].player
            player.resetPlayer()

    def playerDeadEmitterHandler(self, playerId):
        playerWrapper = self.playerWrappers[playerId]
        if len(self.playerWrappers) == 1:
            self.gameOverHandler()
        # stop all player notifiers
        playerWrapper.firingNotifier.thread.terminate()
        playerWrapper.movementNotifier.thread.terminate()
        # playerWrapper.firingNotifier.thread.wait()
        # playerWrapper.movementNotifier.thread.wait()

        self.scene.removeItem(playerWrapper.player)
        sip.delete(playerWrapper.player)
        del playerWrapper.player
        del self.playerWrappers[playerId]

    def gameOverHandler(self):
        if self.base.isAlive:
            self.base.destroyBase()
            pw: PlayerWrapper
            for pw in self.playerWrappers.values():
                pw.firingNotifier.firingSignal.disconnect()
                pw.movementNotifier.movementSignal.disconnect()
                self.scene.removeItem(pw.player)
            self.scene.addItem(self.gameOver)
            # ANIMATE GAME OVER
            self.gameOverAnimation.start(QAbstractAnimation.DeleteWhenStopped)
            # disconnect from game over signal so there won't be more animations
            self.gameOverEmitter.gameOverSignal.disconnect()
