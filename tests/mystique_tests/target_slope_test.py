import unittest

from src.budget_pacing.mystique.target_slope import LinearTargetSpendStrategy
import src.budget_pacing.mystique.mystique_constants as mystique_constants
import mystique_campaign_initialization


class TestLinearTargetSlope(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.mystique_tracked_campaign = mystique_campaign_initialization.instance_for_target_slope_test()
        self.target_slope_strategy = LinearTargetSpendStrategy()
        self.timestamp = 0
        self.required_slope_array = [1] * mystique_constants.num_hours_per_day
        self.required_spend_array = [(i+1)/mystique_constants.num_hours_per_day for i in range(mystique_constants.num_hours_per_day)]

    def test_initialization(self):
        self.target_slope_strategy.initialize_slope(self.mystique_tracked_campaign)
        calculated_slope_array = self.mystique_tracked_campaign.current_target_slope
        calculated_spend_array = self.mystique_tracked_campaign.current_target_spend_curve
        target_slope_history = self.mystique_tracked_campaign.target_slope_history
        target_spend_history = self.mystique_tracked_campaign.target_spend_history

        self.assertEqual(len(calculated_slope_array), len(self.required_slope_array), "incorrect length of target slope array")
        self.assertEqual(len(calculated_spend_array), len(self.required_spend_array), "incorrect length of spend curve array")
        self.assertEqual(len(calculated_slope_array), len(calculated_spend_array), "lengths of target slope and spend arrays do not match")
        for i in range(len(calculated_slope_array)):
            self.assertEqual(calculated_slope_array[i], self.required_slope_array[i], "incorrect value of target slope array")
            self.assertAlmostEqual(calculated_spend_array[i], self.required_spend_array[i], msg="incorrect value of target spend curve array")
        self.assertTrue(len(target_slope_history) == 0, "target slope history improperly initialized")
        self.assertTrue(len(target_spend_history) == 0, "target spend history improperly initialized")

    def test_update_slope(self):
        self.target_slope_strategy.update_slope(self.timestamp, self.mystique_tracked_campaign)
        calculated_slope_array = self.mystique_tracked_campaign.current_target_slope
        calculated_spend_array = self.mystique_tracked_campaign.current_target_spend_curve
        target_slope_history = self.mystique_tracked_campaign.target_slope_history
        target_spend_history = self.mystique_tracked_campaign.target_spend_history

        self.assertEqual(len(calculated_slope_array), len(self.required_slope_array), "incorrect length of target slope array")
        self.assertEqual(len(calculated_spend_array), len(self.required_spend_array), "incorrect length of spend curve array")
        self.assertEqual(len(calculated_slope_array), len(calculated_spend_array), "lengths of target slope and spend arrays do not match")
        for i in range(len(calculated_slope_array)):
            self.assertEqual(calculated_slope_array[i], self.required_slope_array[i], "incorrect value of target slope array")
            self.assertAlmostEqual(calculated_spend_array[i], self.required_spend_array[i], msg="incorrect value of target spend curve array")
        self.assertTrue(len(target_slope_history) == 1, "target slope history improperly initialized")
        self.assertTrue(len(target_spend_history) == 1, "target spend history improperly initialized")

    def test_get_target_slope_and_spend(self):
        self.timestamp = 0
        target_slope, target_spend = self.target_slope_strategy.get_target_slope_and_spend(self.timestamp, self.mystique_tracked_campaign)
        self.assertEqual(target_slope, 1, "incorrect target slope")
        self.assertEqual(target_spend, 0, "incorrect initial target spend")

        self.timestamp = 1
        target_slope, target_spend = self.target_slope_strategy.get_target_slope_and_spend(self.timestamp, self.mystique_tracked_campaign)
        self.assertEqual(target_slope, 1, "incorrect target slope")
        self.assertAlmostEqual(target_spend, 1/mystique_constants.num_iterations_per_day, msg="incorrect initial target spend")

        self.timestamp = 35
        target_slope, target_spend = self.target_slope_strategy.get_target_slope_and_spend(self.timestamp, self.mystique_tracked_campaign)
        self.assertEqual(target_slope, 1, "incorrect target slope")
        self.assertAlmostEqual(target_spend, self.timestamp / mystique_constants.num_iterations_per_day,
                               msg="incorrect initial target spend")

        self.timestamp = mystique_constants.num_iterations_per_day
        target_slope, target_spend = self.target_slope_strategy.get_target_slope_and_spend(self.timestamp, self.mystique_tracked_campaign)
        self.assertEqual(target_slope, 1, "incorrect target slope")
        self.assertEqual(target_spend, 0, "incorrect initial target spend")

    def get_target_spend_array(self):
        target_spend_arr = self.target_slope_strategy.get_target_spend_array(self.mystique_tracked_campaign.current_target_slope)
        i = 0
        self.assertEqual(target_spend_arr[i], 0, "incorrect target spend value")
        i = int(len(target_spend_arr) / 2)
        self.assertAlmostEqual(target_spend_arr[i], 0.5, msg="incorrect target spend value")
        i = len(target_spend_arr) - 1
        self.assertAlmostEqual(target_spend_arr[i], 1, msg="incorrect target spend value")


# run the test
if __name__ == '__main__':
    unittest.main()

