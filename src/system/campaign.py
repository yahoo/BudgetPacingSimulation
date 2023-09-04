import math
from typing import Optional

from scipy import stats

import src.configuration as config
from src import constants
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
                 bids_distribution: stats.rv_continuous = None):
        self.id = campaign_id
        self.bids_distribution = bids_distribution
        if self.bids_distribution is None:
            mu = constants.distribution_of_mu_of_bids_log_distribution.rvs()
            sigma = constants.distribution_of_sigma_of_bids_log_distribution.rvs()
            while sigma < 0:
                # re-sample until sigma >= 0
                sigma = constants.distribution_of_sigma_of_bids_log_distribution.rvs()
            self.bids_distribution = stats.norm(loc=mu, scale=sigma)
        self.total_budget = total_budget
        # self.targeting_group = targeting_group
        self.daily_budget = total_budget / run_period        
        assert self.daily_budget >= config.campaign_minimal_bid
        self.stats = CampaignStatistics(run_period=run_period)

    def bid(self) -> Optional[Bid]:
        bid_amount = math.exp(self.bids_distribution.rvs())
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
