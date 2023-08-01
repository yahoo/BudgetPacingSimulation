import unittest
from src.system.campaign import *
from src.system.serving_system import ServingSystem
from src.system.auction import AuctionWinner


class TestServingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()

    def test_add_campaign(self):
        serving_system = ServingSystem(tracked_campaigns=[], n_fake_bids=2)
        campaign = Campaign(campaign_id=f'campaign', total_budget=1000, run_period=7, max_bid=25)
        serving_system.add_campaign(campaign)
        self.assertTrue(campaign in serving_system.tracked_campaigns.values(),
                        "expected added campaign to be inside tracked campaigns")
        self.assertRaises(Exception, serving_system.add_campaign, campaign,
                          "should have raised an exception preventing insertion of duplicate elements")

    def test_serving_system(self):
        n_campaigns = 5
        n_fake_bids = 3
        campaigns = []
        initial_budget = 1000
        for i in range(n_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=initial_budget, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(tracked_campaigns=campaigns, n_fake_bids=n_fake_bids)
        self.assertEqual(len(serving_system.get_bids()), n_campaigns + n_fake_bids, "wrong number of generated bids")
        # simulating a winning campaign and updating its budget
        campaign_id = campaigns[0].id
        auction_winner = AuctionWinner(bid=Bid(campaign_id, 10), payment=10)
        serving_system.update_winners([auction_winner])
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].stats.spend_history[0][0],
                         auction_winner.payment)


if __name__ == '__main__':
    unittest.main()
