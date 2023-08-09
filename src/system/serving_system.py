import random

from src.system.campaign import Campaign
from src.system.auction import *
import src.configuration as config
from src.system.clock import Clock
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface


class ServingSystem:
    tracked_campaigns: dict[str, Campaign]
    old_campaigns: dict[str, Campaign]

    def __init__(self, pacing_system: PacingSystemInterface = None, tracked_campaigns: list[Campaign] = None):
        if tracked_campaigns is None:
            tracked_campaigns = []
        self.tracked_campaigns = {campaign.id: campaign for campaign in tracked_campaigns}
        self.old_campaigns = {}
        self.pacing_system = pacing_system
        self.pending_pacing_spend_updates = {}
        self.days_run = 0

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
            bid = campaign.bid()
            if bid is None:
                continue
            if self.pacing_system is not None:
                pacing_signal = self.pacing_system.get_pacing_signal(campaign_id=campaign.id)
                assert 0 <= pacing_signal <= 1
                bid.amount *= pacing_signal
            if bid.amount > 0:
                bids.append(bid)
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
                    if winner.bid.campaign_id in self.pending_pacing_spend_updates:
                        self.pending_pacing_spend_updates[winner.bid.campaign_id] += winner.payment
                    else:
                        self.pending_pacing_spend_updates[winner.bid.campaign_id] = winner.payment

    def end_iteration(self):
        # Budget Pacing periodic (every minute) spend updates
        self._update_pacing_system()
        # Daily campaign updates
        if Clock.days() > self.days_run:
            self._daily_campaign_updates()
            self.days_run += 1

    def _update_pacing_system(self):
        if self.pacing_system is None:
            return
        for campaign in self.tracked_campaigns.values():
            # get the spend amount of each campaign during the last minute, and send it to the budget pacing system
            spend = self.pending_pacing_spend_updates.pop(campaign.id, 0)
            self.pacing_system.start_iteration(campaign_id=campaign.id, spend_since_last_iteration=spend)

    def _daily_campaign_updates(self):
        for campaign in list(self.tracked_campaigns.values()):
            campaign.setup_new_day()
            if campaign.run_period == 0:
                # add campaign to the structure of campaigns that are done
                self.old_campaigns[campaign.id] = campaign
                # remove campaign from the structure of active campaigns
                self.tracked_campaigns.pop(campaign.id)

    def _generate_untracked_bids(self) -> list[Bid]:
        fake_bids = []
        for i in range(self._calculate_number_of_untracked_bids()):
            # We will later sample the value of the untracked bid from a distribution
            fake_bids.append(Bid(campaign_id='untracked_campaign_' + str(i),
                                 amount=random.uniform(config.campaign_minimal_bid, config.untracked_bid_max)))
        return fake_bids

    @staticmethod
    def _calculate_number_of_untracked_bids() -> int:
        # We will later sample from distribution according to Clock.minutes()
        return config.num_untracked_bids
