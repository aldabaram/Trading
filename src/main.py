import time

from constant import *
from data_manager import DataManager
from historical_data import HistoricalMarket
from market import Market
from market_analysis import MarketAnalysis
from portfolio import Portfolio
from visualisation import Visualisation

data_manager = DataManager()
if CLEAN_FILES:
    data_manager.clean_files()
data_manager.load_prices()

if USE_HISTORICAL:
    market_source = HistoricalMarket(HISTORICAL_DATA_FILE)
else:
    market_source = Market()
    market_source.start_background()
viz = Visualisation()

portfolio = Portfolio(STARTING_USD)
market_analysis = MarketAnalysis(update_interval=UPDATE_INTERVAL)

def execute_trade(transaction, percentage, price):
    if transaction == "buy":
        trade_type, amount_btc, amount_usdt = portfolio.buy_percentage(percentage, price)
        data_manager.save_trade(trade_type, amount_usdt, amount_btc, price)
    elif transaction == "sell":
        trade_type, amount_btc, amount_usdt = portfolio.sell_percentage(percentage, price)
        data_manager.save_trade(trade_type, amount_usdt, amount_btc, price)
    elif transaction == "hold":
        print("No trade executed. Holding position.")

while True:
    price_data = market_source.get_price()
    if price_data is None:
        if USE_HISTORICAL:
            break
        print("No price data available. Retrying...")
        time.sleep(UPDATE_INTERVAL)
        continue

    price = price_data["price"]
    date = price_data["date"]
    data_manager.save_price(price, date=date, display=not USE_HISTORICAL)
    market_analysis.update(price, date=date)
    data_manager.save_portfolio(portfolio, price, date=date)

    prices = data_manager.get_prices()
    portfolio_values = data_manager.get_portfolio_values()

    if USE_HISTORICAL:
        if len(prices) % 10 == 0:
            viz.show_prices(prices, data_manager.get_dates(), portfolio_values)
    else:
        viz.show_prices(prices, data_manager.get_dates(), portfolio_values)
    time.sleep(UPDATE_INTERVAL)