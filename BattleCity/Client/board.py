from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from Client.firingNotifier import FiringNotifier
from Client.movementNotifier import MovementNotifier
from Client.player import Player


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()

        # player1 keys
        self.firingKey = Qt.Key_Space
        self.movementKeys = {"Up": Qt.Key_Up, "Down": Qt.Key_Down, "Left": Qt.Key_Left, "Right": Qt.Key_Right}

        # player2 keys
        self.firingKey2 = Qt.Key_J
        self.movementKeys2 = {"Up": Qt.Key_W, "Down": Qt.Key_S, "Left": Qt.Key_A, "Right": Qt.Key_D}

        self.__init_ui__()

        # set up a movement and firing notifier for player1
        self.movemeNotifier = MovementNotifier(0.05)
        self.movemeNotifier.movementSignal.connect(self.updatePosition)
        self.movemeNotifier.start()

        self.firingNotifier = FiringNotifier(50)
        self.firingNotifier.firingSignal.connect(self.fireCanon)
        self.player.canShootSignal.connect(self.allowFiring)

        # set up a movement and firing notifier for player2
        self.movemeNotifier2 = MovementNotifier(0.05)
        self.movemeNotifier2.movementSignal.connect(self.updatePosition)
        self.movemeNotifier2.start()

        self.firingNotifier2 = FiringNotifier(50)
        self.firingNotifier2.firingSignal.connect(self.fireCanon2)
        self.player2.canShootSignal.connect(self.allowFiring2)

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
        self.player = Player("yellow", self.firingKey, self.movementKeys)
        self.scene.addItem(self.player)
        # set position of the player -> down and center (last 10 pixels in height argument are for the margin)
        self.player.setPos(self.width() / 2 - self.player.boundingRect().width() / 2 + 50,
                           self.height() - self.player.boundingRect().height() - 10)

        self.player2 = Player("red", self.firingKey2, self.movementKeys2)
        self.scene.addItem(self.player2)
        # set position of the player -> down and center (last 10 pixels in height argument are for the margin)
        self.player2.setPos(self.width() / 2 - self.player2.boundingRect().width() / 2 - 50,
                           self.height() - self.player2.boundingRect().height() - 10)

    def keyPressEvent(self, event):
        key = event.key()
        if key == self.firingKey:
            self.firingNotifier.add_key(key)
        if key in self.movementKeys.values():
            self.movemeNotifier.add_key(key)
        if key == self.firingKey2:
            self.firingNotifier2.add_key(key)
        if key in self.movementKeys2.values():
            self.movemeNotifier2.add_key(key)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == self.firingKey:
            self.firingNotifier.remove_key(key)
        if key in self.movementKeys.values():
            self.movemeNotifier.remove_key(key)
        if key == self.firingKey2:
            self.firingNotifier2.remove_key(key)
        if key in self.movementKeys2.values():
            self.movemeNotifier2.remove_key(key)

    # player1 slots
    def updatePosition(self, key):
        if key in self.movementKeys.values():
            self.player.updatePosition(key)
        if key in self.movementKeys2.values():
            self.player2.updatePosition(key)

    def fireCanon(self, key):
        self.player.fire(key)

    def allowFiring(self, canEmit):
        self.firingNotifier.canEmit = canEmit

    # player2 slots
    def fireCanon2(self, key):
        self.player2.fire(key)

    def allowFiring2(self, canEmit):
        self.firingNotifier2.canEmit = canEmit

    def closeEvent(self, event):
        self.movemeNotifier.die()
        self.movemeNotifier2.die()
