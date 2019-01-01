from PyQt5.QtCore import QThread, QObject, pyqtSignal
import time


class MovementNotifier(QObject):
    movementSignal = pyqtSignal(int)

    def __init__(self, workerSleep):
        super().__init__()

        self.workerSleep = workerSleep
        self.keys = []
        self.is_done = False

        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.emitKey)

    def start(self):
        self.thread.start()

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        self.keys.remove(key)

    def die(self):
        self.is_done = True
        self.thread.quit()

    def emitKey(self):
        while not self.is_done:
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
            time.sleep(self.workerSleep)
