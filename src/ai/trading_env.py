import gymnasium as gym
from gymnasium import spaces
import numpy as np

from ai.observation_builder import FEATURES
from constant import STARTING_USD, TRADING_FEE


class TradingEnv(gym.Env):

    def __init__(
        self,
        prices,
        portfolio,
        market_analysis,
        observation_builder,
        action_processor,
        random_start=True,
        start_step_pool=None
    ):
        super().__init__()

        self.max_steps = 30000
        self.random_start = random_start
        self.start_step_pool = start_step_pool

        self.prices = prices
        self.portfolio = portfolio

        self.market_analysis = market_analysis
        self.observation_builder = observation_builder
        self.action_processor = action_processor

        self.current_step = 3600
        self.previous_value = None

        self.total_reward = 0
        self.total_fees = 0

        self.trades = []

        self.hold_steps = 0
        self.price_history = []
        self.portfolio_history = []


        self.observation_space = spaces.Box(
            low=0,
            high=1,
            shape=(len(FEATURES),),
            dtype=np.float32
        )

        self.action_space = spaces.MultiDiscrete([3, 4])


    def reset(self, seed=None, options=None):

        super().reset(seed=seed)

        self.total_reward = 0
        self.total_fees = 0
        self.trades = []
        self.hold_steps = 0

        start_step = None
        if options is not None:
            start_step = options.get("start_step")

        if start_step is not None:
            self.current_step = start_step

        elif self.start_step_pool is not None:
            self.current_step = int(np.random.choice(self.start_step_pool))

        elif self.random_start:
            self.current_step = np.random.randint(
                3600,
                len(self.prices) - self.max_steps
            )

        else:
            self.current_step = 3600

        price = self.prices[self.current_step]
        self.portfolio.reset(price)

        # Départ 50% USD / 50% BTC
        half_usd = STARTING_USD / 2

        self.portfolio.usd = half_usd
        self.portfolio.btc = (half_usd * (1 - TRADING_FEE)) / price

        self.previous_value = self.portfolio.get_total_value(price)

        self.price_history = [price]
        self.portfolio_history = [self.previous_value]

        self.market_analysis.history = []

        start = self.current_step - 3600
        for p in self.prices[start:self.current_step+1]:
            self.market_analysis.update(p)

        obs = self.observation_builder.build(
            self.market_analysis.get_state(),
            self.portfolio.get_state(price)
        )

        return np.array(obs, dtype=np.float32), {}

    def step(self, action):

        usd_before = self.portfolio.usd
        btc_before = self.portfolio.btc

        price = self.prices[self.current_step]

        transaction, percentage = self.action_processor.process(action)

        trade_success = True

        if transaction == "buy":
            trade_success, _, _, _ = self.portfolio.buy_percentage(
                percentage,
                price
            )

        elif transaction == "sell":
            trade_success, _, _, _ = self.portfolio.sell_percentage(
                percentage,
                price
            )

        if transaction == "hold":
            self.hold_steps += 1

        else:
            self.hold_steps = 0

            self.trades.append({
                "step": self.current_step,
                "type": transaction,
                "price": price,
                "percentage": float(percentage),
                "fee": self.portfolio.last_fee
            })

        self.current_step += 1

        terminated = (
            self.current_step >= len(self.prices) - 1
            or len(self.price_history) >= self.max_steps
        )

        next_price = self.prices[self.current_step]

        self.market_analysis.update(next_price)

        # Valeur réelle après action + fees + mouvement de prix
        new_value = self.portfolio.get_total_value(next_price)

        self.price_history.append(next_price)
        self.portfolio_history.append(new_value)

        self.total_fees += self.portfolio.last_fee

        # ===========================
        # Reward : croissance log du portefeuille
        # Les frais sont déjà inclus dans new_value via portfolio.buy/sell_percentage
        # => pas besoin de les soustraire une seconde fois ici.
        # ===========================

        if self.previous_value > 0 and new_value > 0:
            reward = np.log(new_value / self.previous_value)
        else:
            reward = 0.0

        # Seule pénalité "à la main" conservée : contrainte de faisabilité,
        # pas un jugement sur la stratégie (ex: vendre sans BTC disponible)
        if not trade_success:
            reward -= 0.02
    

        self.total_reward += reward

        self.previous_value = new_value

        observation = self.observation_builder.build(
            self.market_analysis.get_state(),
            self.portfolio.get_state(next_price)
        )

        info = {
            "portfolio_value": new_value,
            "transaction": transaction,
            "percentage": float(percentage),
            "total_reward": self.total_reward,
            "trades": len(self.trades),
            "fee": self.portfolio.last_fee
        }

        return (
            np.array(observation, dtype=np.float32),
            reward,
            terminated,
            False,
            info
        )

    def get_episode_data(self):

        return {

            "prices": self.price_history,

            "portfolio_values":
                self.portfolio_history,

            "trades":
                self.trades,

            "reward":
                self.total_reward,

            "total_fees":
                self.total_fees

        }