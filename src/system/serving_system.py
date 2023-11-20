# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import numpy as np

import src.constants as constants
from src.system.auction import *
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.campaign import Campaign
from src.system.clock import Clock


class ServingSystem:
    tracked_campaigns: dict[str, Campaign]
    old_campaigns: dict[str, Campaign]

    def __init__(self, pacing_system: PacingSystemInterface = None, tracked_campaigns: list[Campaign] = None):
        if tracked_campaigns is None:
            tracked_campaigns = []
        self.tracked_campaigns = {}
        self.old_campaigns = {}
        self.pacing_system = pacing_system
        self.pending_pacing_spend_updates = {}
        for campaign in tracked_campaigns:
            self.add_campaign(campaign)
        self.untracked_bids_cache = np.array([])

    def add_campaign(self, campaign: Campaign):
        if campaign is None:
            raise Exception('cannot add a None campaign')
        if campaign.id in self.tracked_campaigns or campaign.id in self.old_campaigns:
            raise Exception('campaign id already exists')
        self.tracked_campaigns[campaign.id] = campaign
        if self.pacing_system is not None:
            self.pacing_system.add_campaign(campaign)

    def get_bids(self, auction: AuctionInterface) -> list[Bid]:
        num_relevant_campaigns = 0
        bids = []
        # get "real" bids
        for campaign in self.tracked_campaigns.values():
            # check if the auction is relevant (matches campaign's target group) to the campaign
            if not campaign.is_relevant_auction(auction):
                continue
            num_relevant_campaigns += 1  # counting the number of campaigns for which the auction is relevant
            # make sure the campaign hasn't reached its daily budget
            if campaign.spent_today() >= campaign.daily_budget:
                continue
            bid = campaign.bid()
            if bid is None:
                continue
            if self.pacing_system is not None:
                pacing_signal = self.pacing_system.get_pacing_signal(campaign_id=campaign.id)
                bid.amount *= pacing_signal
            if bid.amount > 0:
                bids.append(bid)
        bids += self._generate_untracked_bids(num_relevant_campaigns=num_relevant_campaigns)
        return bids

    def update_winners(self, winners: list[AuctionWinner]):
        for winner in winners:
            if winner.bid.campaign_id in self.tracked_campaigns:
                # update campaign
                self.tracked_campaigns[winner.bid.campaign_id].pay(winner.payment)

                if self.pacing_system is not None:
                    # add payment to the pending updates which will be sent to the budget pacing system
                    self.pending_pacing_spend_updates[winner.bid.campaign_id] = self.pending_pacing_spend_updates.get(
                        winner.bid.campaign_id, 0) + winner.payment

    def end_iteration(self):
        self._end_of_minute_campaign_updates()  # updates campaigns' lifetime statistic
        # Budget Pacing periodic (every minute) spend updates
        self._update_pacing_system()
        # Check if this is the last iteration of the day
        if Clock.minute_in_day() == constants.num_minutes_in_day - 1:
            # Perform daily campaign updates
            self._end_of_day_campaign_updates()

    def _update_pacing_system(self):
        if self.pacing_system is None:
            return
        for campaign in self.tracked_campaigns.values():
            # get the spend amount of each campaign during the last minute, and send it to the budget pacing system
            spend = self.pending_pacing_spend_updates.pop(campaign.id, 0)
            self.pacing_system.end_iteration(campaign_id=campaign.id, spend_since_last_iteration=spend)

    def _end_of_minute_campaign_updates(self):
        # update the number of minutes alive statistic for each campaign
        for campaign in self.tracked_campaigns.values():
            if campaign.spent_today() < campaign.daily_budget \
                    and Clock.minute_in_day() < constants.num_minutes_in_day - 1:
                # we increment campaigns' minutes_alive counter at the end of each minute of the day
                # - except the last minute of the day, since a campaign that hasn't depleted its budget by the end of
                # the current minute will be participating in auctions in the following minute of the same day.
                campaign.stats.minutes_alive_today += 1

    def _end_of_day_campaign_updates(self):
        for campaign in list(self.tracked_campaigns.values()):
            campaign.prepare_for_new_day()
            assert campaign.days_left_to_run() >= 0
            if campaign.days_left_to_run() == 0:
                # add campaign to the structure of campaigns that are done
                self.old_campaigns[campaign.id] = campaign
                # remove campaign from the structure of active campaigns
                self.tracked_campaigns.pop(campaign.id)

    def _generate_untracked_bids(self, num_relevant_campaigns: int) -> list[Bid]:
        num_untracked_bids = self._calculate_number_of_untracked_bids(num_relevant_campaigns)
        if self.untracked_bids_cache.size < num_untracked_bids:
            sampled_batch_size = max(num_untracked_bids, config.bid_sampling_batch_size)
            self.untracked_bids_cache = config.untracked_bids_distribution.rvs(size=sampled_batch_size)
        sampled_bids, self.untracked_bids_cache = self.untracked_bids_cache[-num_untracked_bids:], self.untracked_bids_cache[:-num_untracked_bids]
        return [Bid(campaign_id='untracked_campaign_' + str(i), amount=sampled_bids[i]) for i in range(sampled_bids.size)]

    def get_statistics_per_campaign_csv_rows(self) -> list[dict[str, object]]:
        campaigns_statistics_as_rows = []
        for campaign in self._all_campaigns():
            campaign_statistics = {
                constants.FIELD_CAMPAIGN_ID: campaign.id,
                constants.FIELD_DAY_STARTED: campaign.stats.day_started,
                constants.FIELD_DAY_ENDED: campaign.stats.day_ended,
                constants.FIELD_DAILY_BUDGET: campaign.daily_budget,
                constants.FIELD_NUM_WINS: campaign.num_auctions_won_history(),
                constants.FIELD_CPM: campaign.cpm_daily_history(),
                constants.FIELD_BUDGET_UTILIZATION: campaign.budget_utilization_daily_history(),
                constants.FIELD_OVERSPEND: campaign.overspend_value_daily_history(),
                constants.FIELD_MINUTES_ALIVE: campaign.minutes_alive_history()
            }
            if self.pacing_system:
                # merge campaign's pacing statistics the basic statistics
                campaign_statistics |= self.pacing_system.get_pacing_statistics(campaign.id)
            # add the combined statistics of the campaign to the output list
            campaigns_statistics_as_rows.append(campaign_statistics)
        return campaigns_statistics_as_rows

    def get_global_statistics_csv_rows(self) -> list[dict[str, object]]:
        cpm_per_day = self._calculate_cpm_per_day()
        num_over_budget_campaigns_per_day = self._calculate_num_over_budget_campaigns_per_day()
        total_wins_per_day = self._calculate_total_wins_per_day()
        overspend_amount_per_day = self._calculate_total_overspend_per_day()
        spend_amount_per_day = self._calculate_total_spend_per_day()
        total_minutes_alive_per_day = self._calculate_total_minutes_alive_per_day()
        pacing_statistics = self.pacing_system.get_global_pacing_statistics() if self.pacing_system else None
        day_statistics_rows = []
        for day in range(Clock.days()):
            # Add row for day
            day_row = {
                constants.FIELD_DAY_ID: day,
                constants.FIELD_CPM: cpm_per_day[day],
                constants.FIELD_SPEND: spend_amount_per_day[day],
                constants.FIELD_OVERSPEND: overspend_amount_per_day[day],
                constants.FIELD_NUM_WINS: total_wins_per_day[day],
                constants.FIELD_NUM_OVER_BUDGET_CAMPAIGNS: num_over_budget_campaigns_per_day[day],
                constants.FIELD_MINUTES_ALIVE: total_minutes_alive_per_day[day]
            }
            if pacing_statistics:
                for field in pacing_statistics:
                    # If field is a list (per-day statistic), add the relevant entry to the day's row
                    if isinstance(pacing_statistics[field], list):
                        day_row[field] = pacing_statistics[field][day]
            day_statistics_rows.append(day_row)
        # Add a row with overall statistics
        day_statistics_rows.append({
            constants.FIELD_DAY_ID: constants.OVERALL_STATISTICS_ROW_NAME,
            constants.FIELD_CPM: self._calculate_overall_cpm(),
            constants.FIELD_SPEND: sum(spend_amount_per_day),
            constants.FIELD_OVERSPEND: sum(overspend_amount_per_day),
            constants.FIELD_NUM_WINS: sum(total_wins_per_day),
            constants.FIELD_MINUTES_ALIVE: sum(total_minutes_alive_per_day)
        })
        return day_statistics_rows

    def _calculate_overall_cpm(self) -> float:
        return 1000 * sum(self._calculate_total_spend_per_day()) / sum(self._calculate_total_wins_per_day())

    def _calculate_total_minutes_alive_per_day(self) -> list[int]:
        total_minutes_alive_per_day = [0] * Clock.days()
        for campaign in self._all_campaigns():
            campaign_minutes_alive_history = campaign.minutes_alive_history()
            for day in range(len(campaign_minutes_alive_history)):
                adjusted_day_index = campaign.stats.day_started + day
                total_minutes_alive_per_day[adjusted_day_index] += campaign_minutes_alive_history[day]
        return total_minutes_alive_per_day

    def _calculate_cpm_per_day(self) -> list[float]:
        spend_per_day = self._calculate_total_spend_per_day()
        wins_per_day = self._calculate_total_wins_per_day()
        return [1000 * spend_per_day[day] / wins_per_day[day] if wins_per_day[day] > 0 else None
                for day in range(len(spend_per_day))]

    def _calculate_total_spend_per_day(self) -> list[float]:
        total_spend_per_day = [0] * Clock.days()
        for campaign in self._all_campaigns():
            campaign_spend_history = campaign.spend_history()
            for day in range(len(campaign.overspend_value_daily_history())):
                adjusted_day_index = campaign.stats.day_started + day
                total_spend_per_day[adjusted_day_index] += sum(campaign_spend_history[day])
        return total_spend_per_day

    def _calculate_total_wins_per_day(self) -> list[int]:
        total_num_wins_per_day = [0] * Clock.days()
        for campaign in self._all_campaigns():
            campaign_num_wins_history = campaign.num_auctions_won_history()
            for day in range(len(campaign.overspend_value_daily_history())):
                adjusted_day_index = campaign.stats.day_started + day
                total_num_wins_per_day[adjusted_day_index] += sum(campaign_num_wins_history[day])
        return total_num_wins_per_day

    def _calculate_num_over_budget_campaigns_per_day(self) -> list[int]:
        num_over_budget_campaigns_per_day = [0] * Clock.days()
        for campaign in self._all_campaigns():
            campaign_overspend_history = campaign.overspend_value_daily_history()
            for day in range(len(campaign.overspend_value_daily_history())):
                adjusted_day_index = campaign.stats.day_started + day
                if campaign_overspend_history[day] > 0:
                    num_over_budget_campaigns_per_day[adjusted_day_index] += 1
        return num_over_budget_campaigns_per_day

    def _calculate_total_overspend_per_day(self) -> list[float]:
        total_overspend_per_day = [0] * Clock.days()
        for campaign in self._all_campaigns():
            campaign_overspend_history = campaign.overspend_value_daily_history()
            for day in range(len(campaign.overspend_value_daily_history())):
                adjusted_day_index = campaign.stats.day_started + day
                total_overspend_per_day[adjusted_day_index] += campaign_overspend_history[day]
        return total_overspend_per_day

    @staticmethod
    def _calculate_number_of_untracked_bids(num_relevant_campaigns: int) -> int:
        return round(config.factor_untracked_bids * num_relevant_campaigns)

    def _all_campaigns(self) -> list[Campaign]:
        return list(self.tracked_campaigns.values()) + list(self.old_campaigns.values())
