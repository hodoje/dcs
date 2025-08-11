import datetime

from openal import *

from PyQt5 import sip
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QStackedWidget

import sys

from BasicElements.board import Board
from BasicElements.endOfStageOnePlayer import EndOfStageOnePlayer
from BasicElements.endOfStageTwoPlayers import EndOfStageTwoPlayers
from BasicElements.mainMenu import MainMenu
from BasicElements.winnerScreen import WinnerScreen
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
        self.initialLocalGameData.firstPlayerDetails = PlayerDetails(1, 0, 2, 1, True)
        self.initialLocalGameData.secondPlayerDetails = PlayerDetails(2, 0, 2, 1, True)
        # this will hold either local game data or online game data
        self.currentGameData = None
        self.endOfStageOnePlayer = None
        self.endOfStageTwoPlayers = None
        self.winnerScreen = WinnerScreen(self.config, 1, 0, 0, 0)
        self.winnerScreen.winnerAnimationOverSignal.connect(self.goToMainMenu)
        self.gameStartSound = oalOpen(self.config.sounds["gameStart"])
        self.newStageTimer = QTimer()
        self.newStageTimer.setTimerType(Qt.PreciseTimer)
        self.newStageTimer.setInterval(3000)
        self.newStageTimer.timeout.connect(self.newStage)
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.addWidget(self.mainMenu)
        self.central_widget.setCurrentWidget(self.mainMenu)
        self.central_widget.addWidget(self.winnerScreen)
        self.setWindowTitle("Battle City")
        self.setFixedSize(self.config.mainWindowSize["width"], self.config.mainWindowSize["height"])
        self.center()

    def startRound(self, gameData):
        if self.board is not None:
            sip.delete(self.board)
            del self.board
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
        self.central_widget.setCurrentWidget(self.board)
        self.gameStartSound.play()
        # reset player stats and end stage data if needed
        # placed here so if a player dies, the end stage will show the data
        # but from next round it will be showed as zeros
        if not gameData.firstPlayerDetails.isAlive:
            self.endOfStageTwoPlayers.resetFirstPlayerStats()
            gameData.firstPlayerDetails.points = 0
            gameData.firstPlayerDetails.lives = 0
            gameData.firstPlayerDetails.level = 0
            gameData.firstPlayerSeparateTankDetails.resetStats()
        if gameData.secondPlayerDetails is not None:
            if not gameData.secondPlayerDetails.isAlive:
                self.endOfStageTwoPlayers.resetSecondPlayerStats()
                gameData.secondPlayerDetails.points = 0
                gameData.secondPlayerDetails.lives = 0
                gameData.secondPlayerDetails.level = 0
                gameData.secondPlayerSeparateTankDetails.resetStats()

    def newStage(self):
        self.newStageTimer.stop()
        self.startRound(self.currentGameData)

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
        self.newStageTimer.start()

    def localGameOverHandler(self, localGameData: LocalGameData):
        if self.currentGameTypeData.numOfPlayers == 1:
            if self.endOfStageOnePlayer is None:
                self.endOfStageOnePlayer = EndOfStageOnePlayer(self.config,
                                                               self.currentStage,
                                                               localGameData.firstPlayerDetails.points,
                                                               localGameData.firstPlayerSeparateTankDetails)
                self.central_widget.addWidget(self.endOfStageOnePlayer)
            else:
                self.endOfStageOnePlayer.updateStageScreen(self.currentStage,
                                                           localGameData.firstPlayerDetails.points,
                                                           localGameData.firstPlayerSeparateTankDetails)
            self.central_widget.setCurrentWidget(self.endOfStageOnePlayer)
            self.endOfStageOnePlayer.animate()
            winner = self.getTheWinner(localGameData)
            self.winnerScreen.setWinner(winner,
                                        self.currentGameTypeData.numOfPlayers,
                                        localGameData.firstPlayerDetails.points,
                                        None)
            self.central_widget.setCurrentWidget(self.winnerScreen)
            self.winnerScreen.animate()
        else:
            if self.endOfStageTwoPlayers is None:
                self.endOfStageTwoPlayers = EndOfStageTwoPlayers(self.config,
                                                                 self.currentStage,
                                                                 localGameData.firstPlayerDetails.points,
                                                                 localGameData.firstPlayerSeparateTankDetails,
                                                                 localGameData.secondPlayerDetails.points,
                                                                 localGameData.secondPlayerSeparateTankDetails)
                self.central_widget.addWidget(self.endOfStageTwoPlayers)
            else:
                self.endOfStageTwoPlayers.updateStageScreen(self.currentStage,
                                                            localGameData.firstPlayerDetails.points,
                                                            localGameData.firstPlayerSeparateTankDetails,
                                                            localGameData.secondPlayerDetails.points,
                                                            localGameData.secondPlayerSeparateTankDetails)
            self.central_widget.setCurrentWidget(self.endOfStageTwoPlayers)
            self.endOfStageTwoPlayers.animate()
            winner = self.getTheWinner(localGameData)
            self.winnerScreen.setWinner(winner,
                                        self.currentGameTypeData.numOfPlayers,
                                        localGameData.firstPlayerDetails.points,
                                        localGameData.secondPlayerDetails.points)
            self.central_widget.setCurrentWidget(self.winnerScreen)
            self.winnerScreen.animate()

    def getTheWinner(self, localGameData):
        if self.currentGameTypeData.numOfPlayers == 1:
            return 1
        else:
            if localGameData.firstPlayerDetails.isAlive and localGameData.secondPlayerDetails.isAlive:
                if localGameData.firstPlayerDetails.points > localGameData.secondPlayerDetails.points:
                    return 1
                elif localGameData.firstPlayerDetails.points < localGameData.secondPlayerDetails.points:
                    return 2
                else:
                    return 0
            elif localGameData.firstPlayerDetails.isAlive:
                return 1
            elif localGameData.secondPlayerDetails.isAlive:
                return 2

    def goToMainMenu(self):
        # reset the game
        self.currentStage = 1
        self.currentMap = 1
        self.winnerScreen.resetItems()
        self.central_widget.setCurrentWidget(self.mainMenu)

    def onlineGameStageEndHandler(self, onlineGameStageEndData: OnlineGameData):
        print(f"This player points - {onlineGameStageEndData.playerDetails.points}")

    def onlineGameOverHandler(self, onlineGameData: OnlineGameData):
        print(onlineGameData)
        self.gameOverSound.play()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2 - 100))

    def closeEvent(self, *args, **kwargs):
        oalQuit()
        sip.delete(self)
        del self


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.processEvents()
    ex = MainWindow()
    sys.exit(app.exec())
