from PyQt5.QtCore import QObject, pyqtSignal


class GameOverEmitter(QObject):
    gameOverSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
