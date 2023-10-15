from typing import Optional

import numpy as np
from scipy import stats

import src.configuration as config
from src.system.auction import AuctionInterface
from src.system.bid import Bid
from src.system.clock import Clock


class CampaignStatistics:
    num_iterations_per_spend_entry = config.num_iterations_per_day // config.num_spend_entries_per_day
    num_iterations_per_win_entry = config.num_iterations_per_day // config.num_win_entries_per_day

    def __init__(self, run_period: int):
        self.spend_history = []
        self.today_spend = []
        self.total_spent_today = 0
        self.auctions_won_history = []
        self.auctions_won_today = []
        self.days_left_to_run = run_period
        self.day_started = None
        self.day_ended = None
        self._reset_today_stats()

    def prepare_for_new_day(self):
        # set start day if not already set
        if self.day_started is None:
            self.day_started = Clock.days()
        # decrement the number of days left for the campaign to run
        self.days_left_to_run -= 1
        if self.days_left_to_run == 0:
            self.day_ended = Clock.days()
        # update history
        self.spend_history.append(self.today_spend)
        self.auctions_won_history.append(self.auctions_won_today)
        self._reset_today_stats()

    def update(self, payment: float):
        self.today_spend[self._calculate_spend_index_in_day()] += payment
        self.total_spent_today += payment
        self.auctions_won_today[self._calculate_win_index_in_day()] += 1

    def _reset_today_stats(self):
        self.today_spend = [0] * config.num_spend_entries_per_day
        self.auctions_won_today = [0] * config.num_win_entries_per_day
        self.total_spent_today = 0

    @staticmethod
    def _calculate_spend_index_in_day():
        return Clock.minute_in_day() // CampaignStatistics.num_iterations_per_spend_entry

    @staticmethod
    def _calculate_win_index_in_day():
        return Clock.minute_in_day() // CampaignStatistics.num_iterations_per_win_entry


class Campaign:
    def __init__(self, campaign_id: str, total_budget: float, run_period: int,
                 targeting_groups: dict[str, set[int]] = None, bids_distribution: stats.rv_continuous = None,
                 max_bid: float = None):
        self.id = campaign_id
        if max_bid and max_bid < config.campaign_minimal_bid:
            raise Exception('Invalid max_bid parameter.')
        self.max_bid = max_bid
        self.total_budget = total_budget
        self.daily_budget = total_budget / run_period
        self.bids_distribution = bids_distribution
        if self.bids_distribution is None:
            self.bids_distribution = config.bids_distribution_medium_budget
        assert self.daily_budget >= config.campaign_minimal_bid
        if targeting_groups is None:
            targeting_groups = {}
        self._targeting_groups = targeting_groups
        self.stats = CampaignStatistics(run_period=run_period)
        self.bids_cache = np.array([])

    def bid(self) -> Optional[Bid]:
        if not self.bids_cache.size:
            self.bids_cache = self.bids_distribution.rvs(size=config.bid_sampling_batch_size)
        bid_amount, self.bids_cache = self.bids_cache[-1], self.bids_cache[:-1]
        if self.max_bid:
            bid_amount = min(bid_amount, self.max_bid)
        if bid_amount < config.campaign_minimal_bid:
            return None
        return Bid(campaign_id=self.id, amount=bid_amount)

    def pay(self, amount: float):
        self.stats.update(amount)

    def prepare_for_new_day(self):
        self.stats.prepare_for_new_day()

    def days_left_to_run(self):
        return self.stats.days_left_to_run

    def spend_history(self) -> list[list[float]]:
        return self.stats.spend_history

    def spent_today(self) -> float:
        return self.stats.total_spent_today

    def num_auctions_won_history(self) -> list[list[int]]:
        return self.stats.auctions_won_history

    def num_auctions_won_today(self) -> int:
        return sum(self.stats.auctions_won_today)

    def cpm_daily_history(self) -> list[float]:
        return [1000 * sum(self.spend_history()[day]) / num_wins_in_day
                if (num_wins_in_day := sum(self.num_auctions_won_history()[day])) > 0 else None
                for day in range(len(self.num_auctions_won_history()))]

    def budget_utilization_daily_history(self) -> list[float]:
        return [sum(self.spend_history()[day]) / self.daily_budget
                for day in range(len(self.num_auctions_won_history()))]

    def overspend_value_daily_history(self) -> list[float]:
        return [spent_in_day - self.daily_budget
                if (spent_in_day := sum(self.spend_history()[day])) > self.daily_budget else 0
                for day in range(len(self.num_auctions_won_history()))]

    def is_relevant_auction(self, auction: AuctionInterface) -> bool:
        user_properties = auction.user_properties()
        for (feature, desired_values) in self._targeting_groups.items():
            if user_properties.get(feature) not in desired_values:
                return False
        return True

