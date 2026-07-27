import json
import threading
from datetime import datetime

import websocket


class Market:
    def __init__(self):
        self.current_price = None
        self.current_date = None

    def _on_message(self, ws, message):
        data = json.loads(message)
        price = data.get("p")
        if price is not None:
            self.current_price = float(price)
            self.current_date = datetime.now()

    def start(self):
        connexion = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws/btcusdt@trade",
            on_message=self._on_message,
        )
        connexion.run_forever()

    def start_background(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()

    def get_price(self):
        if self.current_price is None:
            return None
        return {
            "date": self.current_date,
            "price": self.current_price,
        }