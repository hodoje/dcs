from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, Qt


class FiringNotifier(QObject):
    firingSignal = pyqtSignal(int)

    def __init__(self, timerInterval):
        super().__init__()

        self.keys = []
        self.canEmit = True

        self.timerInterval = timerInterval
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.__work__)
        self.timer.start(self.timerInterval)

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        self.keys.remove(key)

    #TODO polish up the firing - now a little bit polished, can probably do better
    @pyqtSlot()
    def __work__(self):
        if self.canEmit:
            for k in self.keys:
                self.firingSignal.emit(k)
