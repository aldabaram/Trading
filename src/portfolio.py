class Portfolio:
    def __init__(self, starting_usd):
        self.usd = starting_usd
        self.btc = 0

    def buy_percentage(self, percentage, price):
        """Achète un pourcentage de l'argent disponible."""
        amount_usd = self.usd * (percentage / 100)
        btc_bought = amount_usd / price
        self.usd -= amount_usd
        self.btc += btc_bought
        return "BUY", btc_bought, amount_usd

    def sell_percentage(self, percentage, price):
        """Vend un pourcentage des BTC possédés."""
        btc_to_sell = self.btc * (percentage / 100)
        amount_usd = btc_to_sell * price
        self.btc -= btc_to_sell
        self.usd += amount_usd
        return "SELL", btc_to_sell, amount_usd

    def get_total_value(self, price):
        """
        Calcule la valeur totale du portefeuille.
        """
        btc_value = self.btc * price
        total = self.usd + btc_value
        return total

    def get_state(self, price):
        """
        Retourne l'état actuel du portefeuille.
        """
        return {
            "usd": self.usd,
            "btc": self.btc,
            "total_value": self.get_total_value(price)
        }