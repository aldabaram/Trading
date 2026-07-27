from stable_baselines3 import PPO
from datetime import datetime
import numpy as np
from constant import *
from market_analysis import MarketAnalysis
from historical_data import HistoricalMarket
from visualisation import Visualisation
from portfolio import Portfolio
from ai.observation_builder import ObservationBuilder
from ai.action_processor import ActionProcessor
from ai.trading_env import TradingEnv

VISUAL = False
BASE_DATE = datetime(2019, 1, 1, 1, 0, 0)

def date_to_step(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    minutes = int((d - BASE_DATE).total_seconds() / 60)
    return max(minutes, 3600)


historical_market = HistoricalMarket(HISTORICAL_DATA_FILE_2019_2024)
prices = historical_market.get_prices()

builder = ObservationBuilder()
processor = ActionProcessor()
viz = Visualisation()

env = TradingEnv(
    prices,
    Portfolio(STARTING_USD),
    MarketAnalysis(update_interval=60),
    builder,
    processor,
    random_start=False
)

model = PPO.load("models/best_model/best_model", env=env)

# Fenêtres variées : crashs, rallies, périodes calmes
test_dates = [
    "2022-08-01",
    "2022-09-01",
    "2022-11-05",   # crash FTX
    "2022-12-15",
    "2023-01-01",   # reprise post-crash
    "2023-02-15",
    "2023-04-01",
    "2023-06-01",
    "2023-08-01",
    "2023-10-01",
    "2023-11-15",
    "2024-01-01",   # début rally 2024
    "2024-03-01",   # pic du rally
    "2024-05-01",
    "2024-07-01",
]

results = []

for date_str in test_dates:
    start_step = date_to_step(date_str)

    if start_step + env.max_steps >= len(prices):
        print(f"{date_str} : fenêtre trop proche de la fin des données, ignorée")
        continue

    obs, info = env.reset(options={"start_step": start_step})

    terminated = truncated = False
    while not terminated and not truncated:
        action, _ = model.predict(obs, deterministic=True)   # <-- FIX ICI
        obs, reward, terminated, truncated, info = env.step(action)

        if VISUAL:
            if env.current_step % 1 == 0:
                viz.update_live(
                    env.price_history,
                    env.portfolio_history,
                    env.current_step,
                    info["transaction"],
                    info["portfolio_value"]
                )

    initial_price = env.price_history[0]
    final_price = env.price_history[-1]
    btc_bought = (STARTING_USD * (1 - TRADING_FEE)) / initial_price
    buy_hold_value = btc_bought * final_price

    agent_value = env.portfolio_history[-1]

    print(f"\n=== Fenêtre démarrant {date_str} (step {start_step}) ===")
    print(f"Prix initial : {initial_price:.2f} | Prix final : {final_price:.2f}")
    print(f"Agent     : {agent_value:.2f}")
    print(f"Buy&Hold  : {buy_hold_value:.2f}")
    print(f"Trades    : {len(env.trades)}")

    results.append({
        "date": date_str,
        "agent": agent_value,
        "buy_hold": buy_hold_value,
        "trades": len(env.trades)
    })

print("\n\n=== RÉSUMÉ ===")
for r in results:
    diff = r["agent"] - r["buy_hold"]
    print(f"{r['date']:12s} | agent={r['agent']:.2f} | b&h={r['buy_hold']:.2f} | diff={diff:+.2f} | trades={r['trades']}")

diffs = [r["agent"] - r["buy_hold"] for r in results]
win_rate = sum(1 for d in diffs if d > 0) / len(diffs)
avg_diff = sum(diffs) / len(diffs)

print(f"\nTaux de fenêtres où l'agent bat le buy&hold : {win_rate*100:.0f}%")
print(f"Différence moyenne (agent - buy&hold) : {avg_diff:+.2f}")