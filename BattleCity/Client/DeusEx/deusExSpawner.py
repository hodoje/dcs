import random

from PyQt5.QtCore import QTimer, Qt

from DeusEx.deusex import DeusEx
from DeusEx.deusexTypes import DeusExTypes


class DeusExSpawner:
    def __init__(self, scene, config, interval, action, locations):
        self.scene = scene
        self.config = config
        self.interval = interval
        self.action = action
        self.locations = locations
        self.deusExTypesList = [DeusExTypes.POSITIVE, DeusExTypes.NEGATIVE]
        self.spawnTimer = QTimer()
        self.spawnTimer.setTimerType(Qt.PreciseTimer)
        self.spawnTimer.timeout.connect(self.spawn)
        self.spawnTimer.setInterval(self.interval)
        self.spawnTimer.start()

    def spawn(self, isPositive=False):
        deusExType = None
        if isPositive:
            deusExType = DeusExTypes.POSITIVE
        else:
            deusExType = DeusExTypes.NEGATIVE
        deusEx = DeusEx(self.config, deusExType)
        deusEx.deusExActivateSignal.connect(self.action)
        deusEx.setZValue(2)
        self.scene.addItem(deusEx)
        deusEx.setPos(random.choice(self.locations))
        self.spawnTimer.stop()
