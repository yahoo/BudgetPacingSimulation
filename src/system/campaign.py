import random
from typing import Optional

import src.configuration as config
from src.system.bid import Bid
from src.system.clock import Clock


class CampaignStatistics:
    def __init__(self):
        self.spend_history = []
        self.today_spend = []
        self.auctions_won_history = []
        self.auctions_won_today = []
        self.day_created = Clock.days()
        self._reset_today_stats()

    def setup_new_day(self):
        self.spend_history.append(self.today_spend)
        self.auctions_won_history.append(self.auctions_won_today)
        self._reset_today_stats()

    def update(self, payment: float):
        self.today_spend[self._calculate_spend_index_in_day()] += payment
        self.auctions_won_today[self._calculate_win_index_in_day()] += 1

    def _reset_today_stats(self):
        self.today_spend = [0] * config.num_spend_entries_per_day
        self.auctions_won_today = [0] * config.num_win_entries_per_day

    @staticmethod
    def _calculate_spend_index_in_day():
        num_iterations_per_spend_entry = config.n_iterations_per_day // config.num_spend_entries_per_day
        return (Clock.minutes_in_day() // num_iterations_per_spend_entry) % config.num_spend_entries_per_day

    @staticmethod
    def _calculate_win_index_in_day():
        num_iterations_per_spend_entry = config.n_iterations_per_day // config.num_win_entries_per_day
        return (Clock.minutes_in_day() // num_iterations_per_spend_entry) % config.num_win_entries_per_day


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
