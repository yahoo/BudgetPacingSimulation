import unittest
from src.system.campaign import *
from src.system.serving_system import ServingSystem
from src.system.auction import AuctionWinner


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

    def test_serving_system(self):
        n_campaigns = 5
        campaigns = []
        initial_budget = 1000
        for i in range(n_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=initial_budget, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        bids = serving_system.get_bids()
        self.assertEqual(len(bids), n_campaigns + config.n_untracked_bids, "wrong number of generated bids")
        for c in campaigns:
            # assert that each campaign has a bid in the list of bids
            self.assertTrue(c.id in [bid.campaign_id for bid in bids], "no bid exists for campaign")
        # simulating a winning campaign and updating its budget
        campaign_id = campaigns[0].id
        auction_winner = AuctionWinner(bid=Bid(campaign_id, 10), payment=10)
        serving_system.update_winners([auction_winner])
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].spent_today(), auction_winner.payment,
                         "today's spend of the winning campaign should reflect the auction won")
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].n_auctions_won_today(), 1,
                         "the number of auctions won today by the campaign should reflect the auction won")


if __name__ == '__main__':
    unittest.main()
