import unittest

from src.budget_pacing.mystique.target_slope import LinearTargetSpendStrategy
import src.budget_pacing.mystique.mystique_constants as mystique_constants
import mystique_tracked_campaign_initialization

class TestTargetSlope(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.mystique_tracked_campaign = mystique_tracked_campaign_initialization.instance_for_target_slope_test()
        self.target_slope_strategy = LinearTargetSpendStrategy()
        self.timestamp = 0

    def test_initialization(self):
        self.target_slope_strategy.initialize_slope(self.timestamp, self.mystique_tracked_campaign)
        required_slope_array = [1] * mystique_constants.num_hours_per_day
        required_spend_array = [(i+1)/mystique_constants.num_hours_per_day for i in range(mystique_constants.num_hours_per_day)]
        calculated_slope_array = self.mystique_tracked_campaign.current_target_slope
        calculated_spend_array = self.mystique_tracked_campaign.current_target_spend_curve

        self.assertEquals(len(calculated_slope_array), len(required_slope_array), "incorrect length of target slope array")
        self.assertEquals(len(calculated_spend_array), len(required_spend_array), "incorrect length of spend curve array")
        for i in range(len(calculated_slope_array)):
            self.assertEquals(calculated_slope_array[i], required_slope_array, "incorrect value of target slope array")
            self.assertAlmostEqual(calculated_spend_array[i], required_spend_array[i], "incorrect value of target spend curve array")


# run the test
unittest.main()


