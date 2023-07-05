class Campaign:
    def __init__(self, id, total_budget, run_period, max_bid, targeting_group):
        self.id = id
        self.total_budget = total_budget
        self.run_period = run_period
        self.max_bid = max_bid
        self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period