import random
from typing import Optional

import src.configuration as config
from src.system.bid import Bid
from src.system.budget_pacing.mystique.clock import Clock


class CampaignStatistics:
    def __init__(self):
        if config.n_iterations_per_day % config.n_iterations_per_hist_interval != 0:
            raise Exception('invalid iterations_per_interval parameter')
        self._iterations_per_interval = config.n_iterations_per_hist_interval
        self._intervals_per_day = config.n_iterations_per_day // self._iterations_per_interval
        self.spend_history = []
        self.auctions_won = []
        self.day_created = Clock.days()
        self.setup_new_day()

    def setup_new_day(self):
        self.spend_history.append([0] * self._intervals_per_day)
        self.auctions_won.append([0] * self._intervals_per_day)

    def update(self, payment: float):
        hist_interval_index = (Clock.minutes() // self._iterations_per_interval) % self._intervals_per_day
        self.auctions_won[Clock.days()][hist_interval_index] += 1
        self.spend_history[Clock.days()][hist_interval_index] += payment


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

    def _daily_spend(self) -> list[float]:
        return [sum(day_spend) for day_spend in self.stats.spend_history]

    def daily_budget_utilization(self) -> list[float]:
        return [total_day_spend/self.daily_budget for total_day_spend in self._daily_spend()]

    def spend_history(self) -> list[list[float]]:
        return self.stats.spend_history

    def spent_today(self) -> float:
        return sum(self.stats.spend_history[-1])



