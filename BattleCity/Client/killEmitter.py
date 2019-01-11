from PyQt5.QtCore import QObject, pyqtSignal
from enemy import Enemy


class KillEmitter(QObject):
    emitKillSignal = pyqtSignal(Enemy)

    def __init__(self):
        super().__init__()
