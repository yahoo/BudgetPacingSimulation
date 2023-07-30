import random
from typing import Optional

from src.auction import AuctionInterface
from src.bid import Bid


class Campaign:
    def __init__(self, campaign_id: str, total_budget: float, run_period: float, max_bid: float, targeting_group):
        self.id = campaign_id
        self.total_budget = total_budget
        self.run_period = run_period
        self.max_bid = max_bid
        self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period

    def bid(self, auction: AuctionInterface) -> Optional[Bid]:
        if self.max_bid < auction.min_bid():
            return None
        bid_amount = random.uniform(auction.min_bid(), self.max_bid)
        # Only in Step 4 we start tracking the campaigns' budgets
        # if bid_amount > self.daily_budget:
        #     bid_amount = self.daily_budget

        return Bid(campaign_id=self.id, amount=bid_amount)
