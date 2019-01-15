from enemyTankDetails import EnemyTankDetails
from enemyTypeEnum import EnemyType


class EnemyTankDetailsFactory:
    def __init__(self, enemyTypes, enemyTypeIds, enemiesToGenerate, bulletSpeedMap):
        self.enemyTypes = enemyTypes
        self.enemyTypeIds = enemyTypeIds
        self.enemiesToGenerate = enemiesToGenerate
        self.bulletSpeedMap = bulletSpeedMap
        self.extractNumberOfTanksPerType()

    def extractNumberOfTanksPerType(self):
        self.basicTanksNum = self.enemiesToGenerate[EnemyType.basic]
        self.fastTanksNum = self.enemiesToGenerate[EnemyType.fast]
        self.powerTanksNum = self.enemiesToGenerate[EnemyType.power]
        self.armorTanksNum = self.enemiesToGenerate[EnemyType.armor]

    def generateEnemiesDetails(self):
        etdMap = {}
        idx = 0
        if self.basicTanksNum > 0:
            for b in range(self.basicTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.basic]["typeIdKey"]],
                    self.enemyTypes[EnemyType.basic]["points"],
                    self.enemyTypes[EnemyType.basic]["health"],
                    self.enemyTypes[EnemyType.basic]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.basic]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.fastTanksNum > 0:
            for f in range(self.fastTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.fast]["typeIdKey"]],
                    self.enemyTypes[EnemyType.fast]["points"],
                    self.enemyTypes[EnemyType.fast]["health"],
                    self.enemyTypes[EnemyType.fast]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.fast]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.powerTanksNum > 0:
            for p in range(self.powerTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.power]["typeIdKey"]],
                    self.enemyTypes[EnemyType.power]["points"],
                    self.enemyTypes[EnemyType.power]["health"],
                    self.enemyTypes[EnemyType.power]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.power]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        if self.armorTanksNum > 0:
            for a in range(self.armorTanksNum):
                etd = EnemyTankDetails(
                    self.enemyTypeIds[self.enemyTypes[EnemyType.armor]["typeIdKey"]],
                    self.enemyTypes[EnemyType.armor]["points"],
                    self.enemyTypes[EnemyType.armor]["health"],
                    self.enemyTypes[EnemyType.armor]["movementSpeed"],
                    self.bulletSpeedMap[self.enemyTypes[EnemyType.armor]["bulletSpeed"]])
                etdMap[idx] = etd
                idx += 1
        return etdMap
