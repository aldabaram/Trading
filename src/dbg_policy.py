import numpy as np
from datetime import datetime

from stable_baselines3 import PPO

from constant import *
from market_analysis import MarketAnalysis
from historical_data import HistoricalMarket
from portfolio import Portfolio
from ai.observation_builder import ObservationBuilder
from ai.action_processor import ActionProcessor
from ai.trading_env import TradingEnv


BASE_DATE = datetime(2022, 7, 1, 2, 0, 0)

def date_to_step(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    minutes = int((d - BASE_DATE).total_seconds() / 60)
    return max(minutes, 3600)


historical_market = HistoricalMarket(HISTORICAL_DATA_FILE_2022_2024)
prices = historical_market.get_prices()

builder = ObservationBuilder()
processor = ActionProcessor()

env = TradingEnv(
    prices,
    Portfolio(STARTING_USD),
    MarketAnalysis(update_interval=60),
    builder,
    processor,
    random_start=False
)

model = PPO.load("models/best_model/best_model", env=env)

direction_names = ["SELL", "HOLD", "BUY"]
intensity_names = ["25%", "50%", "75%", "100%"]

test_dates = [
    "2022-11-05",
    "2023-01-01",
    "2023-06-01",
    "2024-01-01",
    "2024-03-01",
]

for date_str in test_dates:
    start_step = date_to_step(date_str)
    if start_step + env.max_steps >= len(prices):
        print(f"{date_str} : fenêtre trop proche de la fin, ignorée")
        continue

    obs, info = env.reset(options={"start_step": start_step})

    for _ in range(50):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)

    obs_batch = np.expand_dims(obs, axis=0)
    obs_tensor, _ = model.policy.obs_to_tensor(obs_batch)
    dist = model.policy.get_distribution(obs_tensor)

    # dist.distribution est une LISTE de 2 distributions catégorielles : [direction, intensité]
    direction_probs = dist.distribution[0].probs[0].detach().numpy()
    intensity_probs = dist.distribution[1].probs[0].detach().numpy()

    print(f"\n=== {date_str} (step {start_step}, prix {env.prices[env.current_step]:.2f}) ===")
    print("  Direction :")
    for name, p in zip(direction_names, direction_probs):
        print(f"    {name:6s} : {p:.4f}")
    print("  Intensité :")
    for name, p in zip(intensity_names, intensity_probs):
        print(f"    {name:6s} : {p:.4f}")