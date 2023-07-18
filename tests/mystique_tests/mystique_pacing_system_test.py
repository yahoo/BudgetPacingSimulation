import unittest
import numpy as np

from src.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
import mystique_campaign_initialization
import src.budget_pacing.mystique.mystique_constants as mystique_constants


class TestMystiquePacingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.mystique_linear = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)

    def testAddCampaign(self):
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init()
        self.mystique_linear.add_campaign(campaign)

        campaign_id = campaign.campaign_id
        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.daily_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.pacing_signal_for_initialization, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.pacing_signal_for_initialization, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.pacing_signal_for_initialization, "last positive pacing signal initialization not correct")

        campaign = mystique_campaign_initialization.instance_for_budget_above_threshold()
        self.mystique_linear.add_campaign(campaign)

        campaign_id = campaign.campaign_id
        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.total_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.max_ps, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.max_ps, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.max_ps, "last positive pacing signal initialization not correct")

    def test_start_iteration(self):
        campaign_id = 0
        timestamp = 1
        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        target_spend_slope_calculator = self.mystique_linear.target_spend_slope_calculator
        target_slope, target_spend = target_spend_slope_calculator.get_target_slope_and_spend(timestamp,mystique_tracked_campaign)

        actual_spend = 0.004
        self.mystique_linear.start_iteration(timestamp, campaign_id, actual_spend)
        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]

        # test campaign spend
        campaign_sepnd = sum(mystique_tracked_campaign.today_spend)
        self.assertEqual(campaign_sepnd, actual_spend, "Campaign spend not updated correctly")

        # test percent budget depleted
        percent_budget_depleted_today = MystiquePacingSystem.get_percent_budget_depleted_today(mystique_tracked_campaign)
        self.assertEqual(percent_budget_depleted_today, actual_spend / mystique_tracked_campaign.daily_budget, "Percent budget depleted calculation not correct")

        # test spend error
        spend_error = MystiquePacingSystem.get_spend_error(percent_budget_depleted_today, target_spend)
        self.assertEqual(spend_error, percent_budget_depleted_today - target_spend, "Spend error calculation not correct")

        # test gradient error
        spend_derivative_in_latest_time_interval = MystiquePacingSystem.get_spend_derivative_in_latest_time_interval(mystique_tracked_campaign)
        self.assertEqual(spend_derivative_in_latest_time_interval, percent_budget_depleted_today / mystique_constants.percent_of_day_in_one_iteration, "Spend derivative calculation not correct")
        gradient_error = MystiquePacingSystem.get_gradient_error(spend_derivative_in_latest_time_interval, target_slope)
        self.assertEqual(gradient_error, spend_derivative_in_latest_time_interval - target_slope)

        # test intervals until budget is hit
        # TODO : add test for case gradient_error == 0
        estimated_intervals_until_target_is_hit = MystiquePacingSystem.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        self.assertEqual(estimated_intervals_until_target_is_hit, -1 * mystique_constants.num_iterations_per_day * spend_error / gradient_error, "Estimated intervals until budget is hit calculation not correct")

        # test weights calculation
        # TODO : test case of estimated_intervals_until_target_is_hit > 0
        w1, w2 = MystiquePacingSystem.get_pacing_signal_correction_weights(estimated_intervals_until_target_is_hit)
        self.assertEqual(w1, 0.5, "w1 calculation not correct")
        self.assertEqual(w2, 1 - w1, "w2 calculation not correct")

        # test pacing signal calculation
        previous_ps = mystique_tracked_campaign.last_positive_ps
        spend_error_intensity = abs(spend_error)
        spend_error_correction = mystique_constants.max_ps_correction * min(1, spend_error_intensity / mystique_constants.error_corresponding_to_max_correction)
        spend_error_sign = np.sign(spend_error)
        gradient_error_intensity = min(1, abs(gradient_error))
        gradient_error_correction = max(mystique_constants.minimal_non_zero_ps_correction, mystique_constants.max_ps_correction * gradient_error_intensity / mystique_constants.gradient_error_corresponding_to_max_correction)
        gradient_error_sign = np.sign(gradient_error)
        calculated_ps = previous_ps - (w1 * spend_error_correction * spend_error_sign) - (w2 * gradient_error_correction * gradient_error_sign)
        ps = self.mystique_linear.mystique_tracked_campaigns[campaign_id].ps
        self.assertEqual(ps, calculated_ps, "Pacing signal calculation not correct")

        # test for case gradient_error == 0
        timestamp += 1
        next_target_slope, next_target_spend = target_spend_slope_calculator.get_target_slope_and_spend(timestamp,mystique_tracked_campaign)
        actual_spend = next_target_spend - target_spend     # simulating gradient_error == 0
        self.mystique_linear.start_iteration(timestamp, campaign_id, actual_spend)
        spend_error = MystiquePacingSystem.get_spend_error(percent_budget_depleted_today, target_spend)
        # TODO : spend_derivative_in_latest_time_interval is 10% smaller than what it should be. Somewhere the calculation is wrong
        spend_derivative_in_latest_time_interval = MystiquePacingSystem.get_spend_derivative_in_latest_time_interval(mystique_tracked_campaign)
        gradient_error = MystiquePacingSystem.get_gradient_error(spend_derivative_in_latest_time_interval, target_slope)
        estimated_intervals_until_target_is_hit = MystiquePacingSystem.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        self.assertEqual(estimated_intervals_until_target_is_hit, mystique_constants.max_interval, "Estimated intervals until budget is hit calculation not correct")





