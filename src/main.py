import time
from market import Market
from visualization import Visualization
from data_manager import save_price, load_prices

UPDATE_TIME = 5

market = Market()
viz = Visualization()  # Crée l'instance au démarrage (plt.ion() s'active ici)

while True:
    # On récupère le prix du Bitcoin
    price = market.get_btc_price()
    # On sauve le prix dans le fichier CSV
    save_price(price)
    # On charge les prix depuis le fichier CSV
    prices = load_prices()
    # On affiche les prix
    viz.show_prices(prices)
    time.sleep(UPDATE_TIME)