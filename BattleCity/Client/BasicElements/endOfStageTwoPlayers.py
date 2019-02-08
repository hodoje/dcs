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

from itertools import zip_longest


class EndOfStageTwoPlayers(QGraphicsView):
    def __init__(self,
                 config,
                 currentStage,
                 firstPlayerTotalPoints,
                 firstPlayerSeparateTankDetails,
                 secondPlayerTotalPoints,
                 secondPlayerSeparateTankDetails):
        super().__init__()
        self.config = config
        self.currentStage = currentStage
        self.firstPlayerTotalPoints = firstPlayerTotalPoints
        self.firstPlayerSeparateTankDetails = firstPlayerSeparateTankDetails
        self.firstPlayerTotalTanksPerPlayer = 0
        for detail in self.firstPlayerSeparateTankDetails.details.values():
            self.firstPlayerTotalTanksPerPlayer += detail["count"]
        self.secondPlayerTotalPoints = secondPlayerTotalPoints
        self.secondPlayerSeparateTankDetails = secondPlayerSeparateTankDetails
        self.secondPlayerTotalTanksPerPlayer = 0
        for detail in self.secondPlayerSeparateTankDetails.details.values():
            self.secondPlayerTotalTanksPerPlayer += detail["count"]
        self.texture = self.config.endOfStageTwoPlayersTexture
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

        # FIRST PLAYER
        self.hudFirstPlayerTotalPoints = HudEndOfStageTotalPlayerPointsContainer(self.config,
                                                                                 self.firstPlayerTotalPoints)
        self.hudFirstPlayerTotalPoints.setPos(85, 160)
        self.scene.addItem(self.hudFirstPlayerTotalPoints)

        self.firstPlayerBasicTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                           self.firstPlayerSeparateTankDetails.details["basic"])
        self.firstPlayerBasicTankSeparatePoints.setPos(65, 220)
        self.firstPlayerBasicTankSeparatePoints.hide()
        self.scene.addItem(self.firstPlayerBasicTankSeparatePoints)
        self.firstPlayerBasicTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                self.firstPlayerSeparateTankDetails.details["basic"]["count"])
        self.firstPlayerBasicTankSeparateCount.setPos(240, 220)
        self.firstPlayerBasicTankSeparateCount.hide()
        self.scene.addItem(self.firstPlayerBasicTankSeparateCount)

        self.firstPlayerFastTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                          self.firstPlayerSeparateTankDetails.details["fast"])
        self.firstPlayerFastTankSeparatePoints.setPos(65, 280)
        self.firstPlayerFastTankSeparatePoints.hide()
        self.scene.addItem(self.firstPlayerFastTankSeparatePoints)
        self.firstPlayerFastTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                               self.firstPlayerSeparateTankDetails.details["fast"]["count"])
        self.firstPlayerFastTankSeparateCount.setPos(240, 280)
        self.firstPlayerFastTankSeparateCount.hide()
        self.scene.addItem(self.firstPlayerFastTankSeparateCount)

        self.firstPlayerPowerTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                           self.firstPlayerSeparateTankDetails.details["power"])
        self.firstPlayerPowerTankSeparatePoints.setPos(65, 340)
        self.firstPlayerPowerTankSeparatePoints.hide()
        self.scene.addItem(self.firstPlayerPowerTankSeparatePoints)
        self.firstPlayerPowerTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                self.firstPlayerSeparateTankDetails.details["power"]["count"])
        self.firstPlayerPowerTankSeparateCount.setPos(240, 340)
        self.firstPlayerPowerTankSeparateCount.hide()
        self.scene.addItem(self.firstPlayerPowerTankSeparateCount)

        self.firstPlayerArmorTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                           self.firstPlayerSeparateTankDetails.details["armor"])
        self.firstPlayerArmorTankSeparatePoints.setPos(65, 400)
        self.firstPlayerArmorTankSeparatePoints.hide()
        self.scene.addItem(self.firstPlayerArmorTankSeparatePoints)
        self.firstPlayerArmorTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                self.firstPlayerSeparateTankDetails.details["armor"]["count"])
        self.firstPlayerArmorTankSeparateCount.setPos(240, 400)
        self.firstPlayerArmorTankSeparateCount.hide()
        self.scene.addItem(self.firstPlayerArmorTankSeparateCount)

        self.hudFirstPlayerTotalTanksPerPlayer = HudEndOfStageTotalTanksPerPlayerContainer(self.config,
                                                                                           self.firstPlayerTotalTanksPerPlayer)
        self.hudFirstPlayerTotalTanksPerPlayer.setPos(240, 440)
        self.hudFirstPlayerTotalTanksPerPlayer.hide()
        self.scene.addItem(self.hudFirstPlayerTotalTanksPerPlayer)

        # SECOND PLAYER
        self.hudSecondPlayerTotalPoints = HudEndOfStageTotalPlayerPointsContainer(self.config,
                                                                                  self.secondPlayerTotalPoints)
        self.hudSecondPlayerTotalPoints.setPos(450, 160)
        self.scene.addItem(self.hudSecondPlayerTotalPoints)

        self.secondPlayerBasicTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                            self.secondPlayerSeparateTankDetails.details["basic"])
        self.secondPlayerBasicTankSeparatePoints.setPos(430, 220)
        self.secondPlayerBasicTankSeparatePoints.hide()
        self.scene.addItem(self.secondPlayerBasicTankSeparatePoints)
        self.secondPlayerBasicTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                 self.secondPlayerSeparateTankDetails.details["basic"]["count"])
        self.secondPlayerBasicTankSeparateCount.setPos(370, 220)
        self.secondPlayerBasicTankSeparateCount.hide()
        self.scene.addItem(self.secondPlayerBasicTankSeparateCount)

        self.secondPlayerFastTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                           self.secondPlayerSeparateTankDetails.details["fast"])
        self.secondPlayerFastTankSeparatePoints.setPos(430, 280)
        self.secondPlayerFastTankSeparatePoints.hide()
        self.scene.addItem(self.secondPlayerFastTankSeparatePoints)
        self.secondPlayerFastTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                self.secondPlayerSeparateTankDetails.details["fast"]["count"])
        self.secondPlayerFastTankSeparateCount.setPos(370, 280)
        self.secondPlayerFastTankSeparateCount.hide()
        self.scene.addItem(self.secondPlayerFastTankSeparateCount)

        self.secondPlayerPowerTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                            self.secondPlayerSeparateTankDetails.details["power"])
        self.secondPlayerPowerTankSeparatePoints.setPos(430, 340)
        self.secondPlayerPowerTankSeparatePoints.hide()
        self.scene.addItem(self.secondPlayerPowerTankSeparatePoints)
        self.secondPlayerPowerTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                 self.secondPlayerSeparateTankDetails.details["power"]["count"])
        self.secondPlayerPowerTankSeparateCount.setPos(370, 340)
        self.secondPlayerPowerTankSeparateCount.hide()
        self.scene.addItem(self.secondPlayerPowerTankSeparateCount)

        self.secondPlayerArmorTankSeparatePoints = HudEndOfStageSeparateTankPointsContainer(self.config,
                                                                                            self.secondPlayerSeparateTankDetails.details["armor"])
        self.secondPlayerArmorTankSeparatePoints.setPos(430, 400)
        self.secondPlayerArmorTankSeparatePoints.hide()
        self.scene.addItem(self.secondPlayerArmorTankSeparatePoints)
        self.secondPlayerArmorTankSeparateCount = HudEndOfStageSeparateTankCount(self.config,
                                                                                 self.secondPlayerSeparateTankDetails.details["armor"]["count"])
        self.secondPlayerArmorTankSeparateCount.setPos(370, 400)
        self.secondPlayerArmorTankSeparateCount.hide()
        self.scene.addItem(self.secondPlayerArmorTankSeparateCount)

        self.hudSecondPlayerTotalTanksPerPlayer = HudEndOfStageTotalTanksPerPlayerContainer(self.config,
                                                                                            self.secondPlayerTotalTanksPerPlayer)
        self.hudSecondPlayerTotalTanksPerPlayer.setPos(370, 440)
        self.hudSecondPlayerTotalTanksPerPlayer.hide()
        self.scene.addItem(self.hudSecondPlayerTotalTanksPerPlayer)

    def animateBasicTankStats(self):
        self.firstPlayerBasicTankSeparateCount.show()
        self.firstPlayerBasicTankSeparatePoints.show()
        self.secondPlayerBasicTankSeparateCount.show()
        self.secondPlayerBasicTankSeparatePoints.show()
        if self.firstPlayerBasicTankSeparateCount.count != 0 and self.secondPlayerBasicTankSeparateCount.count != 0:
            for firstNum, secondNum in zip_longest(range(1, self.firstPlayerBasicTankSeparateCount.count + 1),
                                                   range(1, self.secondPlayerBasicTankSeparateCount.count + 1)):
                if firstNum is not None:
                    self.firstPlayerBasicTankSeparateCount.currentCount = firstNum
                    self.firstPlayerBasicTankSeparateCount.updateCurrentCount()
                    self.firstPlayerBasicTankSeparatePoints.currentPoints += self.firstPlayerBasicTankSeparatePoints.pointsStep
                    self.firstPlayerBasicTankSeparatePoints.updatePlayerPoints()
                if secondNum is not None:
                    self.secondPlayerBasicTankSeparateCount.currentCount = secondNum
                    self.secondPlayerBasicTankSeparateCount.updateCurrentCount()
                    self.secondPlayerBasicTankSeparatePoints.currentPoints += self.secondPlayerBasicTankSeparatePoints.pointsStep
                    self.secondPlayerBasicTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerBasicTankSeparateCount.count != 0 and self.secondPlayerBasicTankSeparateCount.count == 0:
            for num in range(1, self.firstPlayerBasicTankSeparateCount.count + 1):
                self.firstPlayerBasicTankSeparateCount.currentCount = num
                self.firstPlayerBasicTankSeparateCount.updateCurrentCount()
                self.firstPlayerBasicTankSeparatePoints.currentPoints += self.firstPlayerBasicTankSeparatePoints.pointsStep
                self.firstPlayerBasicTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerBasicTankSeparateCount.count == 0 and self.secondPlayerBasicTankSeparateCount.count != 0:
            for num in range(1, self.secondPlayerBasicTankSeparateCount.count + 1):
                self.secondPlayerBasicTankSeparateCount.currentCount = num
                self.secondPlayerBasicTankSeparateCount.updateCurrentCount()
                self.secondPlayerBasicTankSeparatePoints.currentPoints += self.secondPlayerBasicTankSeparatePoints.pointsStep
                self.secondPlayerBasicTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateFastTankStats(self):
        self.firstPlayerFastTankSeparateCount.show()
        self.firstPlayerFastTankSeparatePoints.show()
        self.secondPlayerFastTankSeparateCount.show()
        self.secondPlayerFastTankSeparatePoints.show()
        if self.firstPlayerFastTankSeparateCount.count != 0 and self.secondPlayerFastTankSeparateCount.count != 0:
            for firstNum, secondNum in zip_longest(range(1, self.firstPlayerFastTankSeparateCount.count + 1),
                                                   range(1, self.secondPlayerFastTankSeparateCount.count + 1)):
                if firstNum is not None:
                    self.firstPlayerFastTankSeparateCount.currentCount = firstNum
                    self.firstPlayerFastTankSeparateCount.updateCurrentCount()
                    self.firstPlayerFastTankSeparatePoints.currentPoints += self.firstPlayerFastTankSeparatePoints.pointsStep
                    self.firstPlayerFastTankSeparatePoints.updatePlayerPoints()
                if secondNum is not None:
                    self.secondPlayerFastTankSeparateCount.currentCount = secondNum
                    self.secondPlayerFastTankSeparateCount.updateCurrentCount()
                    self.secondPlayerFastTankSeparatePoints.currentPoints += self.secondPlayerFastTankSeparatePoints.pointsStep
                    self.secondPlayerFastTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerFastTankSeparateCount.count != 0 and self.secondPlayerFastTankSeparateCount.count == 0:
            for num in range(1, self.firstPlayerFastTankSeparateCount.count + 1):
                self.firstPlayerFastTankSeparateCount.currentCount = num
                self.firstPlayerFastTankSeparateCount.updateCurrentCount()
                self.firstPlayerFastTankSeparatePoints.currentPoints += self.firstPlayerFastTankSeparatePoints.pointsStep
                self.firstPlayerFastTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerFastTankSeparateCount.count == 0 and self.secondPlayerFastTankSeparateCount.count != 0:
            for num in range(1, self.secondPlayerFastTankSeparateCount.count + 1):
                self.secondPlayerFastTankSeparateCount.currentCount = num
                self.secondPlayerFastTankSeparateCount.updateCurrentCount()
                self.secondPlayerFastTankSeparatePoints.currentPoints += self.secondPlayerFastTankSeparatePoints.pointsStep
                self.secondPlayerFastTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animatePowerTankStats(self):
        self.firstPlayerPowerTankSeparateCount.show()
        self.firstPlayerPowerTankSeparatePoints.show()
        self.secondPlayerPowerTankSeparateCount.show()
        self.secondPlayerPowerTankSeparatePoints.show()
        if self.firstPlayerPowerTankSeparateCount.count != 0 and self.secondPlayerPowerTankSeparateCount.count != 0:
            for firstNum, secondNum in zip_longest(range(1, self.firstPlayerPowerTankSeparateCount.count + 1),
                                                   range(1, self.secondPlayerPowerTankSeparateCount.count + 1)):
                if firstNum is not None:
                    self.firstPlayerPowerTankSeparateCount.currentCount = firstNum
                    self.firstPlayerPowerTankSeparateCount.updateCurrentCount()
                    self.firstPlayerPowerTankSeparatePoints.currentPoints += self.firstPlayerPowerTankSeparatePoints.pointsStep
                    self.firstPlayerPowerTankSeparatePoints.updatePlayerPoints()
                if secondNum is not None:
                    self.secondPlayerPowerTankSeparateCount.currentCount = secondNum
                    self.secondPlayerPowerTankSeparateCount.updateCurrentCount()
                    self.secondPlayerPowerTankSeparatePoints.currentPoints += self.secondPlayerPowerTankSeparatePoints.pointsStep
                    self.secondPlayerPowerTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerPowerTankSeparateCount.count != 0 and self.secondPlayerPowerTankSeparateCount.count == 0:
            for num in range(1, self.firstPlayerPowerTankSeparateCount.count + 1):
                self.firstPlayerPowerTankSeparateCount.currentCount = num
                self.firstPlayerPowerTankSeparateCount.updateCurrentCount()
                self.firstPlayerPowerTankSeparatePoints.currentPoints += self.firstPlayerPowerTankSeparatePoints.pointsStep
                self.firstPlayerPowerTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerPowerTankSeparateCount.count == 0 and self.secondPlayerPowerTankSeparateCount.count != 0:
            for num in range(1, self.secondPlayerPowerTankSeparateCount.count + 1):
                self.secondPlayerPowerTankSeparateCount.currentCount = num
                self.secondPlayerPowerTankSeparateCount.updateCurrentCount()
                self.secondPlayerPowerTankSeparatePoints.currentPoints += self.secondPlayerPowerTankSeparatePoints.pointsStep
                self.secondPlayerPowerTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateArmorTankStats(self):
        self.firstPlayerArmorTankSeparateCount.show()
        self.firstPlayerArmorTankSeparatePoints.show()
        self.secondPlayerArmorTankSeparateCount.show()
        self.secondPlayerArmorTankSeparatePoints.show()
        if self.firstPlayerArmorTankSeparateCount.count != 0 and self.secondPlayerArmorTankSeparateCount.count != 0:
            for firstNum, secondNum in zip_longest(range(1, self.firstPlayerArmorTankSeparateCount.count + 1),
                                                   range(1, self.secondPlayerArmorTankSeparateCount.count + 1)):
                if firstNum is not None:
                    self.firstPlayerArmorTankSeparateCount.currentCount = firstNum
                    self.firstPlayerArmorTankSeparateCount.updateCurrentCount()
                    self.firstPlayerArmorTankSeparatePoints.currentPoints += self.firstPlayerArmorTankSeparatePoints.pointsStep
                    self.firstPlayerArmorTankSeparatePoints.updatePlayerPoints()
                if secondNum is not None:
                    self.secondPlayerArmorTankSeparateCount.currentCount = secondNum
                    self.secondPlayerArmorTankSeparateCount.updateCurrentCount()
                    self.secondPlayerArmorTankSeparatePoints.currentPoints += self.secondPlayerArmorTankSeparatePoints.pointsStep
                    self.secondPlayerArmorTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerArmorTankSeparateCount.count != 0 and self.secondPlayerArmorTankSeparateCount.count == 0:
            for num in range(1, self.firstPlayerArmorTankSeparateCount.count + 1):
                self.firstPlayerArmorTankSeparateCount.currentCount = num
                self.firstPlayerArmorTankSeparateCount.updateCurrentCount()
                self.firstPlayerArmorTankSeparatePoints.currentPoints += self.firstPlayerArmorTankSeparatePoints.pointsStep
                self.firstPlayerArmorTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        elif self.firstPlayerArmorTankSeparateCount.count == 0 and self.secondPlayerArmorTankSeparateCount.count != 0:
            for num in range(1, self.secondPlayerArmorTankSeparateCount.count + 1):
                self.secondPlayerArmorTankSeparateCount.currentCount = num
                self.secondPlayerArmorTankSeparateCount.updateCurrentCount()
                self.secondPlayerArmorTankSeparatePoints.currentPoints += self.secondPlayerArmorTankSeparatePoints.pointsStep
                self.secondPlayerArmorTankSeparatePoints.updatePlayerPoints()
                self.tankCounterSound.play()
                QtTest.QTest.qWait(150)
        else:
            self.tankCounterSound.play()

    def animateHudTotalTanksPerPlayer(self):
        self.hudFirstPlayerTotalTanksPerPlayer.show()
        self.hudSecondPlayerTotalTanksPerPlayer.show()

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
        self.animateHudTotalTanksPerPlayer()

    def updateStageScreen(self,
                          currentStage,
                          firstPlayerTotalPoints,
                          firstPlayerSeparateTankDetails,
                          secondPlayerTotalPoints,
                          secondPlayerSeparateTankDetails):
        self.currentStage = currentStage
        self.firstPlayerTotalPoints = firstPlayerTotalPoints
        self.firstPlayerSeparateTankDetails = firstPlayerSeparateTankDetails
        self.firstPlayerTotalTanksPerPlayer = 0
        for detail in self.firstPlayerSeparateTankDetails.details.values():
            self.firstPlayerTotalTanksPerPlayer += detail["count"]
        self.secondPlayerTotalPoints = secondPlayerTotalPoints
        self.secondPlayerSeparateTankDetails = secondPlayerSeparateTankDetails
        self.secondPlayerTotalTanksPerPlayer = 0
        for detail in self.secondPlayerSeparateTankDetails.details.values():
            self.secondPlayerTotalTanksPerPlayer += detail["count"]
        self.hudCurrentStage.updateStage(self.currentStage)

        # FIRST PLAYER
        self.resetFirstPlayerStats()
        self.hudFirstPlayerTotalPoints.updateTotalPlayerPoints(self.firstPlayerTotalPoints)
        self.firstPlayerBasicTankSeparatePoints.updateTankDetails(self.firstPlayerSeparateTankDetails.details["basic"])
        self.firstPlayerBasicTankSeparateCount.updateCount(self.firstPlayerSeparateTankDetails.details["basic"]["count"])
        self.firstPlayerFastTankSeparatePoints.updateTankDetails(self.firstPlayerSeparateTankDetails.details["fast"])
        self.firstPlayerFastTankSeparateCount.updateCount(self.firstPlayerSeparateTankDetails.details["fast"]["count"]),
        self.firstPlayerPowerTankSeparatePoints.updateTankDetails(self.firstPlayerSeparateTankDetails.details["power"])
        self.firstPlayerPowerTankSeparateCount.updateCount(self.firstPlayerSeparateTankDetails.details["power"]["count"])
        self.firstPlayerArmorTankSeparatePoints.updateTankDetails(self.firstPlayerSeparateTankDetails.details["armor"])
        self.firstPlayerArmorTankSeparateCount.updateCount(self.firstPlayerSeparateTankDetails.details["armor"]["count"])
        self.hudFirstPlayerTotalTanksPerPlayer.updateTotalTanksPerPlayer(self.firstPlayerTotalTanksPerPlayer)
        self.firstPlayerBasicTankSeparatePoints.hide()
        self.firstPlayerBasicTankSeparateCount.hide()
        self.firstPlayerFastTankSeparatePoints.hide()
        self.firstPlayerFastTankSeparateCount.hide()
        self.firstPlayerPowerTankSeparatePoints.hide()
        self.firstPlayerPowerTankSeparateCount.hide()
        self.firstPlayerArmorTankSeparatePoints.hide()
        self.firstPlayerArmorTankSeparateCount.hide()
        self.hudFirstPlayerTotalTanksPerPlayer.hide()

        # SECOND PLAYER
        self.resetSecondPlayerStats()
        self.hudSecondPlayerTotalPoints.updateTotalPlayerPoints(self.secondPlayerTotalPoints)
        self.secondPlayerBasicTankSeparatePoints.updateTankDetails(self.secondPlayerSeparateTankDetails.details["basic"])
        self.secondPlayerBasicTankSeparateCount.updateCount(self.secondPlayerSeparateTankDetails.details["basic"]["count"])
        self.secondPlayerFastTankSeparatePoints.updateTankDetails(self.secondPlayerSeparateTankDetails.details["fast"])
        self.secondPlayerFastTankSeparateCount.updateCount(self.secondPlayerSeparateTankDetails.details["fast"]["count"]),
        self.secondPlayerPowerTankSeparatePoints.updateTankDetails(self.secondPlayerSeparateTankDetails.details["power"])
        self.secondPlayerPowerTankSeparateCount.updateCount(self.secondPlayerSeparateTankDetails.details["power"]["count"])
        self.secondPlayerArmorTankSeparatePoints.updateTankDetails(self.secondPlayerSeparateTankDetails.details["armor"])
        self.secondPlayerArmorTankSeparateCount.updateCount(self.secondPlayerSeparateTankDetails.details["armor"]["count"])
        self.hudSecondPlayerTotalTanksPerPlayer.updateTotalTanksPerPlayer(self.secondPlayerTotalTanksPerPlayer)
        self.secondPlayerBasicTankSeparatePoints.hide()
        self.secondPlayerBasicTankSeparateCount.hide()
        self.secondPlayerFastTankSeparatePoints.hide()
        self.secondPlayerFastTankSeparateCount.hide()
        self.secondPlayerPowerTankSeparatePoints.hide()
        self.secondPlayerPowerTankSeparateCount.hide()
        self.secondPlayerArmorTankSeparatePoints.hide()
        self.secondPlayerArmorTankSeparateCount.hide()
        self.hudSecondPlayerTotalTanksPerPlayer.hide()

    def resetFirstPlayerStats(self):
        self.hudFirstPlayerTotalPoints.reset()
        self.firstPlayerBasicTankSeparatePoints.reset()
        self.firstPlayerBasicTankSeparateCount.reset()
        self.firstPlayerFastTankSeparatePoints.reset()
        self.firstPlayerFastTankSeparateCount.reset()
        self.firstPlayerPowerTankSeparatePoints.reset()
        self.firstPlayerPowerTankSeparateCount.reset()
        self.firstPlayerArmorTankSeparatePoints.reset()
        self.firstPlayerArmorTankSeparateCount.reset()
        self.hudFirstPlayerTotalTanksPerPlayer.reset()

    def resetSecondPlayerStats(self):
        self.hudSecondPlayerTotalPoints.reset()
        self.secondPlayerBasicTankSeparatePoints.reset()
        self.secondPlayerBasicTankSeparateCount.reset()
        self.secondPlayerFastTankSeparatePoints.reset()
        self.secondPlayerFastTankSeparateCount.reset()
        self.secondPlayerPowerTankSeparatePoints.reset()
        self.secondPlayerPowerTankSeparateCount.reset()
        self.secondPlayerArmorTankSeparatePoints.reset()
        self.secondPlayerArmorTankSeparateCount.reset()
        self.hudSecondPlayerTotalTanksPerPlayer.reset()
