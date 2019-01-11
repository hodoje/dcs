import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from board import Board


class GameStart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.board = Board()
        self.setCentralWidget(self.board)
        self.setWindowTitle("Battle City")
        self.setFixedSize(660, 570)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2 - 100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameStart()
    sys.exit(app.exec())
