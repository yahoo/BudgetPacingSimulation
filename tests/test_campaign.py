import unittest

from src.system.campaign import *


class TestCampaigns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()
        config.num_spend_entries_per_day = 1
        config.num_win_entries_per_day = config.n_iterations_per_day

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
        payment = 1
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        n_iterations_per_spend_entry = config.n_iterations_per_day // config.num_spend_entries_per_day
        n_iterations_per_win_entry = config.n_iterations_per_day // config.num_win_entries_per_day
        # simulate an auction in each clock iteration
        for i in range(config.n_iterations_per_day):
            campaign.pay(amount=payment)
            self.assertEqual(campaign.stats.today_spend[CampaignStatistics._calculate_spend_index_in_day()],
                             (i+1) * payment if i % n_iterations_per_spend_entry != 0 else 1)
            self.assertEqual(campaign.stats.auctions_won_today[CampaignStatistics._calculate_win_index_in_day()],
                             (i+1) if i % n_iterations_per_win_entry != 0 else 1)
            Clock.advance()
        self.assertEqual(campaign.spent_today(), config.n_iterations_per_day * payment)

    def test_campaign_stats_history(self):
        Clock.reset()
        n_auctions_won = 10
        payment = 5
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        self.assertEqual(len(campaign.stats.spend_history), 0)
        self.assertEqual(len(campaign.stats.auctions_won_history), 0)
        for _ in range(n_auctions_won):
            campaign.pay(amount=payment)
        # simulating day passed
        for _ in range(config.n_iterations_per_day):
            Clock.advance()
        campaign.setup_new_day()
        self.assertEqual(len(campaign.stats.spend_history), 1)
        self.assertEqual(len(campaign.stats.auctions_won_history), 1)
        # checking history
        self.assertEqual(campaign.stats.spend_history[0][0], n_auctions_won * payment)
        self.assertEqual(campaign.stats.auctions_won_history[0][0], n_auctions_won)


if __name__ == '__main__':
    unittest.main()
