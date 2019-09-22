from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from openal import *


class MovementSoundHandler:
    def __init__(self, config):
        self.config = config
        self.movementSignals = []
        # # moving sound
        self.movementSound = oalOpen(self.config.sounds["tankMoving"])
        self.movementSound.set_looping(True)
        self.movementSound.set_gain(30.0)
        # not moving sound
        self.nonMovementSound = oalOpen(self.config.sounds["tankNotMoving"])
        self.nonMovementSound.set_looping(True)
        self.nonMovementSound.set_gain(30.0)

        self.soundTimer = QTimer()
        self.soundTimer.setTimerType(Qt.PreciseTimer)
        self.soundTimer.timeout.connect(self.stopMovementSound)
        self.soundTimer.setInterval(100)

    def playMovementSound(self):
        if self.nonMovementSound is not None and self.movementSound is not None:
            if self.nonMovementSound.get_state() == AL_PLAYING:
                self.nonMovementSound.pause()
            if self.movementSound.get_state() == AL_PAUSED or \
                    self.movementSound.get_state() == AL_STOPPED or \
                    self.movementSound.get_state() == AL_INITIAL:
                self.movementSound.play()
        self.soundTimer.start()

    def stopMovementSound(self):
        if self.nonMovementSound is not None and self.movementSound is not None:
            if self.movementSound.get_state() == AL_PLAYING:
                self.movementSound.pause()
            if self.nonMovementSound.get_state() == AL_PAUSED or \
                    self.nonMovementSound.get_state() == AL_STOPPED or \
                    self.nonMovementSound.get_state() == AL_INITIAL:
                self.nonMovementSound.play()
                self.soundTimer.stop()

    def activate(self):
        self.nonMovementSound.play()
        self.soundTimer.start()

    def deactivate(self):
        self.movementSound.stop()
        self.nonMovementSound.stop()
        self.soundTimer.stop()
