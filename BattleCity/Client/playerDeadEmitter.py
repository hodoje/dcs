from PyQt5.QtCore import QObject, pyqtSignal


class PlayerDeadEmitter(QObject):
    playerDeadSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()