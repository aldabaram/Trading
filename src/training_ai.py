from stable_baselines3.common.monitor import Monitor

from constant import *
from historical_data import HistoricalMarket
from market_analysis import MarketAnalysis
from portfolio import Portfolio

from ai.agent import Agent
from ai.observation_builder import ObservationBuilder
from ai.action_processor import ActionProcessor
from ai.trading_env import TradingEnv

historical_market = HistoricalMarket(HISTORICAL_DATA_FILE_2019_2024)
prices = historical_market.get_prices()

print("Nombre de prix chargés :", len(prices))

builder = ObservationBuilder()
processor = ActionProcessor()

train_env = TradingEnv(
    prices,
    Portfolio(STARTING_USD),
    MarketAnalysis(
        update_interval=60
    ),
    builder,
    processor,
    random_start=True
)
train_env = Monitor(train_env)

eval_env = TradingEnv(
    prices,
    Portfolio(STARTING_USD),
    MarketAnalysis(
        update_interval=60
    ),
    builder,
    processor,
    random_start=True
)

eval_env = Monitor(eval_env)

agent = Agent(
    train_env,
    eval_env
)

agent.train(
    timesteps=2_000_000,
    checkpoint_freq=500_000
)

agent.save(
    "models/ppo_crypto_final"
)