import csv
from pathlib import Path


class HistoricalData:
    def __init__(self, filename=None):
        self.filename = Path(filename)
        self.dates = []
        self.prices = []
        self.index = 0
        self.load_prices(self.filename)

    def load_prices(self, filename=None):
        """Charge les prix historiques dans un format similaire à DataManager."""
        if filename is not None:
            self.filename = Path(filename)

        self.dates = []
        self.prices = []
        self.index = 0

        if not self.filename.exists():
            return []

        with self.filename.open("r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if not row:
                    continue
                self.dates.append(row[0])
                self.prices.append(float(row[1]))

        return self.prices

    def get_price(self):
        """Retourne le prix suivant et la date dans la liste historique."""
        if self.index >= len(self.prices):
            return None

        price = self.prices[self.index]
        date = self.dates[self.index]
        self.index += 1

        return {
            "date": date,
            "price": price,
        }

    def get_prices(self):
        return self.prices[:]

    def get_dates(self):
        return self.dates[:]


class HistoricalMarket(HistoricalData):
    """Alias de compatibilité pour la simulation et le reste du code."""

    pass