import matplotlib.pyplot as plt


class Visualization:
    def __init__(self):
        plt.ion()

    def show_prices(self, prices):
        plt.clf()
        plt.plot(prices)
        plt.xlabel("Temps")
        plt.ylabel("Prix BTC ($)")
        plt.title("Evolution du Bitcoin")
        plt.draw()
        plt.pause(0.01)