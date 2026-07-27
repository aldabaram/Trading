import time
from constant import STARTING_USD, TRADING_FEE

class Portfolio:
    def __init__(self, starting_usd):
        self.usd = starting_usd
        self.btc = 0
        self.last_fee = 0
        
        # Tracking position history
        self.last_buy_time = None
        self.last_sell_time = None
        self.average_buy_price = 0
        self.total_btc_bought = 0  # Total BTC accumulated for average price calculation

    @classmethod
    def from_state(cls, usd, btc, starting_usd=None):
        portfolio = cls(starting_usd if starting_usd is not None else STARTING_USD)
        portfolio.usd = float(usd)
        portfolio.btc = float(btc)
        return portfolio

    def buy_percentage(self, percentage, price):
        if self.usd <= 0:
            return False, "BUY", 0, 0
        amount_usd = self.usd * (percentage / 100)

        fee = amount_usd * TRADING_FEE
        amount_after_fee = amount_usd - fee
        self.last_fee = fee

        btc_bought = amount_after_fee / price

        # Update average buy price
        if self.btc == 0:
            # First buy
            self.average_buy_price = price
        else:
            # Update weighted average
            self.average_buy_price = (self.average_buy_price * self.total_btc_bought + price * btc_bought) / (self.total_btc_bought + btc_bought)
        
        self.total_btc_bought += btc_bought
        self.usd -= amount_usd
        self.btc += btc_bought
        self.last_buy_time = time.time()

        return True, "BUY", btc_bought, amount_usd

    def sell_percentage(self, percentage, price):
        if self.btc <= 0:
            return False,"SELL" , 0, 0

        btc_to_sell = self.btc * (percentage / 100)
        amount_usd = btc_to_sell * price
        fee = amount_usd * TRADING_FEE
        amount_after_fee = amount_usd - fee
        self.last_fee = fee
        self.btc -= btc_to_sell
        self.total_btc_bought -= btc_to_sell
        self.usd += amount_after_fee
        self.last_sell_time = time.time()
        return True, "SELL", btc_to_sell, amount_usd

    def get_total_value(self, price):
        """
        Calcule la valeur totale du portefeuille.
        """
        btc_value = self.btc * price
        total = self.usd + btc_value
        return total

    def _normalize_plus_value(self, plus_value):
        normalized = (plus_value / 100 + 1) / 2
        return max(0.0, min(1.0, normalized))

    def _normalize_holding_time(self, time_seconds, saturation_seconds=86400):
        """Normalize holding time, saturates at saturation_seconds (24h default)."""
        normalized = time_seconds / saturation_seconds
        return max(0.0, min(1.0, normalized))

    def _normalize_entry_price_ratio(self, current_price):
        """Normalize entry price ratio (current_price / average_buy_price)."""
        if self.average_buy_price <= 0:
            return 0.5
        ratio = current_price / self.average_buy_price
        # Map ratio to [0, 1]: 0.5x -> 0, 1x -> 0.5, 2x -> 1
        normalized = (ratio - 0.5) / 1.5 + 0.5
        return max(0.0, min(1.0, normalized))

    def _normalize_unrealized_profit(self, unrealized_pct):
        """Normalize unrealized profit percentage."""
        normalized = (unrealized_pct / 100 + 1) / 2
        return max(0.0, min(1.0, normalized))

    def reset(self, current_price):
        self.usd = STARTING_USD / 2
        self.btc = STARTING_USD / 2 / current_price
        self.last_fee = 0
        self.last_buy_time = time.time()
        self.last_sell_time = None
        self.average_buy_price = current_price
        self.total_btc_bought = self.btc

    def get_state(self, price):
        """
        Retourne l'état actuel du portefeuille avec observations enrichies.
        """
        total_value = self.get_total_value(price)
        plus_value_pct = (total_value - STARTING_USD) / STARTING_USD * 100
        
        # Position size: percentage of portfolio invested in BTC
        btc_value = self.btc * price
        position_size = btc_value / total_value if total_value > 0 else 0
        
        # Holding time: time since last buy
        holding_time_norm = 0.0
        if self.last_buy_time is not None:
            time_since_buy = time.time() - self.last_buy_time
            holding_time_norm = self._normalize_holding_time(time_since_buy)
        
        # Time since sell
        time_since_sell_norm = 0.0
        if self.last_sell_time is not None:
            time_since_sell = time.time() - self.last_sell_time
            time_since_sell_norm = self._normalize_holding_time(time_since_sell)
        
        # Entry price ratio (current price / average buy price)
        entry_price_ratio_norm = 0.5
        if self.btc > 0 and self.average_buy_price > 0:
            entry_price_ratio_norm = self._normalize_entry_price_ratio(price)
        
        # Unrealized profit on current position
        unrealized_profit_norm = 0.5
        if self.btc > 0 and self.average_buy_price > 0:
            unrealized_pct = (price - self.average_buy_price) / self.average_buy_price * 100
            unrealized_profit_norm = self._normalize_unrealized_profit(unrealized_pct)
        
        return {
            "usd": self.usd,
            "btc": self.btc,
            "total_value": total_value,
            "plus_value": plus_value_pct,
            "cash_ratio": self.usd / total_value if total_value else 0.0,
            "crypto_ratio": (self.btc * price) / total_value if total_value else 0.0,
            "plus_value_norm": self._normalize_plus_value(plus_value_pct),
            "holding_time_norm": holding_time_norm,
            "time_since_sell_norm": time_since_sell_norm,
            "entry_price_ratio_norm": entry_price_ratio_norm,
            "unrealized_profit_norm": unrealized_profit_norm,
            "position_size": position_size,
        }