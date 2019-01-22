class EnemyTankDetails:
    def __init__(self, tankTypeId, points, health, movementSpeed, bulletSpeed):
        # this tank type will be the number after '.v' on tank texture images names
        self.tankType = tankTypeId
        self.points = points
        self.health = health
        # movementSpeed is a key to movement timer
        self.movementSpeed = movementSpeed
        # this speed is in pxs
        self.bulletSpeed = bulletSpeed
