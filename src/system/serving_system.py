import random

import src.constants as constants
from src.system.campaign import Campaign
from src.system.auction import *
import src.configuration as config
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
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

    def add_campaign(self, campaign: Campaign):
        if campaign is None:
            raise Exception('cannot add a None campaign')
        if campaign.id in self.tracked_campaigns or campaign.id in self.old_campaigns:
            raise Exception('campaign id already exists')
        self.tracked_campaigns[campaign.id] = campaign
        if self.pacing_system is not None:
            self.pacing_system.add_campaign(campaign)

    def get_bids(self) -> list[Bid]:
        bids = []
        # get "real" bids
        for campaign in self.tracked_campaigns.values():
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
        if len(bids) > 0:
            # add untracked bids
            bids += self._generate_untracked_bids()
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

    def _end_of_day_campaign_updates(self):
        for campaign in list(self.tracked_campaigns.values()):
            campaign.prepare_for_new_day()
            assert campaign.days_left_to_run() >= 0
            if campaign.days_left_to_run() == 0:
                # add campaign to the structure of campaigns that are done
                self.old_campaigns[campaign.id] = campaign
                # remove campaign from the structure of active campaigns
                self.tracked_campaigns.pop(campaign.id)

    def _generate_untracked_bids(self) -> list[Bid]:
        return [Bid(campaign_id='untracked_campaign_' + str(i),
                    amount=random.uniform(config.campaign_minimal_bid, config.untracked_bid_max))
                for i in range(self._calculate_number_of_untracked_bids())]

    def get_statistics_for_all_campaigns(self) -> list[dict[str, object]]:
        campaigns_statistics_as_rows = []
        for campaign in self._all_campaigns():
            campaign_statistics = {
                constants.FIELD_CAMPAIGN_ID: campaign.id,
                constants.FIELD_DAY_STARTED: campaign.stats.day_started,
                constants.FIELD_DAY_ENDED: campaign.stats.day_ended,
                constants.FIELD_DAILY_BUDGET: campaign.daily_budget,
                constants.FIELD_NUM_AUCTIONS_WON_HISTORY: campaign.num_auctions_won_history()
            }
            if self.pacing_system is not None:
                # merge campaign's pacing statistics the basic statistics
                campaign_statistics |= self.pacing_system.get_pacing_statistics(campaign.id)
            # add the combined statistics of the campaign to the output list
            campaigns_statistics_as_rows.append(campaign_statistics)
        return campaigns_statistics_as_rows

    @staticmethod
    def _calculate_number_of_untracked_bids() -> int:
        # We will later sample from distribution according to Clock.minutes()
        return config.num_untracked_bids

    def _all_campaigns(self) -> list[Campaign]:
        return list(self.tracked_campaigns.values()) + list(self.old_campaigns.values())
