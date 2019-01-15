class PlayerWrapper:
    def __init__(self, id, player, firingKey, movementKeys, firingNotifier, movementNotifier):
        self.id = id
        self.player = player
        self.firingKey = firingKey
        self.movementKeys = movementKeys
        self.firingNotifier = firingNotifier
        self.movementNotifier = movementNotifier
