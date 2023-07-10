import numpy as np

from src.budget_pacing.pacing_system_interface import PacingSystemInterface
import target_slope
from target_slope import TargetSpendSlopeType
import src.utils as utils

default_unknown_value = -1
default_ps_value = 0
percent_of_day_in_one_iteration = 1 / 1440
num_iterations_per_day = 1440
num_iterations_per_hour = 60
previous_pacing_signal_for_initialization = 0.0001
max_ps = 1
error_corresponding_to_max_correction = 0.25
max_ps_correction = 0.025
gradient_error_corresponding_to_max_correction = 1.5
max_ps_correction = 0.025
minimal_non_zero_ps_correction = 0.01
min_daily_budget_for_high_initialization = 10000
max_interval = num_iterations_per_day + 1
max_ps_correction_weight = 0.9
ps_correction_weight_factor = 0.2


class MystiqueTrackedCampaigns:
    def __init__(self, daily_budget):
        self.daily_budget = daily_budget
        self.ps = default_ps_value     # to be updated in update_pacing_signal
        self.previous_ps = default_ps_value  # updated again in new_day_init
        self.last_positive_ps = default_ps_value  # updated again in new_day_init
        self.ps_history = np.array([(0, self.previous_ps)]) # each entry is a timestamp and the ps calculated for this iteration
        self.spend = np.array([(0, 0)])   # each entry is a timestamp and the spend reported from the previous iteration
        self.current_target_slope = np.array([])
        self.target_slope_history = np.array([])
        self.current_target_spend_curve = np.array([])
        self.target_spend_history = np.array([])
        self.new_day_init(daily_budget)

    def new_day_init(self, daily_budget):
        if daily_budget < min_daily_budget_for_high_initialization:
            self.previous_ps = previous_pacing_signal_for_initialization
        else:
            self.previous_ps = max_ps
        self.last_positive_ps = self.previous_ps

    def update_pacing_signal(self, timestamp, ps):
        self.ps = ps
        self.ps_history.append((timestamp, ps))

    def update_spend(self, timestamp, spend):
        self.spend.append((timestamp, spend))

    def update_target_slope_curve(self, timestamp, target_slope_curve):
        self.target_slope_history.append((timestamp, target_slope_curve))
        self.current_target_slope = target_slope_curve

    def update_target_spend_curve(self, timestamp, target_spend_curve):
        self.target_spend_history.append((timestamp, target_spend_curve))
        self.current_target_spend_curve = target_spend_curve

    def get_spend_in_last_time_interval(self):
        return self.spend[-1][1]

    def get_today_spend(self):
        return utils.get_arr_sum_of_last_tuple_item_from_modulo_location(self.spend, num_iterations_per_day)

    def conclude_iteration(self):
        self.previous_ps = self.ps
        if self.previous_ps > 0:
            self.last_positive_ps = self.previous_ps


class MystiqueImpl(PacingSystemInterface):
    def __init__(self, target_slope_type):
        self.campaigns = {}     # a dict containing campaign id as key and MystiqueTrackedCampaigns instance as val
        if target_slope_type == TargetSpendSlopeType.LINEAR:
            self.target_spend_slope_calculator = target_slope.LinearTargetSpendSlope()
        elif target_slope_type == TargetSpendSlopeType.NON_LINEAR:
            self.target_spend_slope_calculator = target_slope.NonLinearTargetSpendSlope()

    def add_campaign(self, campaign):
        campaign_id = campaign.id
        daily_budget = campaign.daily_budget
        if campaign_id not in self.campaigns.keys():
            self.campaigns[campaign_id] = MystiqueTrackedCampaigns(daily_budget)

    def conclude_iteration(self, timestamp, campaign_id, spend_since_last_iteration):
        if campaign_id in self.campaigns.keys():
            campaign = self.campaigns[campaign_id]
            campaign.update_spend(timestamp, spend_since_last_iteration)

            new_ps = self.calculate_new_pacing_signal(timestamp, campaign)
            self.update_pacing_signal(timestamp, campaign_id, new_ps)

            campaign.conclude_iteration()

    def update_pacing_signal(self, timestamp, campaign_id, pacing_signal):
        if campaign_id in self.campaigns.keys():
            self.campaigns[campaign_id].update_pacing_signal(timestamp, pacing_signal)

    def get_pacing_signal(self, campaign_id):
        if campaign_id in self.campaigns.keys():
            return self.campaigns[campaign_id].ps
        return default_ps_value

    def calculate_new_pacing_signal(self, timestamp, campaign):
        percent_budget_depleted_today = self.get_percent_budget_depleted_today(campaign)
        current_target_slope, current_target_spend = self.target_spend_slope_calculator.get_target_slope_and_spend(timestamp, campaign)
        spend_error = self.get_spend_error(percent_budget_depleted_today, current_target_spend)

        spend_derivative_in_last_time_interval = self.get_spend_derivative_in_last_time_interval(campaign)
        gradient_error = self.get_gradient_error(spend_derivative_in_last_time_interval, current_target_slope)

        estimated_intervals_until_target_is_hit = self.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        w1, w2 = self.get_pacing_signal_correction_weights(estimated_intervals_until_target_is_hit)
        previous_ps = campaign.last_positive_ps
        return self.get_new_pacing_signal(previous_ps, spend_error, gradient_error, w1, w2)


    @staticmethod
    def get_percent_budget_depleted_today(self, campaign):
        return campaign.get_today_spend() / campaign.daily_budget

    @staticmethod
    def get_spend_error(self, percent_budget_depleted_today, current_target_spend):
        return percent_budget_depleted_today - current_target_spend

    @staticmethod
    def get_spend_error_intensity(self, spend_error):
        return abs(spend_error)

    @staticmethod
    def get_spend_error_correction(self, error_intensity):
        return min(max_ps_correction, max_ps_correction * error_intensity / error_corresponding_to_max_correction)

    @staticmethod
    def get_spend_derivative_in_last_time_interval(self, campaign):
        # if percentOfBudgetDepletedInLastTimeInterval is zero then we define the derivative to be zero too
        if campaign.spend[-1][1] == 0:
            return 0
        percent_budget_depleted_in_last_time_interval = campaign.spend[-1][1] / campaign.daily_budget
        return percent_budget_depleted_in_last_time_interval / percent_of_day_in_one_iteration

    @staticmethod
    def get_gradient_error(self, relative_spend_derivative_in_last_time_interval, current_target_slope):
        return relative_spend_derivative_in_last_time_interval - current_target_slope

    @staticmethod
    def get_gradient_error_intensity(self, gradient_error):
        return min(1, abs(gradient_error))

    @staticmethod
    def get_gradient_error_correction(self, gradient_error_intensity):
        return max(minimal_non_zero_ps_correction, max_ps_correction * gradient_error_intensity / gradient_error_corresponding_to_max_correction)

    @staticmethod
    def get_estimated_intervals_until_target_is_hit(self, spend_error, gradient_error):
        if gradient_error == 0:
            return max_interval
        return -1 * num_iterations_per_day * spend_error / gradient_error

    @staticmethod
    def get_pacing_signal_correction_weights(self, estimated_intervals_until_target_is_hit):
        """returns the spend error and the gradient error weights"""
        if estimated_intervals_until_target_is_hit < 0:
            return 0.5, 0.5
        w1 = min(max_ps_correction_weight, ps_correction_weight_factor * estimated_intervals_until_target_is_hit)
        return w1, 1.0-w1

    @staticmethod
    def get_new_pacing_signal(self, previous_ps, spend_error, gradient_error, w1, w2):
        spend_error_intensity = self.get_spend_error_intensity(spend_error)
        spend_error_correction = self.get_sepnd_error_correction(spend_error_intensity)
        spend_error_sign = np.sign(spend_error)
        gradient_error_intensity = self.get_gradient_error_intensity(gradient_error)
        gradient_error_correction = self.get_gradient_error_correction(gradient_error_intensity)
        gradient_error_sign = np.sign(gradient_error)

        return previous_ps - (w1 * spend_error_correction * spend_error_sign) - (w2 * gradient_error_correction * gradient_error_sign)



