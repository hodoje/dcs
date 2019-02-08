from openal import *

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer, QThread


class MovementNotifier(QObject):
    movementSignal = pyqtSignal(int)

    def __init__(self, timerInterval):
        super().__init__()
        self.keys = []

        self.thread = QThread()
        self.timerInterval = timerInterval
        self.emitTimer = QTimer()
        self.emitTimer.setTimerType(Qt.PreciseTimer)
        self.emitTimer.timeout.connect(self.emit)
        self.moveToThread(self.thread)
        self.emitTimer.setInterval(self.timerInterval)
        self.thread.started.connect(self.emitTimer.start)
        self.thread.start()

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        if key in self.keys:
            self.keys.remove(key)

    def emit(self):
        keys = self.keys[:]
        if keys:
            # mainKey will be the first key that was registered
            # if any other key was pressed they will be omitted
            # with that, moving only in one direction at a time will be possible
            # NOTE: when holding a key (although add_key is called on the board, only one element will be
            # in the self.keys list)
            mainKey = keys[0]
            self.movementSignal.emit(mainKey)
