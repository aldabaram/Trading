import matplotlib.pyplot as plt

class Visualization:
    def __init__(self):
        plt.ion()  # Active le mode interactif au démarrage

    def show_prices(self, prices):
        plt.clf()  # Efface le graphique précédent
        plt.plot(prices)

        plt.xlabel("Temps")
        plt.ylabel("Prix BTC ($)")

        plt.title("Evolution du Bitcoin")

        plt.draw()
        plt.pause(0.1)