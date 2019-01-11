from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem

from firingNotifier import FiringNotifier
from killEmitter import KillEmitter
from movementNotifier import MovementNotifier
from player import Player
from enemy import Enemy
from block import Block
import random


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()

        # set up player and enemy details
        self.playerColors = ["yellow", "green"]
        self.numOfPlayers = 2
        self.enemyColors = ["gray"]
        self.enemyTypes = [5, 6, 7, 8]
        self.enemies = []
        self.enemySpawnInterval = 3000
        self.enemiesPerLevel = {1: 15, 2: 20, 3: 25, 4: 30, 5: 35}
        self.currentLevel = 1
        self.currentEnemyCnt = 0
        self.currentEnemyMaxCnt = self.enemiesPerLevel[self.currentLevel]
        self.maxEnemiesCurrentlyAlive = 6
        self.enemiesCurrentlyAlive = 0
        # all enemies will react to this timer timeout
        self.enemyTimer = QTimer()
        self.enemyTimer.setTimerType(Qt.PreciseTimer)
        self.enemyTimer.start(10)

        # all bullets will react to this timer timeout
        self.bulletTimer = QTimer()
        self.bulletTimer.setTimerType(Qt.PreciseTimer)
        self.bulletTimer.start(10)

        # player1 keys
        self.firingKey = Qt.Key_Space
        self.movementKeys = {"Up": Qt.Key_Up, "Down": Qt.Key_Down, "Left": Qt.Key_Left, "Right": Qt.Key_Right}

        # player2 keys
        self.firingKey1 = Qt.Key_J
        self.movementKeys1 = {"Up": Qt.Key_W, "Down": Qt.Key_S, "Left": Qt.Key_A, "Right": Qt.Key_D}

        # each player and enemy will have this emitter passed to them
        # and will give it to each bullet so the bullet can signal when an enemy has been killed
        self.killEmitter = KillEmitter()
        self.killEmitter.emitKillSignal.connect(self.enemyKiller)

        self.__init_ui__()
        self.generatePlayers()
        self.setUpPlayerSlots()

        # random enemy positions
        # 40 is the size of the enemy tank
        self.randomEnemyPositions = [
            self.field.x()
            # self.field.x() + self.field.width() / 2 + 0.5,
            # self.field.x() + self.field.width() - 38
        ]

        self.enemySpawnTimer = QTimer()
        self.enemySpawnTimer.setTimerType(Qt.PreciseTimer)
        self.enemySpawnTimer.timeout.connect(self.generateEnemy)
        self.enemySpawnTimer.start(self.enemySpawnInterval)

    # INITIALIZATION
    def __init_ui__(self):
        # set up the scene
        self.scene = QGraphicsScene()
        # first two zeros are x and y in regard to the containing view
        # this resolution gives us 15 rows and 20 columns for object of size 40x40px
        self.scene.setSceneRect(0, 0, 800, 700)
        self.scene.setBackgroundBrush(Qt.darkGray)

        # set up the view
        self.setScene(self.scene)
        # these 10 additional pixels are for the margin
        self.setFixedSize(810, 710)
        # optimization
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setViewport(QGLWidget(QGLFormat()))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # set up the field
        self.field = QGraphicsRectItem(0, 0, 640, 640)
        self.field.setZValue(-1)
        self.field.setBrush(Qt.black)
        self.field.setX(40)
        self.field.setY(25)
        self.scene.addItem(self.field)

    def generatePlayers(self):
        for i in range(self.numOfPlayers):
            if i == 0:
                # add the player on the scene
                self.player = Player(
                    self.playerColors[i],
                    self.firingKey,
                    self.movementKeys,
                    self.field,
                    self.killEmitter,
                    self.bulletTimer,
                    Enemy)
                self.scene.addItem(self.player)
                # set position of the player -> down and center (last 10 pixels in height argument are for the margin)
                self.player.setPos(self.field.boundingRect().width() / 2 - self.player.boundingRect().width() / 2,
                                   self.field.boundingRect().height() - self.player.boundingRect().height())

            elif i == 1:
                self.player1 = Player(
                    self.playerColors[i],
                    self.firingKey1,
                    self.movementKeys1,
                    self.field,
                    self.killEmitter,
                    self.bulletTimer,
                    Enemy)
                self.scene.addItem(self.player1)
                # set position of the player -> down and center (last 10 pixels in height argument are for the margin)
                self.player1.setPos(self.field.boundingRect().width() / 2 - self.player1.boundingRect().width() / 2 + 0.5 + 100,
                                    self.field.boundingRect().height() - self.player1.boundingRect().height())

    def setUpPlayerSlots(self):
        for i in range(self.numOfPlayers):
            if i == 0:
                self.movementNotifier = MovementNotifier(10)
                self.movementNotifier.movementSignal.connect(self.updatePosition)

                self.firingNotifier = FiringNotifier(50)
                self.firingNotifier.firingSignal.connect(self.fireCanon)

                self.player.canShootSignal.connect(self.allowFiring)

            elif i == 1:
                self.movementNotifier1 = MovementNotifier(10)
                self.movementNotifier1.movementSignal.connect(self.updatePosition)

                self.firingNotifier1 = FiringNotifier(50)
                self.firingNotifier1.firingSignal.connect(self.fireCanon1)

                self.player1.canShootSignal.connect(self.allowFiring1)
    ###############################################################################

    def generateEnemy(self):
        if self.currentEnemyCnt != self.currentEnemyMaxCnt:
            if self.enemiesCurrentlyAlive < self.maxEnemiesCurrentlyAlive:
                # enemy pos
                posX1 = random.choice(self.randomEnemyPositions)
                posY1 = self.field.y()
                posX2 = posX1 + self.player.texture1.width()
                posY2 = posY1 + self.player.texture1.height()
                middleX = posX1 + self.player.texture1.width() / 2
                middleY = posY1 + self.player.texture1.height() / 2
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
                self.currentEnemyCnt += 1
                self.enemiesCurrentlyAlive += 1
                print(self.enemiesCurrentlyAlive)
                enemyType = random.choice(self.enemyTypes)
                if enemyType == 6:
                    movementPace = 1
                else:
                    movementPace = 1
                enemy = Enemy(
                    enemyType,
                    self.enemyColors[0],
                    movementPace,
                    10,
                    2000,
                    self.field,
                    self.enemyTimer,
                    self.bulletTimer,
                    Player)
                self.scene.addItem(enemy)
                enemy.setPos(posX1, posY1)
                self.enemies.append(enemy)

    def keyPressEvent(self, event):
        key = event.key()
        if key == self.firingKey:
            self.firingNotifier.add_key(key)
        elif key in self.movementKeys.values():
            self.movementNotifier.add_key(key)
        elif key == self.firingKey1:
            self.firingNotifier1.add_key(key)
        elif key in self.movementKeys1.values():
            self.movementNotifier1.add_key(key)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == self.firingKey:
            self.firingNotifier.remove_key(key)
        elif key in self.movementKeys.values():
            self.movementNotifier.remove_key(key)
        elif key == self.firingKey1:
            self.firingNotifier1.remove_key(key)
        elif key in self.movementKeys1.values():
            self.movementNotifier1.remove_key(key)

    # player1 and player2 slot
    def updatePosition(self, key):
        if key in self.movementKeys.values():
            self.player.updatePosition(key)
        if key in self.movementKeys1.values():
            self.player1.updatePosition(key)

    # player1 slots ##########################
    def fireCanon(self, key):
        self.player.shoot(key)

    def allowFiring(self, canEmit):
        self.firingNotifier.canEmit = canEmit
    ##########################################

    # player2 slots ##########################
    def fireCanon1(self, key):
        self.player1.shoot(key)

    def allowFiring1(self, canEmit):
        self.firingNotifier1.canEmit = canEmit
    ##########################################

    def enemyKiller(self, enemy):
        self.enemies.remove(enemy)
        self.enemiesCurrentlyAlive -= 1
