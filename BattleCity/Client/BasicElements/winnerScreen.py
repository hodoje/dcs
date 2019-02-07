from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from HUD.hudEndOfStageTotalPlayerPointsContainer import HudEndOfStageTotalPlayerPointsContainer
from HUD.hudHiscoreTotalPlayerPointsContainer import HudHiscoreTotalPlayerPointsContainer


class WinnerScreen(QGraphicsView):
    winnerAnimationOverSignal = pyqtSignal(int)

    def __init__(self, config, winnerPlayer, numOfPlayers, firstPlayerTotalPoints, secondPlayerTotalPoints):
        super().__init__()
        self.config = config
        self.winnerPlayer = winnerPlayer
        self.numOfPlayers = numOfPlayers
        self.firstPlayerTotalPoints = firstPlayerTotalPoints
        self.secondPlayerTotalPoints = secondPlayerTotalPoints
        self.player1AnimationItems = []
        self.player1CurrentAnimationItem = 0
        self.player2AnimationItems = []
        self.player2CurrentAnimationItem = 0
        self.winnerScreenTieAnimationItems = []
        self.winnerScreenTieCurrentAnimationItem = 0
        self.hiscoreAnimationItems = []
        self.hiscoreAnimationCurrentItem = 0
        self.hudHiscorePlayerTotalPointsList = []
        self.hudHiscorePlayerTotalPointsCurrentItem = 0
        self.amazingScoreSound = QSound(self.config.sounds["amazingScore"])
        self.__init_ui()

    def __init_ui(self):
        # set up the scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 650, 560)
        self.scene.setBackgroundBrush(Qt.darkGray)

        # set up the view
        self.setScene(self.scene)
        # these 10 additional pixels are for the margin
        self.setFixedSize(660, 570)
        # optimization
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setViewport(QGLWidget(QGLFormat()))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        for imgUrl in self.config.hiscoreAnimation:
            pixmap = QPixmap(imgUrl)
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setZValue(-1)
            pixmapItem.hide()
            self.scene.addItem(pixmapItem)
            self.hiscoreAnimationItems.append(pixmapItem)
        for imgUrl in self.config.winnerScreenTieAnimation:
            pixmap = QPixmap(imgUrl)
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setZValue(-1)
            pixmapItem.hide()
            self.scene.addItem(pixmapItem)
            self.winnerScreenTieAnimationItems.append(pixmapItem)
        for imgUrl in self.config.winnerScreenPlayer1Animation:
            pixmap = QPixmap(imgUrl)
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setZValue(-1)
            pixmapItem.hide()
            self.scene.addItem(pixmapItem)
            self.player1AnimationItems.append(pixmapItem)
        for imgUrl in self.config.winnerScreenPlayer2Animation:
            pixmap = QPixmap(imgUrl)
            pixmapItem = QGraphicsPixmapItem(pixmap)
            pixmapItem.setZValue(-1)
            pixmapItem.hide()
            self.scene.addItem(pixmapItem)
            self.player2AnimationItems.append(pixmapItem)

        # points animation used when single player is played
        self.hudHiscorePlayerTotalPointsWhite = HudHiscoreTotalPlayerPointsContainer(self.config, "white", self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsWhite.setPos(45, 235)
        self.hudHiscorePlayerTotalPointsWhite.hide()
        self.scene.addItem(self.hudHiscorePlayerTotalPointsWhite)
        self.hudHiscorePlayerTotalPointsList.append(self.hudHiscorePlayerTotalPointsWhite)

        self.hudHiscorePlayerTotalPointsGray = HudHiscoreTotalPlayerPointsContainer(self.config, "gray", self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsGray.setPos(45, 235)
        self.hudHiscorePlayerTotalPointsGray.hide()
        self.scene.addItem(self.hudHiscorePlayerTotalPointsGray)
        self.hudHiscorePlayerTotalPointsList.append(self.hudHiscorePlayerTotalPointsGray)

        self.hudHiscorePlayerTotalPointsDarkGray = HudHiscoreTotalPlayerPointsContainer(self.config, "darkGray", self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsDarkGray.setPos(45, 235)
        self.hudHiscorePlayerTotalPointsDarkGray.hide()
        self.scene.addItem(self.hudHiscorePlayerTotalPointsDarkGray)
        self.hudHiscorePlayerTotalPointsList.append(self.hudHiscorePlayerTotalPointsDarkGray)

        self.hudHiscorePlayerTotalPointsBlue = HudHiscoreTotalPlayerPointsContainer(self.config, "blue", self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsBlue.setPos(45, 235)
        self.hudHiscorePlayerTotalPointsBlue.hide()
        self.scene.addItem(self.hudHiscorePlayerTotalPointsBlue)
        self.hudHiscorePlayerTotalPointsList.append(self.hudHiscorePlayerTotalPointsBlue)

        self.hudHiscorePlayerTotalPointsDarkBlue = HudHiscoreTotalPlayerPointsContainer(self.config, "darkBlue", self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsDarkBlue.setPos(45, 235)
        self.hudHiscorePlayerTotalPointsDarkBlue.hide()
        self.scene.addItem(self.hudHiscorePlayerTotalPointsDarkBlue)
        self.hudHiscorePlayerTotalPointsList.append(self.hudHiscorePlayerTotalPointsDarkBlue)

        # used when there are two players playing
        self.hudFirstPlayerTotalPoints = HudEndOfStageTotalPlayerPointsContainer(self.config, self.firstPlayerTotalPoints)
        self.hudFirstPlayerTotalPoints.setPos(85, 205)
        self.hudFirstPlayerTotalPoints.hide()
        self.scene.addItem(self.hudFirstPlayerTotalPoints)

        self.hudSecondPlayerTotalPoints = HudEndOfStageTotalPlayerPointsContainer(self.config, self.secondPlayerTotalPoints)
        self.hudSecondPlayerTotalPoints.setPos(450, 205)
        self.hudSecondPlayerTotalPoints.hide()
        self.scene.addItem(self.hudSecondPlayerTotalPoints)

    def animate(self):
        self.animationTimer = QTimer()
        self.animationTimer.setTimerType(Qt.PreciseTimer)
        self.animationTimer.setInterval(10)
        self.animationTimer.timeout.connect(self.checkForAnimationEnd)
        self.animationTimer.start()
        self.amazingScoreSound.play()

    def checkForAnimationEnd(self):
        if self.numOfPlayers == 1:
            if not self.amazingScoreSound.isFinished():
                self.hiscoreAnimationItems[self.hiscoreAnimationCurrentItem].hide()
                self.hiscoreAnimationCurrentItem += 1
                if self.hiscoreAnimationCurrentItem == len(self.hiscoreAnimationItems):
                    self.hiscoreAnimationCurrentItem = 0
                self.hiscoreAnimationItems[self.hiscoreAnimationCurrentItem].show()

                self.hudHiscorePlayerTotalPointsList[self.hudHiscorePlayerTotalPointsCurrentItem].hide()
                self.hudHiscorePlayerTotalPointsCurrentItem += 1
                if self.hudHiscorePlayerTotalPointsCurrentItem == len(self.hudHiscorePlayerTotalPointsList):
                    self.hudHiscorePlayerTotalPointsCurrentItem = 0
                self.hudHiscorePlayerTotalPointsList[self.hudHiscorePlayerTotalPointsCurrentItem].show()
            else:
                self.animationTimer.stop()
                self.winnerAnimationOverSignal.emit(1)
        else:
            self.hudFirstPlayerTotalPoints.show()
            self.hudSecondPlayerTotalPoints.show()
            if self.winnerPlayer == 1:
                if not self.amazingScoreSound.isFinished():
                    self.player1AnimationItems[self.player1CurrentAnimationItem].hide()
                    self.player1CurrentAnimationItem += 1
                    if self.player1CurrentAnimationItem == len(self.player1AnimationItems):
                        self.player1CurrentAnimationItem = 0
                    self.player1AnimationItems[self.player1CurrentAnimationItem].show()
                else:
                    self.animationTimer.stop()
                    self.winnerAnimationOverSignal.emit(1)
            elif self.winnerPlayer == 2:
                if not self.amazingScoreSound.isFinished():
                    self.player2AnimationItems[self.player2CurrentAnimationItem].hide()
                    self.player2CurrentAnimationItem += 1
                    if self.player2CurrentAnimationItem == len(self.player2AnimationItems):
                        self.player2CurrentAnimationItem = 0
                    self.player2AnimationItems[self.player2CurrentAnimationItem].show()
                else:
                    self.animationTimer.stop()
                    self.winnerAnimationOverSignal.emit(1)
            else:
                if not self.amazingScoreSound.isFinished():
                    self.winnerScreenTieAnimationItems[self.winnerScreenTieCurrentAnimationItem].hide()
                    self.winnerScreenTieCurrentAnimationItem += 1
                    if self.winnerScreenTieCurrentAnimationItem == len(self.winnerScreenTieAnimationItems):
                        self.winnerScreenTieCurrentAnimationItem = 0
                    self.winnerScreenTieAnimationItems[self.winnerScreenTieCurrentAnimationItem].show()
                else:
                    self.animationTimer.stop()
                    self.winnerAnimationOverSignal.emit(1)

    def resetItems(self):
        self.player1CurrentAnimationItem = 0
        self.player2CurrentAnimationItem = 0
        self.winnerScreenTieCurrentAnimationItem = 0
        self.hiscoreAnimationCurrentItem = 0
        self.hudHiscorePlayerTotalPointsCurrentItem = 0
        for item in self.player1AnimationItems:
            item.hide()
        for item in self.player2AnimationItems:
            item.hide()
        for item in self.winnerScreenTieAnimationItems:
            item.hide()
        for item in self.hiscoreAnimationItems:
            item.hide()
        for item in self.hudHiscorePlayerTotalPointsList:
            item.hide()
        self.hudFirstPlayerTotalPoints.hide()
        self.hudSecondPlayerTotalPoints.hide()

    def setWinner(self, winner, numOfPlayers, firstPlayerTotalPoints, secondPlayerTotalPoints=None):
        self.winnerPlayer = winner
        self.numOfPlayers = numOfPlayers
        self.firstPlayerTotalPoints = firstPlayerTotalPoints
        if secondPlayerTotalPoints is not None:
            self.secondPlayerTotalPoints = secondPlayerTotalPoints
        else:
            self.secondPlayerTotalPoints = 0
        self.hudFirstPlayerTotalPoints.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.hudSecondPlayerTotalPoints.updateTotalPlayerPoints(self.secondPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsWhite.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsGray.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsDarkGray.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsBlue.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.hudHiscorePlayerTotalPointsDarkBlue.updateTotalPlayerPoints(self.firstPlayerTotalPoints)

