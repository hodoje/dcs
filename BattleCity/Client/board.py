from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from Client.firingNotifier import FiringNotifier
from Client.movementNotifier import MovementNotifier
from Client.player import Player


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.__init_ui__()

        # set up a movement and firing notifier
        self.movemeNotifier = MovementNotifier(0.05)
        self.movemeNotifier.movementSignal.connect(self.updatePosition)
        self.movemeNotifier.start()

        self.firingNotifier = FiringNotifier(50)
        self.firingNotifier.firingSignal.connect(self.fireCanon)
        self.player.canShootSignal.connect(self.allowFiring)

        self.firingKey = Qt.Key_Space
        self.movementKeys = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]

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
        if key == self.firingKey:
            self.firingNotifier.add_key(key)
        elif key in self.movementKeys:
            self.movemeNotifier.add_key(key)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == self.firingKey:
            self.firingNotifier.remove_key(key)
        elif key in self.movementKeys:
            self.movemeNotifier.remove_key(key)

    def updatePosition(self, key):
        self.player.updatePosition(key)

    def fireCanon(self, key):
        self.player.fireCanon(key)

    def allowFiring(self, canEmit):
        self.firingNotifier.canEmit = canEmit

    def closeEvent(self, event):
        self.movemeNotifier.die()