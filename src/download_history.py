import os
import shutil
import zipfile
import requests
import csv
from datetime import datetime


START_YEAR = 2019
START_MONTH = 1

END_YEAR = 2024
END_MONTH = 1

OUTPUT = "data/historical/BTC_prices_2019_2024.csv"
TEMP = "data/historical/temp"


def download_file(url, path):
    """Télécharge un fichier Binance."""

    response = requests.get(url)

    if response.status_code == 200:

        with open(path, "wb") as file:
            file.write(response.content)

        return True

    return False


def extract_prices(zip_path, writer):
    """Extrait les prix BTC depuis une archive."""

    with zipfile.ZipFile(zip_path, "r") as archive:

        filename = archive.namelist()[0]

        with archive.open(filename) as csv_file:

            reader = csv.reader(
                line.decode("utf-8")
                for line in csv_file
            )

            for row in reader:

                if not row[0].isdigit():
                    continue

                try:

                    timestamp = int(row[0])

                    # Binance utilise parfois ms ou µs
                    if timestamp > 100000000000000:
                        timestamp //= 1000000
                    else:
                        timestamp //= 1000

                    date = datetime.fromtimestamp(timestamp)

                    writer.writerow([
                        date.strftime("%Y-%m-%d %H:%M:%S"),
                        row[4]
                    ])

                except (ValueError, IndexError):
                    continue


def main():

    os.makedirs(
        "data/historical",
        exist_ok=True
    )

    os.makedirs(
        TEMP,
        exist_ok=True
    )


    with open(
        OUTPUT,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "date",
            "price"
        ])


        for year in range(
            START_YEAR,
            END_YEAR + 1
        ):

            start = (
                START_MONTH
                if year == START_YEAR
                else 1
            )

            end = (
                END_MONTH
                if year == END_YEAR
                else 12
            )


            for month in range(
                start,
                end + 1
            ):

                month_text = f"{month:02}"

                name = (
                    f"BTCUSDT-1m-{year}-{month_text}.zip"
                )

                url = (
                    "https://data.binance.vision/"
                    "data/spot/monthly/klines/"
                    f"BTCUSDT/1m/{name}"
                )

                zip_path = f"{TEMP}/{name}"


                print(
                    f"Téléchargement {name}"
                )


                if download_file(
                    url,
                    zip_path
                ):

                    extract_prices(
                        zip_path,
                        writer
                    )

                    os.remove(zip_path)

                    print("OK")

                else:

                    print("Introuvable")


    # Suppression du dossier temporaire
    if os.path.exists(TEMP):

        shutil.rmtree(TEMP)


    print(
        "Terminé :",
        OUTPUT
    )


if __name__ == "__main__":
    main()