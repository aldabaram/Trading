import time

from data_manager import load_prices, save_price
from market import Market
from visualization import Visualization

UPDATE_INTERVAL = 0.5

market = Market()
viz = Visualization()

market.start_background()

while True:
    price = market.get_price()
    if price is not None:
        print(price)
        save_price(price)
        prices = load_prices()
        viz.show_prices(prices)
    time.sleep(UPDATE_INTERVAL)