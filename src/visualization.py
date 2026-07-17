import matplotlib.pyplot as plt


class Visualization:
    def __init__(self):
        plt.ion()
        self.figure, (self.price_axis, self.portfolio_axis) = plt.subplots(2, 1)
        self.figure.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.portfolio_value_axis = self.price_axis.twinx()
        self.portfolio = None
        self.price = None
        self.message = "b : acheter 100 USDT | s : vendre 25 % des BTC"
        self.price_history = []
        self.portfolio_history = []

    def show_prices(self, prices, portfolio, price):
        self.portfolio = portfolio
        self.price = price
        state = portfolio.get_state(price)
        total_value = portfolio.get_total_value(price)

        if len(prices) > len(self.price_history):
            self.price_history = prices
        else:
            self.price_history.append(prices[-1])

        self.portfolio_history.append(total_value)

        self.price_axis.clear()
        self.price_axis.plot(
            range(len(self.price_history)),
            self.price_history,
            color="tab:blue",
            label="Prix BTC",
        )
        self.price_axis.set_ylabel("Prix BTC (USDT)")
        self.price_axis.set_title("Bitcoin en temps réel")
        self.price_axis.grid(True, alpha=0.3)

        self.portfolio_value_axis.clear()
        self.portfolio_value_axis.plot(
            range(len(self.portfolio_history)),
            self.portfolio_history,
            color="tab:red",
            label="Valeur du portefeuille",
        )
        self.portfolio_value_axis.set_ylabel("Valeur du portefeuille (USDT)")

        self.portfolio_axis.clear()
        self.portfolio_axis.axis("off")
        self.portfolio_axis.text(
            0.02,
            0.7,
            (
                "Portefeuille virtuel\n"
                f"USDT : {state['usd']:,.2f}\n"
                f"BTC : {state['btc']:.8f}\n"
                f"Valeur totale : {total_value:,.2f} USDT\n\n"
                f"{self.message}"
            ),
            transform=self.portfolio_axis.transAxes,
            fontsize=11,
            va="center",
        )

        self.figure.tight_layout()
        self.figure.canvas.draw_idle()
        plt.pause(0.01)

    def _on_key_press(self, event):
        if self.portfolio is None or self.price is None:
            return
        try:
            if event.key == "b":
                amount = min(100.0, self.portfolio.usd)
                if amount == 0:
                    self.message = "Achat impossible : aucun USDT disponible."
                else:
                    self.portfolio.buy_percentage(100 * amount / self.portfolio.usd, self.price)
                    self.message = f"Achat : {amount:.2f} USDT"
            elif event.key == "s":
                amount = self.portfolio.btc * 0.25
                if amount == 0:
                    self.message = "Vente impossible : aucun BTC disponible."
                else:
                    self.portfolio.sell_percentage(25, self.price)
                    self.message = "Vente : 25 % du BTC"
        except ValueError as error:
            self.message = str(error)
