from PyQt5.QtCore import QObject, pyqtSignal

# connects the board, main window and main menu
from Bridge.gameTypeData import GameTypeData
from Bridge.localGameData import LocalGameData
from Bridge.onlineGameData import OnlineGameData


class Bridge(QObject):
    # main menu to main window signal for selection of the type of game
    gamePickSignal = pyqtSignal(GameTypeData)
    # board to main window signal (used for sending details about players after a round has ended)
    localGameStageEndSignal = pyqtSignal(LocalGameData)
    # board to main window signal (used for sending details about the player after online round)
    onlineGameStageEndSignal = pyqtSignal(OnlineGameData)
    # game over signal sends the same data but needed for different slots
    localGameOverSignal = pyqtSignal(LocalGameData)
    onlineGameOverSignal = pyqtSignal(OnlineGameData)

    def __init__(self):
        super().__init__()
