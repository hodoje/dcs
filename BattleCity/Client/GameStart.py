import sys
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsScene, QMainWindow, QDesktopWidget

from Client.Board import Board
from Client.Tank import Tank


class GameStart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui__()
        self.show()

    def __init_ui__(self):
        self.board = Board()
        self.setCentralWidget(self.board)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameStart()
    sys.exit(app.exec())
