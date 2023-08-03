import unittest

from src.system.campaign import *


class TestCampaigns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()
        config.n_iterations_per_hist_interval = 60

    def test_campaign(self):
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        # simulating a simple "auction"
        bid = campaign.bid()
        self.assertLessEqual(bid.amount, campaign.max_bid, "expected bid to be bounded by max_bid")
        self.assertLessEqual(config.campaign_minimal_bid, bid.amount, "expected bid to be lower-bounded by "
                                                                      "the minimal allowed bid")
        campaign.pay(amount=bid.amount)
        self.assertEqual(campaign.n_auctions_won_today(), 1, "expected win counter to be 1")
        self.assertEqual(campaign.spent_today(), bid.amount, "expected spend history to show payment")

    def test_invalid_max_bid(self):
        self.assertRaises(Exception, Campaign, campaign_id='fail', total_budget=1000, run_period=1,
                          max_bid=config.campaign_minimal_bid - 0.0001)

    def test_campaign_spent_today(self):
        n_auctions_won = 10
        payment = 8
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        for _ in range(n_auctions_won):
            campaign.pay(amount=payment)
        self.assertEqual(campaign.spent_today(), n_auctions_won * payment)
        # advance clock to next history interval
        for _ in range(config.n_iterations_per_hist_interval):
            Clock.advance()
        for _ in range(n_auctions_won):
            campaign.pay(amount=payment)
        self.assertEqual(campaign.spent_today(), 2 * n_auctions_won * payment)

    def test_campaign_stats_history(self):
        n_auctions_won = 10
        payment = 5
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        for _ in range(n_auctions_won):
            campaign.pay(amount=payment)
        # simulating day passed
        for _ in range(config.n_iterations_per_day):
            Clock.advance()
        campaign.setup_new_day()
        # checking history
        history_interval = Clock.minutes() // config.n_iterations_per_hist_interval
        self.assertEqual(campaign.stats.spend_history[Clock.days()][history_interval], n_auctions_won * payment)
        self.assertEqual(campaign.stats.auctions_won_history[Clock.days()][history_interval], n_auctions_won)


if __name__ == '__main__':
    unittest.main()
