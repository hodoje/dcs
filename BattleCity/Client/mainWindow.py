from PyQt5 import sip
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QStackedWidget

import sys

from BasicElements.board import Board
from BasicElements.endOfStageOnePlayer import EndOfStageOnePlayer
from BasicElements.endOfStageTwoPlayers import EndOfStageTwoPlayers
from BasicElements.mainMenu import MainMenu
from Bridge.bridge import Bridge
from Bridge.gameTypeData import GameTypeData
from Bridge.localGameData import LocalGameData
from Bridge.onlineGameData import OnlineGameData
from Config.config import Config
from Player.playerDetails import PlayerDetails
from Player.separateTankPoints import SeparateTankDetails


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.bridge = Bridge()
        self.bridge.gamePickSignal.connect(self.gamePickHandler)
        self.bridge.localGameStageEndSignal.connect(self.localGameStageEndHandler)
        self.bridge.onlineGameStageEndSignal.connect(self.onlineGameStageEndHandler)
        self.bridge.localGameOverSignal.connect(self.localGameOverHandler)
        self.bridge.onlineGameOverSignal.connect(self.onlineGameOverHandler)
        self.mainMenu = MainMenu(self.config, self.bridge)
        self.board = None
        self.numOfMaps = len(self.config.maps)
        self.currentMap = 1
        self.currentStage = 1
        self.currentGameTypeData = None
        # this holds initial data for a local game
        self.initialLocalGameData = LocalGameData()
        self.initialLocalGameData.firstPlayerDetails = PlayerDetails(1, 0, 2, 1)
        self.initialLocalGameData.secondPlayerDetails = PlayerDetails(2, 0, 2, 1)
        # this will hold either local game data or online game data
        self.currentGameData = None
        self.endOfStageOnePlayer = None
        self.endOfStageTwoPlayers = None
        self.gameStartSound = QSoundEffect(self)
        self.gameStartSound.setSource(QUrl.fromLocalFile(self.config.sounds["gameStart"]))
        self.gameOverSound = QSoundEffect(self)
        self.gameOverSound.setSource(QUrl.fromLocalFile(self.config.sounds["gameOver"]))
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.mainMenu)
        self.central_widget.setCurrentWidget(self.mainMenu)
        self.setWindowTitle("Battle City")
        self.setFixedSize(self.config.mainWindowSize["width"], self.config.mainWindowSize["height"])
        self.center()

    def changeView(self, view):
        view.setFocusPolicy(Qt.StrongFocus)
        view.setFocus()

    def startRound(self, gameData):
        if self.board is None:
            self.board = Board(self,
                               self.config,
                               self.currentMap,
                               self.currentStage,
                               self.bridge,
                               self.currentGameTypeData,
                               gameData)
            self.board.setFocusPolicy(Qt.StrongFocus)
            self.board.setFocus()
            self.central_widget.addWidget(self.board)
        else:
            self.board.setFocusPolicy(Qt.StrongFocus)
            self.board.setFocus()
            self.board.startNewStage(self.currentMap, self.currentStage, gameData)
        self.central_widget.setCurrentWidget(self.board)
        self.gameStartSound.play()

    def updateMapAndStage(self):
        if self.currentMap == self.numOfMaps:
            self.currentMap = 1
        else:
            self.currentMap += 1
        self.currentStage += 1

    def gamePickHandler(self, gameTypeData: GameTypeData):
        self.currentGameTypeData = gameTypeData
        if self.currentGameTypeData.isOnline:
            pass
        else:
            self.startRound(self.initialLocalGameData)

    def localGameStageEndHandler(self, localGameStageEndData: LocalGameData):
        print("Player 1:")
        print(f"    ID - {localGameStageEndData.firstPlayerDetails.id}")
        print(f"    Points - {localGameStageEndData.firstPlayerDetails.points}")
        print(f"    Lives - {localGameStageEndData.firstPlayerDetails.lives}")
        print(f"    Level - {localGameStageEndData.firstPlayerDetails.level}")
        if localGameStageEndData.secondPlayerDetails is not None:
            print("Player 2:")
            print(f"    ID - {localGameStageEndData.secondPlayerDetails.id}")
            print(f"    Points - {localGameStageEndData.secondPlayerDetails.points}")
            print(f"    Lives - {localGameStageEndData.secondPlayerDetails.lives}")
            print(f"    Level - {localGameStageEndData.secondPlayerDetails.level}")
        if self.currentGameTypeData.numOfPlayers == 1:
            if self.endOfStageOnePlayer is None:
                self.endOfStageOnePlayer = EndOfStageOnePlayer(self.config,
                                                               self.currentStage,
                                                               localGameStageEndData.firstPlayerDetails.points,
                                                               localGameStageEndData.firstPlayerSeparateTankDetails)
                self.central_widget.addWidget(self.endOfStageOnePlayer)
            else:
                self.endOfStageOnePlayer.updateStageScreen(self.currentStage,
                                                           localGameStageEndData.firstPlayerDetails.points,
                                                           localGameStageEndData.firstPlayerSeparateTankDetails)
            self.central_widget.setCurrentWidget(self.endOfStageOnePlayer)
            self.endOfStageOnePlayer.animate()
        else:
            if self.endOfStageTwoPlayers is None:
                self.endOfStageTwoPlayers = EndOfStageTwoPlayers(self.config,
                                                                 self.currentStage,
                                                                 localGameStageEndData.firstPlayerDetails.points,
                                                                 localGameStageEndData.firstPlayerSeparateTankDetails,
                                                                 localGameStageEndData.secondPlayerDetails.points,
                                                                 localGameStageEndData.secondPlayerSeparateTankDetails)
                self.central_widget.addWidget(self.endOfStageTwoPlayers)
            else:
                self.endOfStageTwoPlayers.updateStageScreen(self.currentStage,
                                                            localGameStageEndData.firstPlayerDetails.points,
                                                            localGameStageEndData.firstPlayerSeparateTankDetails,
                                                            localGameStageEndData.secondPlayerDetails.points,
                                                            localGameStageEndData.secondPlayerSeparateTankDetails)
            self.central_widget.setCurrentWidget(self.endOfStageTwoPlayers)
            self.endOfStageTwoPlayers.animate()
        self.updateMapAndStage()
        self.currentGameData = localGameStageEndData
        self.newStageTimer = QTimer()
        self.newStageTimer.setTimerType(Qt.PreciseTimer)
        self.newStageTimer.setInterval(3000)
        self.newStageTimer.timeout.connect(self.newStage)
        self.newStageTimer.start()

    def newStage(self):
        self.newStageTimer.stop()
        self.startRound(self.currentGameData)

    def onlineGameStageEndHandler(self, onlineGameStageEndData: OnlineGameData):
        print(f"This player points - {onlineGameStageEndData.playerDetails.points}")

    def localGameOverHandler(self, localGameData: LocalGameData):
        print(localGameData)
        self.gameOverSound.play()

    def onlineGameOverHandler(self, onlineGameData: OnlineGameData):
        print(onlineGameData)
        self.gameOverSound.play()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2 - 100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    ex = MainWindow()
    sys.exit(app.exec())
