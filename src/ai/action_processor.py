class ActionProcessor:
    """
    Convertit une action MultiDiscrete [direction, intensité]
    en une transaction réelle.

    direction : 0=SELL, 1=HOLD, 2=BUY
    intensité : 0=25%, 1=50%, 2=75%, 3=100%
    """

    DIRECTIONS = {0: "sell", 1: "hold", 2: "buy"}
    INTENSITIES = {0: 25.0, 1: 50.0, 2: 75.0, 3: 100.0}

    def process(self, action):
        direction_idx = int(action[0])
        intensity_idx = int(action[1])

        transaction = self.DIRECTIONS.get(direction_idx, "hold")

        if transaction == "hold":
            return "hold", 0.0

        percentage = self.INTENSITIES.get(intensity_idx, 25.0)
        return transaction, percentage