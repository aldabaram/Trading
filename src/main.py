import time

from data_manager import *
from market import Market
from visualisation import Visualisation
from portfolio import Portfolio
from market_analysis import MarketAnalysis
from agent import Agent

UPDATE_INTERVAL = 0.1

market = Market()
viz = Visualisation()
agent = Agent()
portfolio = Portfolio(1000)
market_analysis = MarketAnalysis([])
market.start_background()

def execute_trade(transaction, percentage, price):
    if transaction == "buy":
        trade_type, amount_btc, amount_usdt = portfolio.buy_percentage(percentage, price)
        save_trade(trade_type, amount_usdt, amount_btc, price)
    elif transaction == "sell":
        trade_type, amount_btc, amount_usdt = portfolio.sell_percentage(percentage, price)
        save_trade(trade_type, amount_usdt, amount_btc, price)
    elif transaction == "hold":
        print("No trade executed. Holding position.")

while True:
    price = market.get_price()
    if price is not None:
        value = portfolio.get_total_value(price)
        save_price(price)
        market_analysis.update(price)
        save_portfolio(portfolio, price)
        prices = load_prices()
        portfolio_values = load_portfolio_values()
        transaction, percentage = agent.decide(market_analysis.get_state(), portfolio.get_state(price))
        execute_trade(transaction, percentage, price)
        print("Portfolio State:", portfolio.get_state(price))
        print("Market Analysis State:", market_analysis.get_state())
        viz.show_prices(
            prices,
            portfolio_values
        )