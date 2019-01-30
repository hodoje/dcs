from PyQt5.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QRadialGradient, QColor
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QGraphicsObject

from DeusEx.deusExSignalData import DeusExSignalData
from DeusEx.deusexTypes import DeusExTypes


class DeusEx(QGraphicsObject):
    deusExActivateSignal = pyqtSignal(DeusExSignalData)

    def __init__(self, config, type):
        super().__init__()
        self.type = type
        self.config = config
        self.width = 200
        self.height = 200
        self.m_boundingRect = QRectF(0, 0, self.width, self.height)
        self.m_painterPath = QPainterPath()
        self.m_painterPath.addEllipse(self.m_boundingRect)
        # radial gradient settings
        self.rgcx = self.m_boundingRect.center().x()
        self.rgcy = self.m_boundingRect.center().y()
        self.rgMinRadius = 50
        self.rgMaxRadius = 300
        self.rgCurrentRadius = 50
        self.rgfx = self.rgcx
        self.rgfy = self.rgcy
        self.rg = QRadialGradient(self.rgcx, self.rgcy, self.rgCurrentRadius, self.rgfx, self.rgfy)
        if self.type is DeusExTypes.POSITIVE:
            firstClr = QColor(Qt.green)
            firstClr.setAlphaF(0.7)
            secondClr = QColor(Qt.darkGreen)
            secondClr.setAlphaF(0.7)
            self.rg.setColorAt(0.0, firstClr)
            self.rg.setColorAt(1.0, secondClr)
        else:
            firstClr = QColor(Qt.red)
            firstClr.setAlphaF(0.7)
            secondClr = QColor(Qt.darkRed)
            secondClr.setAlphaF(0.7)
            self.rg.setColorAt(0.0, firstClr)
            self.rg.setColorAt(1.0, secondClr)
        # pulsing sound
        if self.type is DeusExTypes.POSITIVE:
            self.pulseSound = QSound(self.config.sounds["nondangerZone"])
        else:
            self.pulseSound = QSound(self.config.sounds["dangerZone"])
        # activate
        if self.type is DeusExTypes.POSITIVE:
            self.endingSound = QSound(self.config.sounds["nondangerZoneEnd"])
        else:
            self.endingSound = QSound(self.config.sounds["dangerZoneEnd"])
        # pulsing timer
        self.pulseTimer = QTimer()
        self.pulseTimer.setTimerType(Qt.PreciseTimer)
        self.pulseTimer.timeout.connect(self.pulse)
        self.pulseTimer.start(100)
        # pre activate timer
        self.preActivateTimer = QTimer()
        self.preActivateTimer.setTimerType(Qt.PreciseTimer)
        self.preActivateTimer.timeout.connect(self.preActivate)
        if self.type is DeusExTypes.POSITIVE:
            self.preActivateTimer.start(7000)
        else:
            self.preActivateTimer.start(3500)
        # activate timer
        self.activateTimer = QTimer()
        self.activateTimer.setTimerType(Qt.PreciseTimer)
        self.activateTimer.timeout.connect(self.endingSoundFinished)

    def boundingRect(self):
        return self.m_boundingRect

    def shape(self):
        return self.m_painterPath

    def paint(self, QPainter, QStyleOptionGraphicsItem, widget=None):
        pen = QPen()
        if self.type is DeusExTypes.POSITIVE:
            pen.setColor(Qt.darkGreen)
        else:
            pen.setColor(Qt.darkRed)
        brush = QBrush(self.rg)
        QPainter.setPen(pen)
        QPainter.setBrush(brush)
        QPainter.drawEllipse(self.m_boundingRect)

    def pulse(self):
        if self.rgCurrentRadius == 50:
            self.pulseSound.play()
        self.rgCurrentRadius += 20
        self.rg.setCenterRadius(self.rgCurrentRadius)
        if self.rgCurrentRadius >= self.rgMaxRadius:
            self.rgCurrentRadius = self.rgMinRadius

    def preActivate(self):
        firstClr = QColor(Qt.yellow)
        firstClr.setAlphaF(0.7)
        secondClr = QColor(Qt.darkYellow)
        secondClr.setAlphaF(0.7)
        self.rg.setColorAt(0.0, firstClr)
        self.rg.setColorAt(1.0, secondClr)
        self.pulseSound.stop()
        self.pulseTimer.timeout.disconnect()
        self.preActivateTimer.timeout.disconnect()
        self.pulseTimer.stop()
        self.preActivateTimer.stop()

        # activate
        self.endingSound.play()
        self.activateTimer.start()

    def endingSoundFinished(self):
        if self.endingSound.isFinished():
            deusExSignalData = DeusExSignalData(self.type)
            for obj in self.collidingItems():
                if type(obj).__name__ == "Player":
                    deusExSignalData.markedPlayers.append(obj)
            self.activateTimer.timeout.disconnect()
            self.activateTimer.stop()
            self.deusExActivateSignal.emit(deusExSignalData)
            self.scene().removeItem(self)
            del self
