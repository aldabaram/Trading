import time
from datetime import datetime

from constant import UPDATE_INTERVAL

WINDOW_1M = 60
WINDOW_5M = 300
WINDOW_1H = 3600
WINDOW_6H = 21600
WINDOW_24H = 86400
MOMENTUM_WINDOW = 900
MAX_HISTORY_SECONDS = WINDOW_24H


class MarketAnalysis:
    def __init__(self, prices=None, update_interval=None):
        self.update_interval = update_interval or UPDATE_INTERVAL
        self.history = []

        if prices is not None:
            for price in prices:
                self.update(price)

    def _coerce_timestamp(self, date):
        if date is None:
            return time.time()
        if isinstance(date, datetime):
            return date.timestamp()
        if isinstance(date, (int, float)):
            return float(date)
        if isinstance(date, str):
            try:
                return datetime.fromisoformat(date.replace("Z", "+00:00")).timestamp()
            except ValueError:
                return time.time()
        return time.time()

    def update(self, price, date=None):
        if date is None and self.history:
            timestamp = self.history[-1][0] + self.update_interval
        else:
            timestamp = self._coerce_timestamp(date)

        self.history.append((timestamp, float(price)))
        self._prune_history(MAX_HISTORY_SECONDS)

    def _prune_history(self, window_seconds):
        if not self.history:
            return
        latest_timestamp = self.history[-1][0]
        cutoff = latest_timestamp - window_seconds
        self.history = [(timestamp, price) for timestamp, price in self.history if timestamp >= cutoff]

    def _get_window_prices(self, window_seconds):
        if not self.history:
            return []
        latest_timestamp = self.history[-1][0]
        cutoff = latest_timestamp - window_seconds
        return [price for timestamp, price in self.history if timestamp >= cutoff]

    def _get_variation(self, window_seconds):
        prices = self._get_window_prices(window_seconds)
        if len(prices) < 2:
            return 0

        oldest_price = prices[0]
        latest_price = prices[-1]
        if oldest_price == 0:
            return 0

        return ((latest_price - oldest_price) / oldest_price) * 100

    def get_variation(self, window_seconds=WINDOW_1M):
        return self._get_variation(window_seconds)

    def moving_average(self):
        if not self.history:
            return 0
        prices = [price for _, price in self.history]
        return sum(prices) / len(prices)

    def volatility(self):
        if len(self.history) < 2:
            return 0
        mean = self.moving_average()
        prices = [price for _, price in self.history]
        variance = sum((price - mean) ** 2 for price in prices) / len(prices)
        return variance ** 0.5

    def momentum(self, window_seconds=MOMENTUM_WINDOW):
        prices = self._get_window_prices(window_seconds)
        if len(prices) < 2:
            return 0

        returns = []
        previous_price = prices[0]
        for price in prices[1:]:
            if previous_price == 0:
                previous_price = price
                continue
            returns.append((price - previous_price) / previous_price * 100)
            previous_price = price

        if not returns:
            return 0
        return sum(returns) / len(returns)

    def drawdown(self, window_seconds=WINDOW_24H):
        prices = self._get_window_prices(window_seconds)
        if not prices:
            return 0

        peak = max(prices)
        if peak == 0:
            return 0

        latest_price = prices[-1]
        return ((latest_price - peak) / peak) * 100

    def price_relative_to_high(self, window_seconds=WINDOW_24H):
        prices = self._get_window_prices(window_seconds)

        if not prices:
            return 0

        high = max(prices)
        latest_price = self.history[-1][1]

        if high == 0:
            return 0

        return ((latest_price - high) / high) * 100

    def price_relative_to_low(self, window_seconds=WINDOW_24H):
        prices = self._get_window_prices(window_seconds)
        if not prices:
            return 1

        low = min(prices)
        latest_price = self.history[-1][1]
        if low == 0:
            return 2

        return latest_price / low

    def _normalize_variation(self, variation, cap=10.0):
        normalized = (variation + cap) / (2 * cap)
        return max(0.0, min(1.0, normalized))

    def _normalize_negative_variation(self, variation, cap=20.0):
        if variation > 0:
            variation = 0
        normalized = 1.0 + (variation / cap)
        return max(0.0, min(1.0, normalized))

    def _normalize_ratio(self, value, cap=2.0):
        normalized = value / cap
        return max(0.0, min(1.0, normalized))

    def normalized_moving_average(self):
        last_price = self.history[-1][1] if self.history else 0
        if not last_price:
            return 0
        value = self.moving_average() / last_price
        return self._normalize_ratio(value, cap=2.0)

    def normalized_volatility(self):
        last_price = self.history[-1][1] if self.history else 0
        if not last_price:
            return 0
        value = self.volatility() / last_price
        return self._normalize_ratio(value, cap=0.1)

    def normalized_price_relative_to_high(self):
        value = self.price_relative_to_high()

        # 0% = sommet
        # -20% = grosse baisse
        normalized = (value + 20) / 20

        return max(0.0, min(1.0, normalized))

    def normalized_price_relative_to_low(self):
        return self._normalize_ratio(self.price_relative_to_low(), cap=2.0)

    def normalized_momentum(self):
        return self._normalize_variation(self.momentum(), cap=10.0)

    def normalized_drawdown(self):
        return self._normalize_negative_variation(self.drawdown(), cap=20.0)

    def get_state(self):
        last_price = self.history[-1][1] if self.history else None
        variation_1m = self.get_variation(WINDOW_1M)
        variation_5m = self.get_variation(WINDOW_5M)
        variation_1h = self.get_variation(WINDOW_1H)
        variation_6h = self.get_variation(WINDOW_6H)
        variation_24h = self.get_variation(WINDOW_24H)
        momentum = self.momentum()
        drawdown = self.drawdown()
        price_to_high = self.price_relative_to_high()
        price_to_low = self.price_relative_to_low()

        return {
            "variation_1m": variation_1m,
            "variation_5m": variation_5m,
            "variation_1h": variation_1h,
            "variation_6h": variation_6h,
            "variation_24h": variation_24h,
            "moving_average": self.moving_average(),
            "volatility": self.volatility(),
            "price_to_high": price_to_high,
            "price_to_low": price_to_low,
            "momentum": momentum,
            "drawdown": drawdown,
            "variation_1m_norm": self._normalize_variation(variation_1m),
            "variation_5m_norm": self._normalize_variation(variation_5m),
            "variation_1h_norm": self._normalize_variation(variation_1h),
            "variation_6h_norm": self._normalize_variation(variation_6h),
            "variation_24h_norm": self._normalize_variation(variation_24h),
            "moving_average_norm": self.normalized_moving_average(),
            "volatility_norm": self.normalized_volatility(),
            "price_to_high_norm": self.normalized_price_relative_to_high(),
            "price_to_low_norm": self.normalized_price_relative_to_low(),
            "momentum_norm": self.normalized_momentum(),
            "drawdown_norm": self.normalized_drawdown(),
        }
