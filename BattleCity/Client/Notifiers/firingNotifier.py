from PyQt5.QtCore import QObject, pyqtSignal, QTimer, Qt, QThread


class FiringNotifier(QObject):
    firingSignal = pyqtSignal(int)

    def __init__(self, timerInterval):
        super().__init__()
        self.keys = []
        # will be false when the player announces he can't shoot
        # the board sets this flag according to player.announceCanShoot function
        self.canEmit = True

        self.thread = QThread()
        self.timerInterval = timerInterval
        self.emitTimer = QTimer()
        self.emitTimer.setTimerType(Qt.PreciseTimer)
        self.emitTimer.timeout.connect(self.emit)
        self.emitTimer.setInterval(self.timerInterval)
        self.moveToThread(self.thread)
        self.thread.started.connect(self.emitTimer.start)
        self.thread.start()

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        if key in self.keys:
            self.keys.remove(key)

    def emit(self):
        if self.canEmit:
            for k in self.keys:
                self.firingSignal.emit(k)
