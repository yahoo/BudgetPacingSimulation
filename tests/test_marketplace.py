import unittest

from src.system.campaign import *
from src.system.serving_system import ServingSystem
from src.system.marketplace import Marketplace
from src import configuration as config


class TestMarketPlace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Clock.reset()
        config.n_auctions_per_iteration = 10
        config.n_iterations_per_hist_interval = 60
        config.n_untracked_bids = 0

    def test_marketplace(self):
        n_days = 3
        n_campaigns = 10
        campaigns = []
        for i in range(n_campaigns):
            campaigns.append(
                Campaign(campaign_id=f'campaign_{i}', total_budget=1000, run_period=7, max_bid=25)
            )
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        marketplace = Marketplace(serving_system=serving_system)
        for day in range(n_days):
            for i in range(config.n_iterations_per_day):
                marketplace.run_iteration()
                if Clock.minutes() == 0:
                    serving_system.new_day_updates()
            # count the total number of auctions wins by iterating over all campaigns
            # and inspecting the win history of the last day
            n_auctions_won_total = sum(
                [sum(c.stats.auctions_won_history[-1]) for c in campaigns]
            )
            self.assertEqual(n_auctions_won_total,
                             config.n_auctions_per_iteration * config.n_iterations_per_day,
                             "expected the total number of wins in an iteration to be equal to the number of auctions")


if __name__ == '__main__':
    unittest.main()
