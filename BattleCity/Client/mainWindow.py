from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from board import Board
from config import Config
from mainMenu import MainMenu
from bridge import Bridge, MenuToMainWindowData, BoardToMainWindowData

import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.bridge = Bridge()
        self.bridge.menuToMainWindowSignal.connect(self.menuToMainWindowHandler)
        self.bridge.boardToMainWindowSignal.connect(self.boardToMainWindowSignalHandler)
        self.numOfMaps = len(self.config.maps)
        self.currentMap = 1
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.mainMenu = MainMenu(self.config, self.bridge)
        self.setCentralWidget(self.mainMenu)
        self.setWindowTitle("Battle City")
        self.setFixedSize(self.config.mainWindowSize["width"], self.config.mainWindowSize["height"])
        self.center()

    def menuToMainWindowHandler(self, menuToMainWindowData: MenuToMainWindowData):
        self.centralWidget().clearFocus()
        self.board = Board(self, self.config, self.currentMap, menuToMainWindowData)
        self.board.setFocusPolicy(Qt.StrongFocus)
        self.board.setFocus()
        self.changeView(self.board)

    def boardToMainWindowSignalHandler(self, boardToMainWindowData: BoardToMainWindowData):
        pass

    def changeView(self, view):
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
