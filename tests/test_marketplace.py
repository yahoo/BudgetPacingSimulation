# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import unittest
from unittest import mock

from src.system.campaign import *
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem
from tests.tests_utils import create_campaigns

_mock_num_auctions_per_iteration = 10


class TestMarketPlace(unittest.TestCase):
    def setUp(self):
        Clock.reset()
        config.num_spend_entries_per_day = 24
        config.num_win_entries_per_day = 24 * 60
        config.factor_untracked_bids = 0
        num_campaigns = 10
        self.campaigns = create_campaigns(num_campaigns)
        serving_system = ServingSystem(tracked_campaigns=self.campaigns)
        self.marketplace = Marketplace(serving_system=serving_system)

    @mock.patch("src.system.marketplace.Marketplace._sample_current_num_of_auctions",
                lambda _: _mock_num_auctions_per_iteration)
    def test_marketplace(self):
        num_days = 3
        num_campaigns = 10
        num_auctions_per_iteration = 10
        campaigns = create_campaigns(num_campaigns)
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        # replacing the function that calculates the number of auctions for each minute
        Marketplace._sample_current_num_of_auctions = lambda _: num_auctions_per_iteration
        marketplace = Marketplace(serving_system=serving_system)
        for day in range(num_days):
            for i in range(config.num_iterations_per_day):
                self.marketplace.run_iteration()
            # check history of last day
            num_auctions_won_last_day = sum(
                [sum(c.stats.auctions_won_history[-1]) for c in self.campaigns]
            )
            self.assertEqual(num_auctions_won_last_day,
                             _mock_num_auctions_per_iteration * config.num_iterations_per_day,
                             "expected the total number of wins in a day to be equal to the number of auctions")

    def test_traffic_dist_mean_same_every_day(self):
        n_days = 7
        minutes_to_check = [0, config.num_iterations_per_day // 4, config.num_iterations_per_day // 2,
                            config.num_iterations_per_day - 1]
        calculated_mean_per_minute = {
            minute: [] for minute in minutes_to_check
        }
        for day in range(n_days):
            for minute in minutes_to_check:
                Clock._iterations = day * config.num_iterations_per_day + minute
                calculated_mean = self.marketplace._calculate_current_mean_num_of_auctions()
                if day > 0:
                    # Check that the calculated mean is equal to the mean calculated
                    # in the same minute of the previous day
                    self.assertEqual(calculated_mean, calculated_mean_per_minute[minute][-1])
                calculated_mean_per_minute[minute].append(calculated_mean)

    def test_traffic_dist_mean_single_cos_wave(self):
        calculated_mean_histogram = {}
        for _ in range(config.num_iterations_per_day):
            calculated_mean = self.marketplace._calculate_current_mean_num_of_auctions()
            if calculated_mean_histogram.get(calculated_mean) is None:
                calculated_mean_histogram[calculated_mean] = 1
            else:
                calculated_mean_histogram[calculated_mean] += 1
            Clock.advance()
        # check that each calculated value for the distribution mean appears at most twice in a given day
        for calculated_mean, num_appearances in calculated_mean_histogram.items():
            self.assertGreaterEqual(num_appearances, 1)
            self.assertLessEqual(num_appearances, 2)


if __name__ == '__main__':
    unittest.main()
