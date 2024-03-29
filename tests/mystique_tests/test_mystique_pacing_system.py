# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import unittest
import numpy as np

from src.system.clock import Clock
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem, MystiqueHardThrottlingPacingSystem
import mystique_campaign_initialization
import src.system.budget_pacing.mystique.mystique_constants as mystique_constants


class TestMystiquePacingSystem(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.mystique_linear = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
        Clock.reset()

    def testAddCampaign(self):
        campaign_id = "0"
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init(campaign_id)
        self.mystique_linear.add_campaign(campaign)

        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.daily_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.pacing_signal_for_initialization, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.pacing_signal_for_initialization, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.pacing_signal_for_initialization, "last positive pacing signal initialization not correct")
        self.assertTrue(len(mystique_tracked_campaign.current_target_slope) > 0, "current_target_slope not initialized")
        self.assertTrue(len(mystique_tracked_campaign.current_target_spend_curve) > 0, "current_target_spend_curve not initialized")

        campaign_id = "1"
        campaign = mystique_campaign_initialization.instance_for_budget_above_threshold(campaign_id)
        self.mystique_linear.add_campaign(campaign)

        campaign_id = campaign.id
        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.total_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.max_ps, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.max_ps, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.max_ps, "last positive pacing signal initialization not correct")

    def test_ps_calculation(self):
        campaign_id = "0"
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init(campaign_id)
        self.mystique_linear.add_campaign(campaign)
        Clock.advance()

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        target_spend_slope_calculator = self.mystique_linear.target_spend_slope_calculator
        target_slope, target_spend = target_spend_slope_calculator.get_target_slope_and_spend(mystique_tracked_campaign)
        actual_spend = 0.004

        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        Clock.advance()

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
        estimated_intervals_until_target_is_hit = MystiquePacingSystem.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        self.assertEqual(estimated_intervals_until_target_is_hit, -1 * mystique_constants.num_iterations_per_day * spend_error / gradient_error, "Estimated intervals until budget is hit calculation not correct")

        # test weights calculation
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
        _, next_target_spend = target_spend_slope_calculator.get_target_slope_and_spend(mystique_tracked_campaign)
        actual_spend = (next_target_spend - target_spend) * mystique_tracked_campaign.daily_budget     # simulating gradient_error == 0

        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        Clock.advance()

        spend_error = MystiquePacingSystem.get_spend_error(percent_budget_depleted_today, target_spend)
        spend_derivative_in_latest_time_interval = MystiquePacingSystem.get_spend_derivative_in_latest_time_interval(mystique_tracked_campaign)
        gradient_error = MystiquePacingSystem.get_gradient_error(spend_derivative_in_latest_time_interval, target_slope)
        estimated_intervals_until_target_is_hit = MystiquePacingSystem.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        self.assertEqual(estimated_intervals_until_target_is_hit, mystique_constants.max_interval, "Estimated intervals until budget is hit calculation not correct")

        # test for case estimated_intervals_until_target_is_hit > 0
        w1, w2 = MystiquePacingSystem.get_pacing_signal_correction_weights(estimated_intervals_until_target_is_hit)
        w1_to_compare = min(mystique_constants.max_ps_correction_weight,
                            mystique_constants.ps_correction_weight_factor * estimated_intervals_until_target_is_hit)
        self.assertEqual(w1, w1_to_compare, "w1 calculation not correct")
        self.assertEqual(w2, 1 - w1, "w2 calculation not correct")

        # testing the edge cases:

        # test for runaway train
        actual_spend = 7
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        Clock.advance()

        ps = self.mystique_linear.get_pacing_signal(campaign_id)
        self.assertEqual(ps, 0, "Pacing signal calculation in runaway train not correct")

        # test minimal ps value
        Clock.advance()
        actual_spend = 0.0001
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        ps = mystique_tracked_campaign.ps
        self.assertEqual(ps, mystique_constants.minimal_ps_value, "Pacing signal calculation not minimal")

        # test budget depletion
        Clock.advance()
        previous_ps = mystique_tracked_campaign.ps
        actual_spend = mystique_tracked_campaign.daily_budget - sum(mystique_tracked_campaign.today_spend)
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        current_ps = mystique_tracked_campaign.ps
        self.assertEqual(current_ps, previous_ps, "Pacing signal calculation in budget depletion not correct")

        # test end of day
        Clock.reset()
        campaign_id = "2"
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init(campaign_id)
        self.mystique_linear.add_campaign(campaign)
        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        actual_spend = 0.006
        iterations = mystique_constants.num_iterations_per_day - mystique_constants.minutes_for_end_day_edge_case
        for i in range(iterations):
            Clock.advance()
            self.mystique_linear.end_iteration(campaign_id, actual_spend)
        previous_ps = mystique_tracked_campaign.ps
        Clock.advance()
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        current_ps = mystique_tracked_campaign.ps
        avg_ps = mystique_tracked_campaign.get_avg_daily_ps()
        self.assertNotEqual(previous_ps, current_ps, "end of day price signal calculation not correct")
        self.assertEqual(avg_ps, current_ps, "end of day price signal calculation not correct")

    def test_new_day(self):
        campaign_id = "3"
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init(campaign_id)
        self.mystique_linear.add_campaign(campaign)
        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        actual_spend = 0.006

        # going through a whole day worth of iterations
        iterations = mystique_constants.num_iterations_per_day - 1
        for i in range(iterations):
            self.mystique_linear.end_iteration(campaign_id, actual_spend)
            Clock.advance()

        self.assertTrue(len(mystique_tracked_campaign.today_ps) > 0, "today's pacing signal values were not updated")
        self.assertTrue(len(mystique_tracked_campaign.today_spend) > 0, "today's spend values were not updated")
        self.assertTrue(len(mystique_tracked_campaign.ps_history) ==0, "pacing signal history not empty when it should be")
        self.assertTrue(len(mystique_tracked_campaign.spend_history) == 0, "spend history not empty when it should be")
        prev_day_avg_ps = mystique_tracked_campaign.get_avg_daily_ps_below_threshold()
        # end first day:
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        Clock.advance()
        # check that the first day ended well
        self.assertEqual(len(mystique_tracked_campaign.today_ps), 0, "new day's pacing signal values should be empty")
        self.assertEqual(len(mystique_tracked_campaign.today_spend), 0, "new day's spend values should be empty")
        self.assertTrue(len(mystique_tracked_campaign.ps_history) > 0, "pacing signal history not updated when it should be")
        self.assertTrue(len(mystique_tracked_campaign.spend_history) > 0, "spend history not updated when it should be")
        self.assertEqual(prev_day_avg_ps, mystique_tracked_campaign.previous_ps, "previous pacing signal on new day not correct")
        self.assertEqual(prev_day_avg_ps, mystique_tracked_campaign.last_positive_ps, "last positive pacing signal on new day not correct")
        # 1st iteration of second day
        self.mystique_linear.end_iteration(campaign_id, actual_spend)
        Clock.advance()
        self.assertEqual(len(mystique_tracked_campaign.today_ps), 1, "new day's pacing signal values should be empty")
        self.assertEqual(len(mystique_tracked_campaign.today_spend), 1, "new day's spend values should be empty")
        self.assertTrue(len(mystique_tracked_campaign.ps_history) > 0, "pacing signal history not updated when it should be")
        self.assertTrue(len(mystique_tracked_campaign.spend_history) > 0, "spend history not updated when it should be")
        self.assertEqual(prev_day_avg_ps, mystique_tracked_campaign.previous_ps, "previous pacing signal on new day not correct")
        self.assertEqual(prev_day_avg_ps, mystique_tracked_campaign.last_positive_ps, "last positive pacing signal on new day not correct")


class TestMystiqueHardThrottlingPacingSystem(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.mystique_hard_throttling = MystiqueHardThrottlingPacingSystem(TargetSpendStrategyType.LINEAR)
        Clock.reset()

    def test_pacing_signal_is_zero_or_one(self):
        campaign_id = "0"
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init(campaign_id)
        self.mystique_hard_throttling.add_campaign(campaign)
        self.assertTrue(campaign_id in self.mystique_hard_throttling.mystique_tracked_campaigns.keys(),
                        "Campaign not added to Mystique's tracked campaigns")
        actual_spend = 0.005

        # going through an hour's worth of iterations
        for i in range(mystique_constants.num_iterations_per_hour):
            ps = self.mystique_hard_throttling.get_pacing_signal(campaign_id=campaign_id)
            self.assertTrue(ps in [0, 1], "Hard throttling pacing system "
                                          "should return a value of ps that is either 0 or 1.")
            self.mystique_hard_throttling.end_iteration(campaign_id, actual_spend)
            Clock.advance()
