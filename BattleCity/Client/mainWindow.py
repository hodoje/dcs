from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget

import sys

from BasicElements.board import Board
from BasicElements.mainMenu import MainMenu
from Bridge.bridge import Bridge
from Bridge.gameTypeData import GameTypeData
from Bridge.localGameData import LocalGameData
from Bridge.onlineGameData import OnlineGameData
from Config.config import Config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.bridge = Bridge()
        self.bridge.gamePickSignal.connect(self.gamePickHandler)
        self.bridge.localGameStageEndSignal.connect(self.localGameStageEndHandler)
        self.bridge.onlineGameStageEndSignal.connect(self.onlineGameStageEndHandler)
        self.numOfMaps = len(self.config.maps)
        self.currentMap = 1
        self.gameStartSound = QSoundEffect(self)
        self.gameStartSound.setSource(QUrl.fromLocalFile(self.config.sounds["gameStart"]))
        self.gameOverSound = QSoundEffect(self)
        self.gameOverSound.setSource(QUrl.fromLocalFile(self.config.sounds["gameOver"]))
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.mainMenu = MainMenu(self.config, self.bridge)
        self.setCentralWidget(self.mainMenu)
        self.setWindowTitle("Battle City")
        self.setFixedSize(self.config.mainWindowSize["width"], self.config.mainWindowSize["height"])
        self.center()

    def gamePickHandler(self, gameTypeData: GameTypeData):
        self.gameStartSound.play()
        self.board = Board(self, self.config, self.currentMap, self.bridge, gameTypeData.isOnline, gameTypeData.numOfPlayers)
        self.changeView(self.board)

    def localGameStageEndHandler(self, localGameStageEndData: LocalGameData):
        print(localGameStageEndData.firstPlayerDetails)
        if localGameStageEndData.secondPlayerDetails is not None:
            print(localGameStageEndData.secondPlayerDetails)
        self.gameOverSound.play()

    def onlineGameStageEndHandler(self, onlineGameStageEndData: OnlineGameData):
        pass

    def changeView(self, view):
        self.centralWidget().clearFocus()
        view.setFocusPolicy(Qt.StrongFocus)
        view.setFocus()
        self.setCentralWidget(view)

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2 - 100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec())
