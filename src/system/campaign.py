import random
from typing import Optional

import src.configuration as config
from src.system.bid import Bid
from src.system.clock import Clock


class CampaignStatistics:
    # Defines the length of each entry in the spend / #won lists (lists of lists, actually).
    n_history_entries_per_day = config.n_iterations_per_day // config.n_iterations_per_hist_interval

    def __init__(self):
        self.spend_history = []
        self.today_spend = []
        self.auctions_won_history = []
        self.auctions_won_today = []
        self.day_created = Clock.days()
        self.setup_new_day()

    def setup_new_day(self):
        self.spend_history.append(self.today_spend)
        self.today_spend = [0] * CampaignStatistics.n_history_entries_per_day
        self.auctions_won_history.append(self.auctions_won_today)
        self.auctions_won_today = [0] * CampaignStatistics.n_history_entries_per_day

    def update(self, payment: float):
        hist_interval_index = (Clock.minutes() // config.n_iterations_per_hist_interval) \
                              % CampaignStatistics.n_history_entries_per_day
        self.today_spend[hist_interval_index] += payment
        self.auctions_won_today[hist_interval_index] += 1


class Campaign:
    def __init__(self, campaign_id: str, total_budget: float, run_period: int, max_bid: float):
        self.id = campaign_id
        if max_bid <= config.campaign_minimal_bid:
            raise Exception('Invalid max_bid parameter.')
        self.max_bid = max_bid
        self.total_budget = total_budget
        self.run_period = run_period
        # self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period
        self.stats = CampaignStatistics()

    def bid(self) -> Optional[Bid]:
        bid_amount = random.uniform(config.campaign_minimal_bid, self.max_bid)
        # Only in Step 4 we start tracking the campaigns' budgets
        # if bid_amount > self.daily_budget:
        #     bid_amount = self.daily_budget
        return Bid(campaign_id=self.id, amount=bid_amount)

    def pay(self, amount: float):
        self.stats.update(amount)

    def setup_new_day(self):
        if self.run_period > 0:
            self.run_period -= 1
        self.stats.setup_new_day()

    def spend_history(self) -> list[list[float]]:
        return self.stats.spend_history

    def spent_today(self) -> float:
        return sum(self.stats.today_spend)

    def n_auctions_won_today(self) -> int:
        return sum(self.stats.auctions_won_today)
