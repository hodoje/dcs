from PyQt5.QtCore import QObject, pyqtSignal, Qt, QTimer


class MovementNotifier(QObject):
    movementSignal = pyqtSignal(int)

    def __init__(self, timerInterval):
        super().__init__()

        self.keys = []
        self.is_done = False

        self.timerInterval = timerInterval
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.emit)
        self.timer.start(self.timerInterval)

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
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
            movementKeys = [k for k in keys if k == mainKey]
            if movementKeys:
                for x in movementKeys:
                    self.movementSignal.emit(x)
