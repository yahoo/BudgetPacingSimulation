import random
from typing import Optional

from src import constants
from src.bid import Bid


class Campaign:
    def __init__(self, campaign_id: str, total_budget: float, run_period: float, max_bid: float, targeting_group):
        self.id = campaign_id
        if max_bid <= constants.MINIMAL_BID:
            raise Exception('Invalid max_bid parameter.')
        self.max_bid = max_bid
        self.total_budget = total_budget
        self.run_period = run_period
        self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period

    def bid(self) -> Optional[Bid]:
        bid_amount = random.uniform(constants.MINIMAL_BID, self.max_bid)
        # Only in Step 4 we start tracking the campaigns' budgets
        # if bid_amount > self.daily_budget:
        #     bid_amount = self.daily_budget
        return Bid(campaign_id=self.id, amount=bid_amount)

