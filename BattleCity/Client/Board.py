from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from Client.KeyNotifier import KeyNotifier
from Client.Tank import Tank


class Board(QGraphicsView):
    def __init__(self):
        super().__init__()

        # set up a movement and firing notifier
        self.mafNotifier = KeyNotifier(0.05)
        self.mafNotifier.movementSignal.connect(self.updatePosition)
        self.mafNotifier.firingSignal.connect(self.fireCanon)
        self.mafNotifier.start()

        self.__init_ui__()

    def __init_ui__(self):
        # set up the scene
        self.scene = QGraphicsScene()
        # first two zeros are x and y in regard to the containing view
        self.scene.setSceneRect(0, 0, 800, 600)

        # set up the view
        self.setScene(self.scene)
        # these 10 additional pixels are for the margin
        self.setFixedSize(810, 610)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # add the tank on the scene
        self.tank = Tank()
        self.tank.setRect(0, 0, 50, 50)
        self.scene.addItem(self.tank)
        # set position of the tank -> down and center (last 10 pixels in height argument are for the margin)
        self.tank.setPos(self.width() / 2 - self.tank.rect().width() / 2, self.height() - self.tank.rect().height() - 10)

        self.show()

    def keyPressEvent(self, event):
        self.mafNotifier.add_key(event.key())

    def keyReleaseEvent(self, event):
        self.mafNotifier.remove_key(event.key())

    def updatePosition(self, key):
        self.tank.updatePosition(key)

    def fireCanon(self, key):
        self.tank.fireCanon(key)

    def closeEvent(self, event):
        self.mafNotifier.die()
