class Agent:
    def __init__(self):
        pass

    def decide(self, market_state, portfolio_state):
        variation = market_state["variation"]
        if variation < -0.001:
            return "buy", 10
        elif variation > 0.001:
            return "sell", 10
        else:
            return "hold", 0