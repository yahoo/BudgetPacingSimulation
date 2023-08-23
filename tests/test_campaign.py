import unittest

from src.system.campaign import *


class TestCampaigns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()
        config.num_spend_entries_per_day = 24
        config.num_win_entries_per_day = config.num_iterations_per_day

    def test_simple_auction(self):
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        # simulating a simple "auction"
        bid = campaign.bid()
        self.assertIsNotNone(bid)
        self.assertIsInstance(bid.amount, float)
        campaign.pay(amount=bid.amount)
        self.assertEqual(campaign.num_auctions_won_today(), 1, "expected win counter to be 1")
        self.assertEqual(campaign.spent_today(), bid.amount, "expected spend history to show payment")

    def test_invalid_max_bid(self):
        self.assertRaises(Exception, Campaign, campaign_id='fail', total_budget=1000, run_period=1,
                          max_bid=config.campaign_minimal_bid - 0.0001)

    def test_campaign_stats_during_day(self):
        payment = 1
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        CampaignStatistics.num_iterations_per_spend_entry = config.num_iterations_per_day // config.num_spend_entries_per_day
        CampaignStatistics.num_iterations_per_win_entry = config.num_iterations_per_day // config.num_win_entries_per_day
        # simulate an auction in each clock iteration
        for i in range(config.num_iterations_per_day):
            # expected number of payments / wins in the currently active stats entry in the campaign:
            expected_previous_payments = (i % CampaignStatistics.num_iterations_per_spend_entry) * payment
            expected_previous_wins = i % CampaignStatistics.num_iterations_per_win_entry
            # simulating a win
            campaign.pay(amount=payment)
            self.assertEqual(campaign.stats.today_spend[CampaignStatistics._calculate_spend_index_in_day()],
                             expected_previous_payments + payment)
            self.assertEqual(campaign.stats.auctions_won_today[CampaignStatistics._calculate_win_index_in_day()],
                             expected_previous_wins + 1)
            Clock.advance()
        self.assertEqual(campaign.spent_today(), config.num_iterations_per_day * payment)

    def test_campaign_stats_history(self):
        Clock.reset()
        num_auctions_won = 10
        payment = 5
        campaign = Campaign(campaign_id='campaign_test', total_budget=1000, run_period=7, max_bid=25)
        self.assertEqual(len(campaign.stats.spend_history), 0)
        self.assertEqual(len(campaign.stats.auctions_won_history), 0)
        for _ in range(num_auctions_won):
            campaign.pay(amount=payment)
        # simulating day passed
        for _ in range(config.num_iterations_per_day):
            Clock.advance()
        campaign.prepare_for_new_day()
        self.assertEqual(len(campaign.stats.spend_history), 1)
        self.assertEqual(len(campaign.stats.auctions_won_history), 1)
        # checking history
        self.assertEqual(campaign.stats.spend_history[0][0], num_auctions_won * payment)
        self.assertEqual(campaign.stats.auctions_won_history[0][0], num_auctions_won)


if __name__ == '__main__':
    unittest.main()
