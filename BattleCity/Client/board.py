from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from firingNotifier import FiringNotifier
from movementNotifier import MovementNotifier
from player import Player


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()

        # set up a movement and firing notifier
        self.movemeNotifier = MovementNotifier(0.015)
        self.movemeNotifier.movementSignal.connect(self.updatePosition)
        self.movemeNotifier.start()

        self.firingNotifier = FiringNotifier(0.5)
        self.firingNotifier.firingSignal.connect(self.fireCanon)
        self.firingNotifier.start()

        self.firingKey = Qt.Key_Space
        self.movementKeys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]

        self.__init_ui__()

    def __init_ui__(self):
        # set up the scene
        self.scene = QGraphicsScene()
        # first two zeros are x and y in regard to the containing view
        # this resolution gives us 15 rows and 20 columns for object of size 40x40px
        self.scene.setSceneRect(0, 0, 800, 600)
        self.scene.setBackgroundBrush(Qt.black)

        # set up the view
        self.setScene(self.scene)
        # these 10 additional pixels are for the margin
        self.setFixedSize(810, 610)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)

        # add the player on the scene
        self.player = Player()
        self.scene.addItem(self.player)
        # set position of the player -> down and center (last 10 pixels in height argument are for the margin)
        self.player.setPos(self.width() / 2 - self.player.boundingRect().width() / 2, self.height() - self.player.boundingRect().height() - 10)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.firingNotifier.add_key(key)
        elif key in self.movementKeys:
            self.movemeNotifier.add_key(key)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.firingNotifier.remove_key(key)
        elif key in self.movementKeys:
            self.movemeNotifier.remove_key(key)

    def updatePosition(self, key):
        self.player.updatePosition(key)

    def fireCanon(self, key):
        self.player.fireCanon(key)

    def closeEvent(self, event):
        self.movemeNotifier.die()
        self.firingNotifier.die()
