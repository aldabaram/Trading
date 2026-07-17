class MarketAnalysis:
    def __init__(self, prices):
        self.prices = prices
    
    def update(self, price):
        self.prices.append(price)
        if len(self.prices) > 100:
            self.prices.pop(0)

    def get_variation(self):
        """Calcule la variation du dernier prix par rapport au prix précédent."""
        if len(self.prices) > 1:
            last_price = self.prices[-1]
            last_trade_price = self.prices[-2]
            return ((last_price - last_trade_price) / last_trade_price) * 100
        return 0

    def moving_average(self):
        """Calcule la moyenne des derniers prix."""
        if len(self.prices) == 0:
            return 0
        return sum(self.prices) / len(self.prices)

    def volatility(self):
        """Mesure l'amplitude des variations récentes du Bitcoin."""
        if len(self.prices) < 2:
            return 0
        mean = self.moving_average()
        variance = sum((price - mean) ** 2 for price in self.prices) / len(self.prices)
        return variance ** 0.5

    def get_state(self):
        """Retourne l'état actuel de l'analyse du marché."""
        return {
            "last_price": self.prices[-1] if self.prices else None,
            "variation": self.get_variation(),
            "moving_average": self.moving_average(),
            "volatility": self.volatility()
        }
