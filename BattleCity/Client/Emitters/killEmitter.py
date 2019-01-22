from PyQt5.QtCore import QObject, pyqtSignal

from Emitters.killEmitData import KillEmitData


class KillEmitter(QObject):
    emitKillSignal = pyqtSignal(KillEmitData)

    def __init__(self):
        super().__init__()
