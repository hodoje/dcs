from openal import *

from PyQt5 import QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from HUD.hudEndOfStageCurrentStageContainer import HudEndOfStageCurrentStageContainer
from HUD.hudEndOfStageSeparateTankCount import HudEndOfStageSeparateTankCount
from HUD.hudEndOfStageSeparateTankPointsContainer import HudEndOfStageSeparateTankPointsContainer
from HUD.hudEndOfStageTotalPlayerPointsContainer import HudEndOfStageTotalPlayerPointsContainer
from HUD.hudEndOfStageTotalTanksPerPlayerContainer import HudEndOfStageTotalTanksPerPlayerContainer


class EndOfStageOnePlayer(QGraphicsView):
    def __init__(self, config, currentStage, totalPlayerPoints, separateTankDetails):
        super().__init__()
        self.config = config
        self.currentStage = currentStage
        self.totalPlayerPoints = totalPlayerPoints
        self.separateTankDetails = separateTankDetails
        self.totalTanksPerPlayer = 0
        for detail in self.separateTankDetails.details.values():
            self.totalTanksPerPlayer += detail["count"]
        self.texture = self.config.endOfStageOnePlayerTexture
        self.tankCounterSound = oalOpen(self.config.sounds["tankCounter"])
        self.__init_ui()

    def __init_ui(self):
        # set up the scene
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 650, 560)
        self.scene.setBackgroundBrush(Qt.darkGray)

        # set up the view
        self.setScene(self.scene)
        # these 10 additional pixels are for the margin
        self.setFixedSize(660, 570)
        # optimization
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setInteractive(False)
        self.setViewport(QGLWidget(QGLFormat()))
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # set the background
        backgroundPixmap = QPixmap(self.texture)
        background = QGraphicsPixmapItem(backgroundPixmap)
        self.scene.addItem(background)

        self.hudCurrentStage = HudEndOfStageCurrentStageContainer(self.config, self.currentStage)
        self.hudCurrentStage.setPos(370, 80)
        self.scene.addItem(self.hudCurrentStage)

        self.hudTotalPlayerPoints = HudEndOfStageTotalPlayerPointsContainer(self.config, self.totalPlayerPoints)
        self.hudTotalPlayerPoints.setPos(85, 160)
        self.scene.addItem(self.hudTotalPlayerPoints)

        self.basicTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                self.separateTankDetails.details["basic"])
        self.basicTankSeparatePoints.setPos(65, 220)
        self.basicTankSeparatePoints.hide()
        self.scene.addItem(self.basicTankSeparatePoints)
        self.basicTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                     self.separateTankDetails.details["basic"]["count"])
        self.basicTankSeparateCount.setPos(240, 220)
        self.basicTankSeparateCount.hide()
        self.scene.addItem(self.basicTankSeparateCount)

        self.fastTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                               self.separateTankDetails.details["fast"])
        self.fastTankSeparatePoints.setPos(65, 280)
        self.fastTankSeparatePoints.hide()
        self.scene.addItem(self.fastTankSeparatePoints)
        self.fastTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                    self.separateTankDetails.details["fast"]["count"])
        self.fastTankSeparateCount.setPos(240, 280)
        self.fastTankSeparateCount.hide()
        self.scene.addItem(self.fastTankSeparateCount)

        self.powerTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                self.separateTankDetails.details["power"])
        self.powerTankSeparatePoints.setPos(65, 340)
        self.powerTankSeparatePoints.hide()
        self.scene.addItem(self.powerTankSeparatePoints)
        self.powerTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                     self.separateTankDetails.details["power"]["count"])
        self.powerTankSeparateCount.setPos(240, 340)
        self.powerTankSeparateCount.hide()
        self.scene.addItem(self.powerTankSeparateCount)

        self.armorTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                self.separateTankDetails.details["armor"])
        self.armorTankSeparatePoints.setPos(65, 400)
        self.armorTankSeparatePoints.hide()
        self.scene.addItem(self.armorTankSeparatePoints)
        self.armorTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                     self.separateTankDetails.details["armor"]["count"])
        self.armorTankSeparateCount.setPos(240, 400)
        self.armorTankSeparateCount.hide()
        self.scene.addItem(self.armorTankSeparateCount)

        self.hudTotalTanksPerPlayer = HudEndOfStageTotalTanksPerPlayerContainer(self.config, self.totalTanksPerPlayer)
        self.hudTotalTanksPerPlayer.setPos(240, 440)
        self.hudTotalTanksPerPlayer.hide()
        self.scene.addItem(self.hudTotalTanksPerPlayer)

    def animateBasicTankStats(self):
        self.basicTankSeparateCount.show()
        self.basicTankSeparatePoints.show()
        if self.basicTankSeparateCount.count != 0:
            for num in range(1, self.basicTankSeparateCount.count + 1):
                self.basicTankSeparateCount.currentCount = num
                self.basicTankSeparateCount.updateCurrentCount()
                self.basicTankSeparatePoints.currentPoints += self.basicTankSeparatePoints.pointsStep
                self.basicTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateFastTankStats(self):
        self.fastTankSeparateCount.show()
        self.fastTankSeparatePoints.show()
        if self.fastTankSeparateCount.count != 0:
            for num in range(1, self.fastTankSeparateCount.count + 1):
                self.fastTankSeparateCount.currentCount = num
                self.fastTankSeparateCount.updateCurrentCount()
                self.fastTankSeparatePoints.currentPoints += self.fastTankSeparatePoints.pointsStep
                self.fastTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animatePowerTankStats(self):
        self.powerTankSeparateCount.show()
        self.powerTankSeparatePoints.show()
        if self.powerTankSeparateCount.count != 0:
            for num in range(1, self.powerTankSeparateCount.count + 1):
                self.powerTankSeparateCount.currentCount = num
                self.powerTankSeparateCount.updateCurrentCount()
                self.powerTankSeparatePoints.currentPoints += self.powerTankSeparatePoints.pointsStep
                self.powerTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateArmorTankStats(self):
        self.armorTankSeparateCount.show()
        self.armorTankSeparatePoints.show()
        if self.armorTankSeparateCount.count != 0:
            for num in range(1, self.armorTankSeparateCount.count + 1):
                self.armorTankSeparateCount.currentCount = num
                self.armorTankSeparateCount.updateCurrentCount()
                self.armorTankSeparatePoints.currentPoints += self.armorTankSeparatePoints.pointsStep
                self.armorTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateTotalTanksPerPlayer(self):
        self.hudTotalTanksPerPlayer.show()

    def animate(self):
        QtTest.QTest.qWait(500)
        self.animateBasicTankStats()
        QtTest.QTest.qWait(500)
        self.animateFastTankStats()
        QtTest.QTest.qWait(500)
        self.animatePowerTankStats()
        QtTest.QTest.qWait(500)
        self.animateArmorTankStats()
        QtTest.QTest.qWait(500)
        self.animateTotalTanksPerPlayer()

    def updateStageScreen(self, currentStage, totalPlayerPoints, separateTankDetails):
        self.currentStage = currentStage
        self.totalPlayerPoints = totalPlayerPoints
        self.separateTankDetails = separateTankDetails
        self.totalTanksPerPlayer = 0
        for detail in self.separateTankDetails.details.values():
            self.totalTanksPerPlayer += detail["count"]
        self.hudCurrentStage.updateStage(self.currentStage)
        self.resetPlayerStats()
        self.hudTotalPlayerPoints.updateTotalPlayerPoints(self.totalPlayerPoints)
        self.basicTankSeparatePoints.updateTankDetails(self.separateTankDetails.details["basic"])
        self.basicTankSeparateCount.updateCount(self.separateTankDetails.details["basic"]["count"])
        self.fastTankSeparatePoints.updateTankDetails(self.separateTankDetails.details["fast"])
        self.fastTankSeparateCount.updateCount(self.separateTankDetails.details["fast"]["count"]),
        self.powerTankSeparatePoints.updateTankDetails(self.separateTankDetails.details["power"])
        self.powerTankSeparateCount.updateCount(self.separateTankDetails.details["power"]["count"])
        self.armorTankSeparatePoints.updateTankDetails(self.separateTankDetails.details["armor"])
        self.armorTankSeparateCount.updateCount(self.separateTankDetails.details["armor"]["count"])
        self.hudTotalTanksPerPlayer.updateTotalTanksPerPlayer(self.totalTanksPerPlayer)
        self.basicTankSeparatePoints.hide()
        self.basicTankSeparateCount.hide()
        self.fastTankSeparatePoints.hide()
        self.fastTankSeparateCount.hide()
        self.powerTankSeparatePoints.hide()
        self.powerTankSeparateCount.hide()
        self.armorTankSeparatePoints.hide()
        self.armorTankSeparateCount.hide()
        self.hudTotalTanksPerPlayer.hide()

    def resetPlayerStats(self):
        self.hudTotalPlayerPoints.reset()
        self.basicTankSeparatePoints.reset()
        self.basicTankSeparateCount.reset()
        self.fastTankSeparatePoints.reset()
        self.fastTankSeparateCount.reset()
        self.powerTankSeparatePoints.reset()
        self.powerTankSeparateCount.reset()
        self.armorTankSeparatePoints.reset()
        self.armorTankSeparateCount.reset()
        self.hudTotalTanksPerPlayer.reset()
