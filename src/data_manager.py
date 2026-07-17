import csv
from datetime import datetime


def save_price(price):
    with open("data/prices.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(),
            price
        ])

def load_prices():
    prices = []
    with open("data/prices.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            prices.append(float(row[1]))
    return prices

def save_portfolio(portfolio, price):
    """prend en paramètre un objet portfolio afin de récupérer get_total_value et get_state et sauvegarde l'état du portefeuille dans un fichier CSV."""
    with open("data/portfolio.csv", "a") as file:
        writer = csv.writer(file)
        state = portfolio.get_state(price)
        writer.writerow([
            datetime.now(),
            state['usd'],
            state['btc'],
            state['total_value']
        ])

def load_portfolio_values():
    values = []
    with open("data/portfolio.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            values.append(float(row[3]))
    return values

def save_trade(trade_type, amount_usdt, amount_btc, price):
    """renvoie une ligne de type date,action,percentage,price,usd,btc dans un fichier CSV."""
    with open("data/trades.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(),
            trade_type,
            price,
            amount_usdt,
            amount_btc,
        ])

def load_trades():
    trades = []
    with open("data/trades.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            trades.append({
                "date": row[0],
                "type": row[1],
                "price": float(row[2]),
                "usd": float(row[3]),
                "btc": float(row[4]),
            })
    return trades