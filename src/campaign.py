class Campaign:
    def __init__(self, campaign_id: int, total_budget: float, run_period: float, max_bid: float, targeting_group):
        self.campaign_id = campaign_id
        self.total_budget = total_budget
        self.run_period = run_period
        self.max_bid = max_bid
        self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period
