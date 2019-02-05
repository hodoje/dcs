from PyQt5 import sip
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtMultimedia import QSound
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem

import random

from Block.base import Base
from BasicElements.enemy import Enemy
from BasicElements.gameOver import GameOver
from BasicElements.player import Player
from Block.block import Block
from Block.blockTypeEnum import BlockType
from Bridge.localGameData import LocalGameData
from DeusEx.deusExSpawner import DeusExSpawner
from Emitters.gameOverEmitter import GameOverEmitter
from Emitters.killEmitter import KillEmitter
from Emitters.playerDeadEmitter import PlayerDeadEmitter
from Enemy.enemyTankDetailsFactory import EnemyTankDetailsFactory
from HUD.hudCurrentStage import HudCurrentStage
from HUD.hudEnemyContainer import HudEnemyContainer
from HUD.hudPlayerLives import HudPlayerLives
from Notifiers.firingNotifier import FiringNotifier
from Notifiers.movementNotifier import MovementNotifier
from Player.playerWrapper import PlayerWrapper
from DeusEx.deusex import DeusEx
from DeusEx.deusexTypes import DeusExTypes


class Board(QGraphicsView):
    def __init__(self, parent, config, currentMap, currentStage, bridge, gameTypeData, playerData):
        QGraphicsView.__init__(self, parent)
        self.config = config
        self.currentMap = currentMap
        self.currentStage = currentStage
        self.bridge = bridge
        self.gameTypeData = gameTypeData
        self.isOnline = gameTypeData.isOnline
        self.numOfPlayers = gameTypeData.numOfPlayers
        self.playerData = playerData
        # set up player and enemy details
        # incremented when generating players (used on local)
        self.playersAlive = 0
        self.playerColors = ["yellow", "green"]
        self.playerLevels = self.config.playerLevels
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
        self.slowEnemyMovementTimer.setInterval(self.config.enemyMovementSpeedMap["slow"])
        self.slowEnemyMovementTimer.start()
        self.enemyMovementTimers["slow"] = self.slowEnemyMovementTimer

        self.normalEnemyMovementTimer = QTimer()
        self.normalEnemyMovementTimer.setTimerType(Qt.PreciseTimer)
        self.normalEnemyMovementTimer.setInterval(self.config.enemyMovementSpeedMap["normal"])
        self.normalEnemyMovementTimer.start()
        self.enemyMovementTimers["normal"] = self.normalEnemyMovementTimer

        self.fastEnemyMovementTimer = QTimer()
        self.fastEnemyMovementTimer.setTimerType(Qt.PreciseTimer)
        self.fastEnemyMovementTimer.setInterval(self.config.enemyMovementSpeedMap["fast"])
        self.fastEnemyMovementTimer.start()
        self.enemyMovementTimers["fast"] = self.fastEnemyMovementTimer

        # ENEMY SHOOTING TIMER
        self.enemyShootingTimer = QTimer()
        self.enemyShootingTimer.setTimerType(Qt.PreciseTimer)
        self.enemyShootingTimer.setInterval(self.config.enemyShootInterval)
        self.enemyShootingTimer.start()

        # SET UP RANDOM ENEMY SPAWNING TIMER
        self.enemySpawnTimer = QTimer()
        self.enemySpawnTimer.setTimerType(Qt.PreciseTimer)
        self.enemySpawnTimer.timeout.connect(self.generateEnemy)
        self.enemySpawnTimer.setInterval(self.enemySpawnInterval)
        self.enemySpawnTimer.start()

        # BULLET REFRESH RATE
        # i've chose not to make different timers for different speeds just to save
        # on resources and computational power
        # difference from tank movement is that tanks constantly move by 1px
        # and bullets don't need to so we change the number of pixel as the movement pace for bullets
        self.bulletTimer = QTimer()
        self.bulletTimer.setTimerType(Qt.PreciseTimer)
        self.bulletTimer.setInterval(10)
        self.bulletTimer.start()

        # movement animation timer
        self.animationTimer = QTimer()
        self.animationTimer.setTimerType(Qt.PreciseTimer)
        self.animationTimer.setInterval(100)
        self.animationTimer.start()

        # each player and enemy will have this emitter passed to them
        # and will give it to each bullet so the bullet can signal when an enemy has been killed
        self.killEmitter = KillEmitter()
        self.killEmitter.emitKillSignal.connect(self.killEmitterHandler)

        # player dead emitter
        # each player has one and when the player has no more lives, it emits this signal
        self.playerDeadEmitter = PlayerDeadEmitter()
        self.playerDeadEmitter.playerDeadSignal.connect(self.playerDeadEmitterHandler)

        # explosion sound whenever an enemy is destroyed
        self.enemyExplosionSound = QSound(self.config.sounds["explosion"])
        # explosion sound whenever a player is destroyed
        self.playerExplosionSound = QSound(self.config.sounds["playerExplosion"])

        # initialize board ui
        self.__init_ui__()

        # 34 is the max width of the enemy tank
        self.randomEnemyPositions = [
            self.field.x(),
            self.field.x() + (self.field.boundingRect().width() - 1) / 2,
            # '-34' doesn't let enemies spawn outside the field
            self.field.x() + self.field.boundingRect().width() - 34
        ]

        # GAME OVER setup
        self.gameOverEmitter = GameOverEmitter()
        self.gameOverEmitter.gameOverSignal.connect(self.gameOverHandler)
        # game over animation
        # we need to keep the gameOverAnimation alive so it can animate
        self.gameOver = GameOver(self.config.gameOverTexture)
        self.gameOver.setPos(QPointF(150, self.fieldBottom + 50))
        self.gameOverTimer = QTimer()
        self.gameOverTimer.setTimerType(Qt.PreciseTimer)
        self.gameOverTimer.setInterval(15)
        self.gameOverTimer.timeout.connect(self.animateGameOver)
        self.gameOverSound = QSound(self.config.sounds["gameOver"])

        # deus ex spawner and its possible locations
        self.deusExLocations = [
            QPointF(self.field.x(), self.field.y()),
            QPointF(self.field.x() + 160, self.field.y()),
            QPointF(self.field.x() + 240, self.field.y()),
            QPointF(self.field.x() + 320, self.field.y()),
            QPointF(self.field.x(), self.field.y() + 160),
            QPointF(self.field.x() + 160, self.field.y() + 160),
            QPointF(self.field.x() + 240, self.field.y() + 160),
            QPointF(self.field.x() + 320, self.field.y() + 160),
            QPointF(self.field.x(), self.field.y() + 240),
            QPointF(self.field.x() + 160, self.field.y() + 240),
            QPointF(self.field.x() + 240, self.field.y() + 240),
            QPointF(self.field.x() + 320, self.field.y() + 240),
            QPointF(self.field.x(), self.field.y() + 320),
            QPointF(self.field.x() + 160, self.field.y() + 320),
            QPointF(self.field.x() + 240, self.field.y() + 320),
            QPointF(self.field.x() + 320, self.field.y() + 320)
        ]
        # deusExActivities
        self.positiveDeusExActivities = [
            self.destroyCurrentlyAliveEnemies,
            self.playerShield,
            self.playerLevelUp,
            self.playerLifeUp,
            self.stopTheTime,
            self.upgradeBase
        ]
        self.negativeDeusExActivities = [
            self.playerLevelDown,
            self.playerLifeDown,
            self.playerLosePoints,
            self.playerCantMove,
            self.removeBaseShield
        ]
        self.deusExSpawner = DeusExSpawner(self.scene, self.config, 15000, self.deusExActivate, self.deusExLocations)

        self.generateEtd()
        self.generatePlayers()

    # UI INITIALIZATION
    def __init_ui__(self):
        # set up the scene
        self.scene = QGraphicsScene()
        # these 10 subtracted pixels are for the margin
        self.scene.setSceneRect(0, 0, self.config.mainWindowSize["width"] - 10,
                                self.config.mainWindowSize["height"] - 10)
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
        # HUD
        # stage hud
        self.hudCurrentStage = HudCurrentStage(self.config, self.currentStage)
        self.hudCurrentStage.setX(self.field.x() + self.field.boundingRect().width() + 20)
        self.hudCurrentStage.setY(self.field.y() + self.field.boundingRect().height() - 100)
        self.scene.addItem(self.hudCurrentStage)
        # player lives hud
        self.hudPlayersLives = {}
        if self.isOnline:
            pass
        else:
            for i in range(self.numOfPlayers):
                if i == 0:
                    if self.playerData.firstPlayerDetails.isAlive:
                        playerLives = HudPlayerLives(i, self.config, self.playerData.firstPlayerDetails.lives)
                        playerLives.setX(self.field.x() + self.field.boundingRect().width() + 20)
                        playerLives.setY(self.field.y() + self.field.boundingRect().height() - 220 + i * 60)
                        self.scene.addItem(playerLives)
                        self.hudPlayersLives[self.playerData.firstPlayerDetails.id] = playerLives
                elif i == 1:
                    if self.playerData.secondPlayerDetails.isAlive:
                        playerLives = HudPlayerLives(i, self.config, self.playerData.secondPlayerDetails.lives)
                        playerLives.setX(self.field.x() + self.field.boundingRect().width() + 20)
                        playerLives.setY(self.field.y() + self.field.boundingRect().height() - 220 + i * 60)
                        self.scene.addItem(playerLives)
                        self.hudPlayersLives[self.playerData.secondPlayerDetails.id] = playerLives
        # enemies left hud
        self.enemyHud = HudEnemyContainer(self.config)
        self.enemyHud.setX(self.field.x() + self.field.boundingRect().width() + 20)
        self.enemyHud.setY(self.field.y() + 40)
        self.scene.addItem(self.enemyHud)

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
        self.baseBlocks = []
        # set up the map
        for b in self.config.maps[f"map{self.currentMap}"]["blueprint"]:
            blockX = b["xCoord"]
            blockY = b["yCoord"]
            blockType = b["type"]
            blockIsBase = b["isBaseBlock"]
            block = Block(blockX, blockY, blockType, blockIsBase, self.blockTextures)
            # hold reference to base blocks
            if block.isBaseBlock:
                self.baseBlocks.append(block)
            # setting z value to be higher than others so the tanks would appear under the bush
            if blockType == BlockType.bush:
                block.setZValue(2)
            # setting z value lower than others so the tanks would appear above the ice
            elif blockType == BlockType.ice:
                block.setZValue(-1)
            self.scene.addItem(block)
        # add the base
        self.base = Base(self.config.baseTextures["aliveBase"], self.config.baseTextures["deadBase"])
        self.base.setX(self.fieldCenterX - self.base.aliveImage.width() / 2)
        self.base.setY(self.fieldBottom - self.base.aliveImage.height())
        self.scene.addItem(self.base)

    def generatePlayers(self):
        if self.isOnline:
            pass
        else:
            for i in range(self.numOfPlayers):
                if i == 0:
                    if self.playerData.firstPlayerDetails.isAlive:
                        firingKey = Qt.Key_Space
                        movementKeys = {"Up": Qt.Key_Up, "Down": Qt.Key_Down, "Left": Qt.Key_Left, "Right": Qt.Key_Right}
                        movementNotifier = MovementNotifier(self.config.playerMovementSpeed)
                        movementNotifier.movementSignal.connect(self.updatePosition)
                        firingNotifier = FiringNotifier(50)
                        firingNotifier.firingSignal.connect(self.fireCanon)
                        playerDetails = self.playerData.firstPlayerDetails
                        playerWrapper = PlayerWrapper(playerDetails,
                                                      self.config,
                                                      self.playerColors[i],
                                                      firingKey,
                                                      movementKeys,
                                                      firingNotifier,
                                                      movementNotifier,
                                                      self.playerLevels,
                                                      self.field,
                                                      self.killEmitter,
                                                      self.bulletTimer,
                                                      Enemy,
                                                      self.animationTimer,
                                                      self.playerDeadEmitter,
                                                      self.gameOverEmitter)
                        playerWrapper.player.canShootSignal.connect(self.allowFiring)
                        startingPos = QPointF(
                            self.fieldCenterX - self.base.boundingRect().width() / 2 - self.base.boundingRect().width() * 2,
                            self.fieldBottom - playerWrapper.player.boundingRect().height() - 5)
                        playerWrapper.player.startingPos = startingPos
                        self.playerWrappers[playerDetails.id] = playerWrapper
                        self.scene.addItem(playerWrapper.player)
                        self.playersAlive += 1
                        playerWrapper.player.setPos(startingPos)
                elif i == 1:
                    if self.playerData.secondPlayerDetails.isAlive:
                        firingKey = Qt.Key_J
                        movementKeys = {"Up": Qt.Key_W, "Down": Qt.Key_S, "Left": Qt.Key_A, "Right": Qt.Key_D}
                        movementNotifier = MovementNotifier(self.config.playerMovementSpeed)
                        movementNotifier.movementSignal.connect(self.updatePosition)
                        firingNotifier = FiringNotifier(50)
                        firingNotifier.firingSignal.connect(self.fireCanon)
                        playerDetails = self.playerData.secondPlayerDetails
                        playerWrapper = PlayerWrapper(playerDetails,
                                                      self.config,
                                                      self.playerColors[i],
                                                      firingKey,
                                                      movementKeys,
                                                      firingNotifier,
                                                      movementNotifier,
                                                      self.playerLevels,
                                                      self.field,
                                                      self.killEmitter,
                                                      self.bulletTimer,
                                                      Enemy,
                                                      self.animationTimer,
                                                      self.playerDeadEmitter,
                                                      self.gameOverEmitter)
                        playerWrapper.player.canShootSignal.connect(self.allowFiring)
                        startingPos = QPointF(
                            self.fieldCenterX + self.base.boundingRect().width() / 2 + self.base.boundingRect().width(),
                            self.fieldBottom - playerWrapper.player.boundingRect().height() - 5)
                        playerWrapper.player.startingPos = startingPos
                        self.playerWrappers[playerDetails.id] = playerWrapper
                        self.scene.addItem(playerWrapper.player)
                        self.playersAlive += 1
                        playerWrapper.player.setPos(startingPos)

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
                self.scene.removeItem(self.enemyHud.removeEnemy())
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

    def allowFiring(self, canShootSignalData):
        self.playerWrappers[canShootSignalData.playerId].firingNotifier.canEmit = canShootSignalData.canEmit

    def fireCanon(self, key):
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            if key == playerWrapper.firingKey:
                playerWrapper.player.shoot(key)

    def killEmitterHandler(self, killEmitterData):
        if killEmitterData.targetType is Enemy:
            # add points, check if the enemy is flashing and if so, spawn a positive DeusEx
            enemy = self.enemies[killEmitterData.targetId]
            playerWrapper = self.playerWrappers[killEmitterData.shooterId]
            playerWrapper.player.points += enemy.tankDetails.points
            playerWrapper.separateTankDetails.details[enemy.tankDetails.stringTankType]["count"] += 1
            # if the enemy is flashing then give the players a positive DeusEx
            if enemy.isFlashing:
                self.deusExSpawner.spawn(isPositive=True)
            # remove the tank, its details and delete it for good
            del self.enemiesEtds[killEmitterData.targetId]
            self.scene.removeItem(self.enemies[killEmitterData.targetId])
            sip.delete(self.enemies[killEmitterData.targetId])
            del self.enemies[killEmitterData.targetId]

            self.enemiesCurrentlyAlive -= 1
            self.enemyExplosionSound.play()
            # if there are no more enemy tank details that means that the stage is over
            if not self.enemiesEtds:
                self.stageEndInitiate()
        elif killEmitterData.targetType is Player:
            player = self.playerWrappers[killEmitterData.targetId].player
            player.resetPlayer()
            # if lives are less than 0, that means the player is dead
            if player.lives >= 0:
                self.hudPlayersLives[player.id].updateLives(player.lives)
            self.playerExplosionSound.play()

    def playerDeadEmitterHandler(self, playerId):
        playerWrapper = self.playerWrappers[playerId]
        # stop all player notifiers
        playerWrapper.firingNotifier.firingSignal.disconnect()
        playerWrapper.movementNotifier.movementSignal.disconnect()
        playerWrapper.firingNotifier.thread.terminate()
        playerWrapper.movementNotifier.thread.terminate()
        playerWrapper.player.isAlive = False
        # remove player from scene, but still keep it's data
        self.scene.removeItem(playerWrapper.player)
        # delete the reference to a player because in gameover handler
        # we will go over the rest of players and remove them from the scene
        # so now we set the player reference to None because of the check in gameover handler
        # decrease the number of players alive, if now is 0, all players are dead and the game is over
        self.playersAlive -= 1
        if self.playersAlive == 0:
            self.gameOverHandler()

    def stageEndInitiate(self):
        self.stageEndTimer = QTimer()
        self.stageEndTimer.setTimerType(Qt.PreciseTimer)
        self.stageEndTimer.setInterval(3000)
        self.stageEndTimer.timeout.connect(self.stageEnd)
        self.stageEndTimer.start()

    def stageEnd(self):
        self.stageEndTimer.stop()
        self.deusExSpawner.spawnTimer.stop()
        playerWrapper: PlayerWrapper
        for playerWrapper in self.playerWrappers.values():
            # check if player is dead, if not, disconnect from all notifiers
            # if he's dead, he already disconnected, and is removed from the scene
            if playerWrapper.player is not None and playerWrapper.player.isAlive:
                playerWrapper.firingNotifier.firingSignal.disconnect()
                playerWrapper.movementNotifier.movementSignal.disconnect()
                playerWrapper.firingNotifier.thread.terminate()
                playerWrapper.movementNotifier.thread.terminate()
                self.scene.removeItem(playerWrapper.player)
        # clear up the map and disable all timers until next stage
        self.scene.clear()
        self.animationTimer.stop()
        self.bulletTimer.stop()
        for timer in self.enemyMovementTimers.values():
            timer.stop()
        self.enemySpawnTimer.stop()
        self.enemyShootingTimer.stop()
        if self.isOnline:
            # data = OnlineGameData(self.playerWrappers[self.playerData.playerDetails.id].getPlayerDetails())
            # self.bridge.onlineGameStageEndSignal.emit(data)
            pass
        else:
            if self.numOfPlayers == 1:
                data = LocalGameData(self.playerWrappers[self.playerData.firstPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.firstPlayerDetails.id].separateTankDetails)
                self.bridge.localGameStageEndSignal.emit(data)
            else:
                data = LocalGameData(self.playerWrappers[self.playerData.firstPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.firstPlayerDetails.id].separateTankDetails,
                                     self.playerWrappers[self.playerData.secondPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.secondPlayerDetails.id].separateTankDetails)
                self.bridge.localGameStageEndSignal.emit(data)

    def gameOverHandler(self):
        if self.base.isAlive:
            self.base.destroyBase()
            self.deusExSpawner.spawnTimer.stop()
            playerWrapper: PlayerWrapper
            for playerWrapper in self.playerWrappers.values():
                # check if player is dead, if not, disconnect from all notifiers
                # if he's dead, he already disconnected, and is removed from the scene
                if playerWrapper.player is not None and playerWrapper.player.isAlive:
                    playerWrapper.firingNotifier.thread.terminate()
                    playerWrapper.movementNotifier.thread.terminate()
                    playerWrapper.firingNotifier.firingSignal.disconnect()
                    playerWrapper.movementNotifier.movementSignal.disconnect()
                    self.scene.removeItem(playerWrapper.player)
            self.scene.addItem(self.gameOver)
            # ANIMATE GAME OVER
            #self.gameOverAnimation.start(QPropertyAnimation.KeepWhenStopped)
            #print(self.gameOverAnimation.currentValue())
            self.gameOverTimer.start()
            self.gameOverSound.play()
            # disconnect from game over signal so there won't be more animations
            self.gameOverEmitter.gameOverSignal.disconnect()

    def animateGameOver(self):
        self.gameOver.setY(self.gameOver.y() - 2)
        if int(self.gameOver.y()) == 150:
            self.gameOverTimer.stop()
            self.gameOverHandlerSendData()

    def gameOverHandlerSendData(self):
        self.scene.clear()
        self.animationTimer.stop()
        self.bulletTimer.stop()
        for timer in self.enemyMovementTimers.values():
            timer.stop()
        self.enemySpawnTimer.stop()
        self.enemyShootingTimer.stop()
        if self.isOnline:
            pass
        else:
            if self.numOfPlayers == 1:
                data = LocalGameData(self.playerWrappers[self.playerData.firstPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.firstPlayerDetails.id].separateTankDetails)
                self.bridge.localGameOverSignal.emit(data)
            else:
                data = LocalGameData(self.playerWrappers[self.playerData.firstPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.firstPlayerDetails.id].separateTankDetails,
                                     self.playerWrappers[self.playerData.secondPlayerDetails.id].getPlayerDetails(),
                                     self.playerWrappers[self.playerData.secondPlayerDetails.id].separateTankDetails)
                self.bridge.localGameOverSignal.emit(data)

    def deusExActivate(self, deusExSignalData):
        deusExChoice = None
        if deusExSignalData.deusExType is DeusExTypes.POSITIVE:
            deusExChoice = random.choice(self.positiveDeusExActivities)
        else:
            deusExChoice = random.choice(self.negativeDeusExActivities)
        for player in deusExSignalData.markedPlayers:
            pw = self.playerWrappers[player.id]
            deusExChoice(pw)
        self.deusExSpawner.spawnTimer.start()

    # DEUS EX ACTIVITIES
    # POSITIVE
    def destroyCurrentlyAliveEnemies(self, pw=None):
        if self.enemies:
            for id, enemy in self.enemies.items():
                del self.enemiesEtds[id]
                self.scene.removeItem(enemy)
                # although this looks like it would produce an error because of deleting elements from currently
                # iterating collection, it won't because we're deleting the c++ object and not the python wrapper
                sip.delete(enemy)
            self.enemies.clear()
            self.enemiesCurrentlyAlive = 0
            self.enemyExplosionSound.play()
        # if there are no more enemy tank details that means that the stage is over
        if not self.enemiesEtds:
            self.stageEndInitiate()

    def playerShield(self, pw=None):
        pw.player.isShielded = True
        pw.player.shieldTimer.start()
        playerShieldTimer = QTimer()
        playerShieldTimer.setTimerType(Qt.PreciseTimer)
        playerShieldTimer.setInterval(15000)
        playerShieldTimer.timeout.connect(lambda: self.afterPlayerShield(pw))
        playerShieldTimer.start()
        setattr(self, f"playerShieldTimer{pw.player.id}", playerShieldTimer)

    def afterPlayerShield(self, pw=None):
        pw.player.shieldTimer.stop()
        pw.player.isShielded = False
        timer = getattr(self, f"playerShieldTimer{pw.player.id}", None)
        if timer is not None:
            timer.stop()
            del timer

    def upgradeBase(self, pw=None):
        for baseBlock in self.baseBlocks:
            if baseBlock.isHidden:
                self.scene.addItem(baseBlock)
                baseBlock.isHidden = False
            baseBlock.type = BlockType.steel
            baseBlock.updateTexture()
        self.upgradeBaseTimer = QTimer()
        self.upgradeBaseTimer.setTimerType(Qt.PreciseTimer)
        self.upgradeBaseTimer.timeout.connect(self.afterUpgradeBase)
        self.upgradeBaseTimer.setInterval(15000)
        self.upgradeBaseTimer.start()

    def afterUpgradeBase(self, pw=None):
        for baseBlock in self.baseBlocks:
            baseBlock.type = BlockType.brick
            baseBlock.updateTexture()
        self.upgradeBaseTimer.stop()
        del self.upgradeBaseTimer

    def playerLevelUp(self, pw=None):
        pw.player.levelUp()
        # check if player is blocked when his size changed, and if it is, put him somewhere where he's not blocked
        allObjects = self.scene.items()
        x1 = pw.player.x()
        y1 = pw.player.y()
        x2 = x1 + pw.player.width
        y2 = y1 + pw.player.height
        for obj in allObjects:
            oType = type(obj)
            if obj != pw.player and oType != QGraphicsRectItem:
                if type(obj) == Block:
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
                    # handle the x axis
                    deltaX = None
                    deltaY = None
                    if x1 < objX1:
                        deltaX = x2 - objX1
                        x1 -= deltaX
                    elif x1 > objX1:
                        deltaX = objX2 - x1
                        x1 += deltaX
                    else:
                        deltaX = 0
                    # handle the y axis
                    if y1 < objY1:
                        deltaY = y2 - objY1
                        y1 -= (deltaY + 1)
                    elif y1 > objY1:
                        deltaY = objY2 - y1
                        y1 += deltaY + 1
                    else:
                        deltaY = 0

                    # draw in paint these situations and you'll understand why i chose this approach
                    if deltaX > deltaY:
                        pw.player.setY(y1)
                    else:
                        pw.player.setX(x1)
                    continue

    def playerLifeUp(self, pw=None):
        pw.player.lives += 1
        self.hudPlayersLives[pw.player.id].updateLives(pw.player.lives)

    def stopTheTime(self, pw=None):
        self.enemyShootingTimer.stop()
        for timer in self.enemyMovementTimers.values():
            timer.stop()
        self.stopTheTimeTimer = QTimer()
        self.stopTheTimeTimer.setTimerType(Qt.PreciseTimer)
        self.stopTheTimeTimer.timeout.connect(self.afterStopTheTime)
        self.stopTheTimeTimer.setInterval(10000)
        self.stopTheTimeTimer.start()

    def afterStopTheTime(self, pw=None):
        self.enemyShootingTimer.start()
        for timer in self.enemyMovementTimers.values():
            timer.start()
        self.stopTheTimeTimer.stop()
        del self.stopTheTimeTimer

    # NEGATIVE
    def playerLevelDown(self, pw=None):
        pw.player.levelDown()
        # check if player is blocked when his size changed, and if it is, put him somewhere where he's not blocked
        allObjects = self.scene.items()
        x1 = pw.player.x()
        y1 = pw.player.y()
        x2 = x1 + pw.player.width
        y2 = y1 + pw.player.height
        for obj in allObjects:
            oType = type(obj)
            if obj != pw.player and oType != QGraphicsRectItem:
                if type(obj) == Block:
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
                    # handle the x axis
                    deltaX = None
                    deltaY = None
                    if x1 < objX1:
                        deltaX = x2 - objX1
                        x1 -= deltaX
                    elif x1 > objX1:
                        deltaX = objX2 - x1
                        x1 += deltaX
                    else:
                        deltaX = 0
                    # handle the y axis
                    if y1 < objY1:
                        deltaY = y2 - objY1
                        y1 -= (deltaY + 1)
                    elif y1 > objY1:
                        deltaY = objY2 - y1
                        y1 += deltaY + 1
                    else:
                        deltaY = 0

                    # draw in paint these situations and you'll understand why i chose this approach
                    if deltaX > deltaY:
                        pw.player.setY(y1)
                    else:
                        pw.player.setX(x1)
                    continue

    def playerLifeDown(self, pw=None):
        pw.player.lives -= 1
        if pw.player.lives < 0:
            pw.player.lives = 0
        self.hudPlayersLives[pw.player.id].updateLives(pw.player.lives)

    def playerLosePoints(self, pw=None):
        pw.player.points -= 1000
        if pw.player.points < 0:
            pw.player.points = 0

    def playerCantMove(self, pw):
        pw.firingNotifier.emitTimer.stop()
        pw.movementNotifier.emitTimer.stop()
        playerCantMoveTimer = QTimer()
        playerCantMoveTimer.setTimerType(Qt.PreciseTimer)
        playerCantMoveTimer.timeout.connect(lambda: self.afterPlayerCantMove(pw))
        playerCantMoveTimer.setInterval(10000)
        playerCantMoveTimer.start()
        setattr(self, f"playerCantMoveTimer{pw.player.id}", playerCantMoveTimer)

    def afterPlayerCantMove(self, pw):
        pw.firingNotifier.emitTimer.start()
        pw.movementNotifier.emitTimer.start()
        timer = getattr(self, f"playerCantMoveTimer{pw.player.id}", None)
        if timer is not None:
            timer.stop()
            del timer

    def removeBaseShield(self, pw=None):
        for baseBlock in self.baseBlocks:
            baseBlock.isHidden = True
            self.scene.removeItem(baseBlock)
        self.removeBaseShieldTimer = QTimer()
        self.removeBaseShieldTimer.setTimerType(Qt.PreciseTimer)
        self.removeBaseShieldTimer.timeout.connect(self.afterRemoveBaseShield)
        self.removeBaseShieldTimer.setInterval(15000)
        self.removeBaseShieldTimer.start()

    def afterRemoveBaseShield(self):
        for baseBlock in self.baseBlocks:
            # this check is needed because upgrade base adds the base blocks to the scene
            # practically annulling the remove base effect
            if baseBlock.isHidden:
                baseBlock.isHidden = False
                self.scene.addItem(baseBlock)
        self.removeBaseShieldTimer.stop()
        del self.removeBaseShieldTimer

    def startNewStage(self, nextMap, nextStage, gameTypeData, playerData):
        self.currentMap = nextMap
        self.currentStage = nextStage
        self.gameTypeData = gameTypeData
        self.isOnline = gameTypeData.isOnline
        self.numOfPlayers = gameTypeData.numOfPlayers
        self.playerData = playerData
        self.__init_ui__()
        self.animationTimer.start()
        self.bulletTimer.start()
        for timer in self.enemyMovementTimers.values():
            timer.start()
        self.enemySpawnTimer.start()
        self.enemyShootingTimer.start()
        del self.gameOver
        self.gameOver = GameOver(self.config.gameOverTexture)
        self.gameOver.setPos(QPointF(150, self.fieldBottom + 50))
        self.gameOverEmitter.gameOverSignal.connect(self.gameOverHandler)
        self.generateEtd()
        self.generatePlayers()
        self.currentEnemyCnt = 0
        del self.deusExSpawner
        self.deusExSpawner = DeusExSpawner(self.scene, self.config, 15000, self.deusExActivate, self.deusExLocations)
