import matplotlib.pyplot as plt

class Visualisation:

    def __init__(self):
        plt.ion()

    def show_prices(self, prices, portfolio_values):
        """ affiche les prix du Bitcoin et la valeur du portefeuille en temps réel. """
        plt.clf()

        ax1 = plt.gca()
        ax1.plot(prices)
        ax1.set_xlabel("Temps")
        ax1.set_ylabel("Prix BTC")

        ax2 = ax1.twinx()
        ax2.plot(portfolio_values, color="red")
        ax2.set_ylabel("Valeur portefeuille")
        plt.title("Bitcoin et portefeuille")

        plt.draw()
        plt.pause(0.01)