from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time
from PyQt5.QtCore import Qt


class KeyNotifier(QObject):
    movementSignal = pyqtSignal(int)
    firingSignal = pyqtSignal(int)

    def __init__(self, workerSleep):
        super().__init__()

        self.workerSleep = workerSleep
        self.keys = []
        self.is_done = False

        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.__work__)

    def start(self):
        self.thread.start()

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        self.keys.remove(key)

    def die(self):
        self.is_done = True
        self.thread.quit()

    @pyqtSlot()
    def __work__(self):
        while not self.is_done:
            keys = self.keys[:]
            if keys:
                # mainKey will be the first key that was registered in the next iteration after sleep
                # with that, moving in only one direction at a time will be possible
                mainKey = keys[0]
                firingKeys = [k for k in keys if k == Qt.Key_Space]
                if firingKeys:
                    for x in firingKeys:
                        self.firingSignal.emit(x)
                movementKeys = [k for k in keys if k == mainKey]
                if movementKeys:
                    for x in movementKeys:
                        self.movementSignal.emit(x)
                # some other possible solution
                #for k in keys:
                #    if mainKey == Qt.Key_Space:
                #        self.firingSignal.emit(k)
                #    if k == mainKey:
                #        self.movementSignal.emit(k)
                #    elif k == Qt.Key_Space:
                #        self.firingSignal.emit(k)
            time.sleep(self.workerSleep)
