class SeparateTankDetails:
    def __init__(self):
        self.details = {
            "basic": {
                "count": 0,
                "pointsStep": 100
            },
            "fast": {
                "count": 0,
                "pointsStep": 200
            },
            "power": {
                "count": 0,
                "pointsStep": 300
            },
            "armor": {
                "count": 0,
                "pointsStep": 400
            }
        }

    def resetStats(self):
        for details in self.details.values():
            details["count"] = 0
