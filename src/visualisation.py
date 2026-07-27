import matplotlib.pyplot as plt
from constant import STARTING_USD

class Visualisation:

    def __init__(self):
        plt.ion()

        self.fig, self.ax_price = plt.subplots()
        self.ax_portfolio = self.ax_price.twinx()

        self.price_line, = self.ax_price.plot([], [], label="BTC")
        self.portfolio_line, = self.ax_portfolio.plot(
            [],
            [],
            color="red",
            label="Portfolio"
        )

        self.ax_price.set_xlabel("Temps")
        self.ax_price.set_ylabel("Prix BTC")
        self.ax_portfolio.set_ylabel("Valeur portefeuille")

        self.ax_price.legend(loc="upper left")
        self.ax_portfolio.legend(loc="upper right")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update(self, prices, portfolio_values):

        x = range(len(prices))

        self.price_line.set_data(
            x,
            prices
        )

        self.portfolio_line.set_data(
            x,
            portfolio_values
        )

        self.ax_price.relim()
        self.ax_price.autoscale_view()

        self.ax_portfolio.relim()
        self.ax_portfolio.autoscale_view()

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
    
    def update_live(self, prices, portfolio_values, step, action, value):
        self.update(
            prices,
            portfolio_values
        )

        performance = (
            value - STARTING_USD
        ) / STARTING_USD * 100

        self.ax_price.set_title(
            f"Step : {step} | "
            f"Portefeuille : {value:.2f}$ | "
            f"Performance : {performance:.2f}% | "
            f"Action : {action}"
        )

        plt.pause(0.001)

    def show_prices(self, prices, portfolio_values):

        self.update(
            prices,
            portfolio_values
        )

        plt.pause(0.001)
