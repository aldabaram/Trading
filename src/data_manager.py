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