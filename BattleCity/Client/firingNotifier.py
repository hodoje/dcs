from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QWaitCondition, QMutex
import time


class FiringNotifier(QObject):
    firingSignal = pyqtSignal(int)

    def __init__(self, workerSleep):
        super().__init__()

        self.workerSleep = workerSleep
        self.keys = []
        self.is_done = False

        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.__work__)

        self.canEmit = True

    def start(self):
        self.thread.start()

    def add_key(self, key):
        self.keys.append(key)

    def remove_key(self, key):
        self.keys.remove(key)

    def die(self):
        self.is_done = True
        self.thread.quit()

    #TODO polish up the firing
    @pyqtSlot()
    def __work__(self):
        while not self.is_done:
            if self.canEmit:
                for k in self.keys:
                    self.firingSignal.emit(k)
            time.sleep(self.workerSleep)
