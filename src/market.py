import json
import threading
import websocket


class Market:
    def __init__(self):
        self.current_price = None

    def _on_message(self, ws, message):
        data = json.loads(message)
        price = data.get("p")
        if price is not None:
            self.current_price = float(price)

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
        return self.current_price