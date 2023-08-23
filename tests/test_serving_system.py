import unittest

from src.constants import num_minutes_in_day
from src.system.auction import AuctionWinner
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.campaign import *
from src.system.serving_system import ServingSystem


class TestServingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()

    def test_add_campaign(self):
        serving_system = ServingSystem(tracked_campaigns=[])
        campaign = Campaign(campaign_id=f'campaign', total_budget=1000, run_period=7, max_bid=25)
        serving_system.add_campaign(campaign)
        self.assertTrue(campaign in serving_system.tracked_campaigns.values(),
                        "expected added campaign to be inside tracked campaigns")
        self.assertRaises(Exception, serving_system.add_campaign, campaign,
                          "should have raised an exception preventing insertion of duplicate elements")

    def test_simple_auction(self):
        num_campaigns = 5
        campaigns = []
        initial_budget = 1000
        for i in range(num_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=initial_budget, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        bids = serving_system.get_bids()
        self.assertEqual(len(bids), num_campaigns + config.num_untracked_bids, "wrong number of generated bids")
        for c in campaigns:
            # assert that each campaign has a bid in the list of bids
            self.assertTrue(c.id in [bid.campaign_id for bid in bids], "no bid exists for campaign")
        # simulating a winning campaign and updating its budget
        campaign_id = campaigns[0].id
        auction_winner = AuctionWinner(bid=Bid(campaign_id, 10), payment=10)
        serving_system.update_winners([auction_winner])
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].spent_today(), auction_winner.payment,
                         "today's spend of the winning campaign should reflect the auction won")
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].num_auctions_won_today(), 1,
                         "the number of auctions won today by the campaign should reflect the auction won")

    def test_with_mock_budget_pacing_always_zero_ps(self):
        config.num_untracked_bids = 0
        num_campaigns = 5
        campaigns = []
        for i in range(num_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=1000, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(pacing_system=MockPacingSystem(pacing_signal=0),
                                       tracked_campaigns=campaigns)
        bids = serving_system.get_bids()
        self.assertEqual(len(bids), 0, "expected list of bids to be empty when all bids are zero")

    def test_campaign_budget_depletion(self):
        # Creating a single campaign, depleting its budget,
        # and checking that the serving system no longer gets bids from it.
        config.num_untracked_bids = 0
        campaign_daily_budget = config.campaign_minimal_bid
        campaign_run_period = 2
        campaign = Campaign(campaign_id='campaign', total_budget=campaign_daily_budget * campaign_run_period,
                            run_period=campaign_run_period, max_bid=campaign_daily_budget+0.1)
        serving_system = ServingSystem(tracked_campaigns=[campaign])
        bids = serving_system.get_bids()
        self.assertEqual(len(bids), 1, "expected to get a bid from a single campaign")
        # simulating a win for the campaign which depletes its budget
        auction_winner = AuctionWinner(bid=Bid(campaign.id, campaign.max_bid), payment=campaign.max_bid)
        serving_system.update_winners([auction_winner])
        self.assertGreater(campaign.spent_today(), campaign.daily_budget)
        bids_after_depletion = serving_system.get_bids()
        self.assertEqual(bids_after_depletion, [], "expected list of bids to be empty after depleting campaign's budget")

    def test_with_mystique_budget_pacing(self):
        config.num_untracked_bids = 0
        campaign = Campaign(campaign_id='campaign1', total_budget=1000, run_period=7, max_bid=25)
        mystique = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
        serving_system = ServingSystem(pacing_system=mystique,
                                       tracked_campaigns=[campaign])
        # check that campaigns were added to Mystique
        self.assertTrue(campaign.id in mystique.mystique_tracked_campaigns,
                        "campaign was not added to pacing system")
        bids = serving_system.get_bids()
        self.assertEqual(len(bids), 1)
        bid = bids[0]
        self.assertGreater(bid.amount, 0)
        payment = bid.amount
        serving_system.update_winners([AuctionWinner(bid=bid, payment=payment)])
        serving_system.end_iteration()
        # check that the campaign itself was updated
        self.assertEqual(campaign.spent_today(), payment, "expected campaign spend to be equal to payment")
        # check that the tracked campaign in mystique was updated with the spend of the campaign
        mystique_tracked_campaign = mystique.mystique_tracked_campaigns.get(campaign.id)
        self.assertEqual(len(mystique_tracked_campaign.today_spend), 1,
                         "expected mystique tracked campaign to contain a single entry in its daily spend list")
        # simulate days passed
        for _ in range(num_minutes_in_day*2):
            Clock.advance()
            serving_system.end_iteration()
        self.assertEqual(mystique_tracked_campaign.spend_history[0][0], payment,
                         "expected mystique tracked campaign to contain an entry equal to the amount it payed "
                         "during the last iteration in its daily spend list")
        # check that the CampaignStatistics history were updated
        self.assertEqual(campaign.stats.spend_history[0][0], payment, "expected campaign spend history to include payment")


class MockPacingSystem(PacingSystemInterface):
    def __init__(self, pacing_signal=0):
        self.pacing_signal = pacing_signal

    def add_campaign(self, campaign):
        pass

    def end_iteration(self, campaign_id, spend_since_last_iteration):
        pass

    def get_pacing_signal(self, campaign_id):
        return self.pacing_signal

    def new_day_init(self):
        pass


if __name__ == '__main__':
    unittest.main()
