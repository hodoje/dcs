from Enemy.enemyTankDetails import EnemyTankDetails
from Enemy.enemyTypeEnum import EnemyType


class EnemyTankDetailsFactory:
    def __init__(self, enemyTypes, enemyTypeIds, enemiesToGenerate, bulletSpeedMap):
        self.enemyTypes = enemyTypes
        self.enemyTypeIds = enemyTypeIds
        self.enemiesToGenerate = enemiesToGenerate
        self.bulletSpeedMap = bulletSpeedMap
        self.extractNumberOfTanksPerType()

    def extractNumberOfTanksPerType(self):
        self.basicTanksNum = self.enemiesToGenerate[EnemyType.BASIC]
        self.fastTanksNum = self.enemiesToGenerate[EnemyType.FAST]
        self.powerTanksNum = self.enemiesToGenerate[EnemyType.POWER]
        self.armorTanksNum = self.enemiesToGenerate[EnemyType.ARMOR]

    def generateEnemiesDetails(self):
        etdMap = {}
        idx = 0
        if self.basicTanksNum > 0:
            for b in range(self.basicTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.BASIC]["typeIdKey"]],
                    self.enemyTypes[EnemyType.BASIC]["points"],
                    self.enemyTypes[EnemyType.BASIC]["health"],
                    self.enemyTypes[EnemyType.BASIC]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.BASIC]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.fastTanksNum > 0:
            for f in range(self.fastTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.FAST]["typeIdKey"]],
                    self.enemyTypes[EnemyType.FAST]["points"],
                    self.enemyTypes[EnemyType.FAST]["health"],
                    self.enemyTypes[EnemyType.FAST]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.FAST]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.powerTanksNum > 0:
            for p in range(self.powerTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.POWER]["typeIdKey"]],
                    self.enemyTypes[EnemyType.POWER]["points"],
                    self.enemyTypes[EnemyType.POWER]["health"],
                    self.enemyTypes[EnemyType.POWER]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.POWER]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.armorTanksNum > 0:
            for a in range(self.armorTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.ARMOR]["typeIdKey"]],
                    self.enemyTypes[EnemyType.ARMOR]["points"],
                    self.enemyTypes[EnemyType.ARMOR]["health"],
                    self.enemyTypes[EnemyType.ARMOR]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.ARMOR]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        return etdMap
