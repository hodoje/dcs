from PyQt5.QtCore import QObject, pyqtSignal


class MenuToMainWindowData:
    def __init__(self, isOnline, numOfPlayers):
        self.isOnline = isOnline
        self.numOfPlayers = numOfPlayers


class BoardToMainWindowData:
    def __init__(self, winnerId, winnerPoints):
        self.winnerId = winnerId,
        self.winnerPoints = winnerPoints

# connects the board, main window and main menu
class Bridge(QObject):
    menuToMainWindowSignal = pyqtSignal(MenuToMainWindowData)
    boardToMainWindowSignal = pyqtSignal(BoardToMainWindowData)

    def __init__(self):
        super().__init__()