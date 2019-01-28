from BasicElements.player import Player
from Player.playerDetails import PlayerDetails


class PlayerWrapper:
    def __init__(self,
                 playerDetails: PlayerDetails,
                 config,
                 color,
                 firingKey,
                 movementKeys,
                 firingNotifier,
                 movementNotifier,
                 playerLevels,
                 field,
                 killEmitter,
                 bulletTimer,
                 targetType,
                 animationTimer,
                 playerDeadEmitter,
                 gameOverEmitter):
        self.playerDetails = playerDetails
        self.config = config
        self.color = color
        self.firingKey = firingKey
        self.movementKeys = movementKeys
        self.firingNotifier = firingNotifier
        self.movementNotifier = movementNotifier
        self.player = Player(self.playerDetails,
                             self.config,
                             self.color,
                             self.firingKey,
                             self.movementKeys,
                             playerLevels,
                             field,
                             targetType,
                             animationTimer,
                             bulletTimer,
                             killEmitter,
                             playerDeadEmitter,
                             gameOverEmitter)

    def getPlayerDetails(self):
        return PlayerDetails(self.player.id, self.player.points, self.player.lives, self.player.level)

    def levelUp(self):
        self.player.levelUp()

    def levelDown(self):
        self.player.levelDown()
