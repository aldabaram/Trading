MARKET_FEATURES = [
    "variation_1m_norm",
    "variation_5m_norm",
    "variation_1h_norm",
    "variation_6h_norm",
    "variation_24h_norm",
    "moving_average_norm",
    "volatility_norm",
    "price_to_high_norm",
    "price_to_low_norm",
    "momentum_norm",
    "drawdown_norm",
]

PORTFOLIO_FEATURES = [
    "cash_ratio",
    "crypto_ratio",
    "plus_value_norm",
    "holding_time_norm",
    "time_since_sell_norm",
    "entry_price_ratio_norm",
    "unrealized_profit_norm",
    "position_size",
]

# Combined features list used everywhere in the project
FEATURES = MARKET_FEATURES + PORTFOLIO_FEATURES


class ObservationBuilder:
    FEATURES = FEATURES
    
    def __init__(self):
        pass

    def build(self, market_state, portfolio_state):
        observation = []

        for key in MARKET_FEATURES:
            observation.append(market_state[key])

        for key in PORTFOLIO_FEATURES:
            observation.append(portfolio_state[key])

        return observation