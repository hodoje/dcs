from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtOpenGL import QGLWidget, QGLFormat
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from bridge import Bridge, MenuToMainWindowData


class MainMenu(QGraphicsView):
    def __init__(self, config, bridge: Bridge):
        super().__init__()
        self.config = config
        self.bridge = bridge
        self.mainMenuTexture = self.config.mainMenuTexture
        # 1 - local 1 player, 2 - local 2 players, 3 - online
        self.options = [0, 1, 2]
        # initially the first option is selected
        self.selectedOption = 0
        self.selectorPositions = [QPointF(180, 315), QPointF(180, 355), QPointF(180, 395)]
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
        backgroundPixmap = QPixmap(self.mainMenuTexture)
        background = QGraphicsPixmapItem(backgroundPixmap)
        self.scene.addItem(background)

        # menu selector
        selectorPixmap = QPixmap(self.config.mainMenuSelector)
        self.selector = QGraphicsPixmapItem(selectorPixmap)
        self.selector.setPos(self.selectorPositions[self.selectedOption])
        self.scene.addItem(self.selector)

    def keyPressEvent(self, QKeyEvent):
        key = QKeyEvent.key()
        if key == Qt.Key_Up:
            if (self.selectedOption - 1) < 0:
                self.selectedOption = 0
            else:
                self.selectedOption -= 1
            self.setSelectorPos()
        elif key == Qt.Key_Down:
            if (self.selectedOption + 1) > 2:
                self.selectedOption = 2
            else:
                self.selectedOption += 1
            self.setSelectorPos()
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.selectedOption == 0:
                self.localSinglePlayer()
            elif self.selectedOption == 1:
                self.localMultiplayer()
            else:
                self.onlineMultiplayer()

    def setSelectorPos(self):
        self.selector.setPos(self.selectorPositions[self.selectedOption])

    def localSinglePlayer(self):
        self.bridge.menuToMainWindowSignal.emit(MenuToMainWindowData(False, 1))

    def localMultiplayer(self):
        self.bridge.menuToMainWindowSignal.emit(MenuToMainWindowData(False, 2))

    def onlineMultiplayer(self):
        pass