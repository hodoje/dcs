import random

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtMultimedia import QSound

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
        self.positivePulseSound = QSound(self.config.sounds["nondangerZone"])
        self.negativePulseSound = QSound(self.config.sounds["dangerZone"])
        self.positiveEndingSound = QSound(self.config.sounds["nondangerZoneEnd"])
        self.negativeEndingSound = QSound(self.config.sounds["dangerZoneEnd"])
        self.spawnTimer = QTimer()
        self.spawnTimer.setTimerType(Qt.PreciseTimer)
        self.spawnTimer.timeout.connect(self.spawn)
        self.spawnTimer.setInterval(self.interval)
        self.spawnTimer.start()

    def spawn(self, isPositive=False):
        deusExType = None
        deusEx = None
        if isPositive:
            deusExType = DeusExTypes.POSITIVE
            deusEx = DeusEx(self.config, deusExType, self.positivePulseSound, self.positiveEndingSound)
        else:
            deusExType = DeusExTypes.NEGATIVE
            deusEx = DeusEx(self.config, deusExType, self.negativePulseSound, self.negativeEndingSound)
        deusEx.deusExActivateSignal.connect(self.action)
        deusEx.setZValue(2)
        deusEx.setPos(random.choice(self.locations))
        self.scene.addItem(deusEx)
        # self.spawnTimer.stop()
