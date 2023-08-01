import random

from src.system.campaign import Campaign
from src.system.auction import *
import src.configuration as config


class ServingSystem:
    tracked_campaigns: dict[str, Campaign]
    old_campaigns: dict[str, Campaign]

    def __init__(self, tracked_campaigns: list[Campaign] = None, n_fake_bids=0, fake_bid_max=10):
        if tracked_campaigns is None:
            tracked_campaigns = []
        self.tracked_campaigns = {campaign.id: campaign for campaign in tracked_campaigns}
        self.old_campaigns = {}
        self.n_fake_bids = n_fake_bids
        if fake_bid_max <= config.campaign_minimal_bid:
            raise Exception('invalid fake_bid_max parameter.')
        self.fake_bid_max = fake_bid_max

    def add_campaign(self, campaign: Campaign):
        if campaign is None:
            raise Exception('cannot add a None campaign')
        if campaign.id in self.tracked_campaigns or campaign.id in self.old_campaigns:
            raise Exception('campaign id already exists')
        self.tracked_campaigns[campaign.id] = campaign

    def _generate_fictitious_bids(self) -> list[Bid]:
        fake_bids = []
        for i in range(self.n_fake_bids):
            fake_bids.append(Bid(campaign_id='untracked_campaign_' + str(i),
                                 amount=random.uniform(config.campaign_minimal_bid, self.fake_bid_max)))
        return fake_bids

    def get_bids(self) -> list[Bid]:
        bids = []
        # get "real" bids
        for campaign in self.tracked_campaigns.values():
            bid = campaign.bid()
            if bid is not None:
                bids.append(bid)
        # add "fake" bids
        bids += self._generate_fictitious_bids()
        return bids

    def update_winners(self, winners: list[AuctionWinner]):
        for winner in winners:
            if winner.bid.campaign_id in self.tracked_campaigns:
                self.tracked_campaigns[winner.bid.campaign_id].pay(winner.payment)

    def new_day_updates(self):
        for campaign in list(self.tracked_campaigns.values()):
            campaign.setup_new_day()
            if campaign.run_period == 0:
                # add campaign to the structure of campaigns that are done
                self.old_campaigns[campaign.id] = campaign
                # remove campaign from the structure of active campaigns
                self.tracked_campaigns.pop(campaign.id)
