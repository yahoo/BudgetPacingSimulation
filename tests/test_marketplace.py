import unittest

from src.system.campaign import *
from src.system.serving_system import ServingSystem
from src.system.marketplace import Marketplace
from src import configuration as config


class TestMarketPlace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()
        config.num_spend_entries_per_day = 24
        config.num_win_entries_per_day = 24 * 60
        config.num_untracked_bids = 0

    def test_marketplace(self):
        num_days = 3
        num_campaigns = 10
        num_auctions_per_iteration = 10
        campaigns = []
        for i in range(num_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=1000000, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        # replacing the function that calculates the number of auctions for each minute
        Marketplace._sample_current_num_of_auctions = lambda _: num_auctions_per_iteration
        marketplace = Marketplace(serving_system=serving_system)
        for day in range(num_days):
            for i in range(config.num_iterations_per_day):
                marketplace.run_iteration()
            # check history of last day
            num_auctions_won_last_day = sum(
                [sum(c.stats.auctions_won_history[-1]) for c in campaigns]
            )
            self.assertEqual(num_auctions_won_last_day,
                             num_auctions_per_iteration * config.num_iterations_per_day,
                             "expected the total number of wins in a day to be equal to the number of auctions")


if __name__ == '__main__':
    unittest.main()
