import json


class Config:
    def __init__(self):
        with open("Config/config.json") as config_file:
            self.config = json.load(config_file)
        self.mainWindowSize = self.config["mainWindowSize"]
        self.mainMenuTexture = self.config["mainMenuTexture"]
        self.mainMenuSelector = self.config["mainMenuSelector"]
        self.gameOverTexture = self.config["gameOverTexture"]
        self.currentStageTexture = self.config["currentStageTexture"]
        self.numbers = self.config["numbers"]
        self.playersLives = self.config["playersLives"]
        self.initialPlayerLives = self.config["initialPlayerLives"]
        self.baseTextures = self.config["baseTextures"]
        self.blockTextures = self.config["blockTextures"]
        self.hudEnemy = self.config["hudEnemy"]
        self.hudEnemyContainer = self.config["hudEnemyContainer"]
        self.hudEnemyContainerWidth = self.config["hudEnemyContainerWidth"]
        self.hudEnemyContainerHeight = self.config["hudEnemyContainerHeight"]
        self.enemySpawnRegionWidth = self.config["enemySpawnRegionWidth"]
        self.enemySpawnRegionHeight = self.config["enemySpawnRegionHeight"]
        self.enemyShootInterval = self.config["enemyShootInterval"]
        self.enemyMovementSpeedMap = self.config["enemyMovementSpeedMap"]
        self.bulletSpeedMap = self.config["bulletSpeedMap"]
        self.enemyTypeIds = self.config["enemyTypeIds"]
        self.enemyTypes = self.config["enemyTypes"]
        self.playerMovementSpeed = self.config["playerMovementSpeed"]
        self.playerLevels = self.config["playerLevels"]
        self.maps = self.config["maps"]
        self.sounds = self.config["sounds"]
