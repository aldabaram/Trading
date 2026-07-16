import yfinance as yf


class Market:

    def get_btc_price(self):

        bitcoin = yf.Ticker("BTC-USD")

        data = bitcoin.history(period="1d")

        price = data["Close"].iloc[-1]

        return price