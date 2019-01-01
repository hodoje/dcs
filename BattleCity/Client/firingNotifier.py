from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt


class FiringNotifier(QObject):
    firingSignal = pyqtSignal(int)

    def __init__(self, timerInterval):
        super().__init__()

        self.keys = []
        # will be false when the player announces he can't shoot
        # the board sets this flag according to player.announceCanShoot function
        self.canEmit = True

        self.timerInterval = timerInterval
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.emitKey)
        self.timer.start(self.timerInterval)

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        self.keys.remove(key)

    def emitKey(self):
        if self.canEmit:
            for k in self.keys:
                self.firingSignal.emit(k)
