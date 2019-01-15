from PyQt5.QtCore import QObject, pyqtSignal


class KillEmitData:
    def __init__(self, shooterId, targetId, targetType):
        self.shooterId = shooterId
        self.targetId = targetId
        self.targetType = targetType


class KillEmitter(QObject):
    emitKillSignal = pyqtSignal(KillEmitData)

    def __init__(self):
        super().__init__()
