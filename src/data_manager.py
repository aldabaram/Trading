import csv
from datetime import datetime
from pathlib import Path
import json

from constant import PORTFOLIO_HISTORY_FILE, PRICE_HISTORY_FILE, TRADES_HISTORY_FILE


class DataManager:
    """Classe pour gérer les données du marché et du portefeuille."""

    def __init__(self, price_file=None, portfolio_file=None, trade_file=None):
        self.price_file = Path(price_file or PRICE_HISTORY_FILE)
        self.portfolio_file = Path(portfolio_file or PORTFOLIO_HISTORY_FILE)
        self.trade_file = Path(trade_file or TRADES_HISTORY_FILE)
        self.dates = []
        self.prices = []
        self._ensure_parent_dirs()
    
    def clean_files(self):
        """Supprime les fichiers de données existants."""
        for file_path in [self.price_file, self.portfolio_file, self.trade_file]:
            print(f"Cleaning file: {file_path}")
            if file_path.exists():
                file_path.unlink()

    def _ensure_parent_dirs(self):
        for file_path in [self.price_file, self.portfolio_file, self.trade_file]:
            file_path.parent.mkdir(parents=True, exist_ok=True)

    def save_price(self, price, date=None, display=True):
        """Sauvegarde un prix BTC et l'affiche si demandé."""
        if date is None:
            date = datetime.now()

        self.dates.append(date)
        self.prices.append(float(price))

        with self.price_file.open("a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, price])

        return {"date": date, "price": float(price)}

    def load_prices(self):
        if not self.price_file.exists():
            return []

        prices = []
        dates = []
        with self.price_file.open("r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                dates.append(row[0])
                prices.append(float(row[1]))

        self.dates = dates
        self.prices = prices
        return prices

    def get_dates(self):
        return self.dates

    def get_prices(self):
        return self.prices

    def save_portfolio(self, portfolio, price, date=None):
        """Sauvegarde l'état du portefeuille."""
        if date is None:
            date = datetime.now()

        state = portfolio.get_state(price)
        with self.portfolio_file.open("a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, state["usd"], state["btc"], state["total_value"]])

        return state

    def load_portfolio_values(self):
        if not self.portfolio_file.exists():
            return []

        values = []
        with self.portfolio_file.open("r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                values.append(float(row[3]))
        return values

    def load_last_portfolio_state(self):
        if not self.portfolio_file.exists():
            return None

        with self.portfolio_file.open("r", newline="") as file:
            rows = list(csv.reader(file))

        if not rows:
            return None

        last_row = rows[-1]
        return {
            "usd": float(last_row[1]),
            "btc": float(last_row[2]),
            "total_value": float(last_row[3]),
        }

    def get_portfolio_values(self):
        return self.load_portfolio_values()

    def get_portfolio_file(self):
        return self.portfolio_file

    def save_trade(self, trade_type, amount_usdt, amount_btc, price, date=None):
        """Sauvegarde une transaction."""
        if date is None:
            date = datetime.now()

        with self.trade_file.open("a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, trade_type, price, amount_usdt, amount_btc])

        return {
            "date": date,
            "type": trade_type,
            "price": price,
            "usd": amount_usdt,
            "btc": amount_btc,
        }

    def load_trades(self):
        if not self.trade_file.exists():
            return []

        trades = []
        with self.trade_file.open("r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                trades.append({
                    "date": row[0],
                    "type": row[1],
                    "price": float(row[2]),
                    "usd": float(row[3]),
                    "btc": float(row[4]),
                })
        return trades

    def save_episode(self, env, episode_number):
        folder = Path("data/episodes")
        folder.mkdir(exist_ok=True)

        episode = {
            "episode": int(episode_number),

            "final_value": float(env.portfolio_history[-1]),

            "total_reward": float(env.total_reward),

            "prices": [
                float(price)
                for price in env.price_history
            ],

            "portfolio_values": [
                float(value)
                for value in env.portfolio_history
            ],

            "trades": []
        }

        for trade in env.trades:
            episode["trades"].append({
                "step": int(trade["step"]),
                "type": trade["type"],
                "price": float(trade["price"]),
                "percentage": float(trade["percentage"]),
                "fee": float(trade["fee"])
            })


        file = folder / f"episode_{episode_number}.json"

        with file.open("w") as f:
            json.dump(
                episode,
                f,
                indent=4
            )