import numpy as np

from src.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.campaign import Campaign
import target_slope
from target_slope import TargetSpendStrategyType
import mystique_constants


class MystiqueTrackedCampaign:
    def __init__(self, daily_budget: float):
        self.daily_budget = daily_budget
        self.ps = mystique_constants.default_ps_value     # to be updated in update_pacing_signal
        self.previous_ps = mystique_constants.default_ps_value  # updated again in new_day_init
        self.last_positive_ps = mystique_constants.default_ps_value  # updated again in new_day_init
        self.ps_history = [] # list of lists for each day, each entry in arr is the calculated ps and the location is number of iteration
        self.today_ps = []    # each entry is the calculated PS, the location in the arr is the number of iteration
        self.spend_history = []   # list of lists for each day, each entry in arr is the spend and the location is number of iteration
        self.today_spend = []   # each entry is the spend reported from the previous iteration, the location in the arr is the number of iteration
        self.current_target_slope = []
        self.target_slope_history = []
        self.current_target_spend_curve = []
        self.target_spend_history = []
        self.new_day_init()

    def new_day_init(self):
        if self.daily_budget < mystique_constants.min_daily_budget_for_high_initialization:
            self.previous_ps = mystique_constants.previous_pacing_signal_for_initialization
        else:
            self.previous_ps = mystique_constants.max_ps
        self.last_positive_ps = self.previous_ps

        # updating the PS history arr and initializing today's PS arr
        if len(self.today_ps) > 0:
            self.ps_history.append(self.today_ps)
        self.today_ps = []

        # updating the spend history arr and initializing today's spend arr
        if len(self.today_spend) > 0:
            self.spend_history.append(self.today_spend)
        self.today_spend = []

    def update_pacing_signal(self, ps: float):
        self.previous_ps = self.ps
        if self.ps > 0:
            self.last_positive_ps = self.ps
        self.ps = ps
        self.today_ps.append(ps)

    def update_spend(self, spend: float):
        self.today_spend.append(spend)

    def update_target_slope_curve(self, target_slope_curve: list[float]):
        if len(self.current_target_slope) > 0:
            self.target_slope_history.append(self.current_target_slope)
        self.current_target_slope = target_slope_curve

    def update_target_spend_curve(self, target_spend_curve: list[float]):
        if len(self.current_target_spend_curve) > 0:
            self.target_spend_history.append(self.current_target_spend_curve)
        self.current_target_spend_curve = target_spend_curve

    def get_spend_in_last_time_interval(self):
        return self.today_spend[-1]

    def get_today_spend(self):
        return sum(self.today_spend)


class MystiquePacingSystem(PacingSystemInterface):
    def __init__(self, target_slope_type: TargetSpendStrategyType):
        self.mystique_tracked_campaigns = {}    # a dict containing campaign id as key and MystiqueTrackedCampaigns instance as val
        if target_slope_type == TargetSpendStrategyType.LINEAR:
            self.target_spend_slope_calculator = target_slope.LinearTargetSpendStrategy()
        elif target_slope_type == TargetSpendStrategyType.NON_LINEAR:
            self.target_spend_slope_calculator = target_slope.NonLinearTargetSpendStrategy()

    def add_campaign(self, campaign: Campaign):
        campaign_id = campaign.id
        daily_budget = campaign.daily_budget
        if campaign_id not in self.mystique_tracked_campaigns.keys():
            self.mystique_tracked_campaigns[campaign_id] = MystiqueTrackedCampaign(daily_budget)

    def start_iteration(self, timestamp: int, campaign_id: str, spend_since_last_iteration: float):
        if campaign_id in self.mystique_tracked_campaigns.keys():
            mystique_tracked_campaign = self.mystique_tracked_campaigns[campaign_id]
            mystique_tracked_campaign.update_spend(spend_since_last_iteration)

            new_ps = self.calculate_new_pacing_signal(timestamp, mystique_tracked_campaign)
            self.update_pacing_signal(timestamp, mystique_tracked_campaign)

    def get_pacing_signal(self, campaign_id: str):
        if campaign_id in self.mystique_tracked_campaigns.keys():
            return self.mystique_tracked_campaigns[campaign_id].ps
        return mystique_constants.default_ps_value

    def update_pacing_signal(self, timestamp: int, mystique_tracked_campaign: MystiqueTrackedCampaign):
        new_ps = self.calculate_new_pacing_signal(timestamp, mystique_tracked_campaign)
        mystique_tracked_campaign.update_pacing_signal(new_ps)

    def calculate_new_pacing_signal(self, timestamp: int, mystique_tracked_campaign: MystiqueTrackedCampaign):
        percent_budget_depleted_today = self.get_percent_budget_depleted_today(mystique_tracked_campaign)
        current_target_slope, current_target_spend = self.target_spend_slope_calculator.get_target_slope_and_spend(timestamp, mystique_tracked_campaign)
        spend_error = self.get_spend_error(percent_budget_depleted_today, current_target_spend)

        spend_derivative_in_last_time_interval = self.get_spend_derivative_in_last_time_interval(mystique_tracked_campaign)
        gradient_error = self.get_gradient_error(spend_derivative_in_last_time_interval, current_target_slope)

        estimated_intervals_until_target_is_hit = self.get_estimated_intervals_until_target_is_hit(spend_error, gradient_error)
        w1, w2 = self.get_pacing_signal_correction_weights(estimated_intervals_until_target_is_hit)
        previous_ps = mystique_tracked_campaign.last_positive_ps
        return self.get_new_pacing_signal(previous_ps, spend_error, gradient_error, w1, w2)

    @staticmethod
    def get_percent_budget_depleted_today(self, mystique_tracked_campaign: MystiqueTrackedCampaign):
        return mystique_tracked_campaign.get_today_spend() / mystique_tracked_campaign.daily_budget

    @staticmethod
    def get_spend_error(self, percent_budget_depleted_today: float, current_target_spend: float):
        return percent_budget_depleted_today - current_target_spend

    @staticmethod
    def get_spend_error_intensity(self, spend_error: float):
        return abs(spend_error)

    @staticmethod
    def get_spend_error_correction(self, error_intensity: float):
        return mystique_constants.max_ps_correction * min(1, error_intensity / mystique_constants.error_corresponding_to_max_correction)

    @staticmethod
    def get_spend_derivative_in_last_time_interval(self, mystique_tracked_campaign: MystiqueTrackedCampaign):
        # if percentOfBudgetDepletedInLastTimeInterval is zero then we define the derivative to be zero too
        last_spend = mystique_tracked_campaign.today_spend[-1]
        if last_spend == 0:
            return 0
        percent_budget_depleted_in_last_time_interval = last_spend / mystique_tracked_campaign.daily_budget
        return percent_budget_depleted_in_last_time_interval / mystique_constants.percent_of_day_in_one_iteration

    @staticmethod
    def get_gradient_error(self, relative_spend_derivative_in_last_time_interval: float, current_target_slope: float):
        return relative_spend_derivative_in_last_time_interval - current_target_slope

    @staticmethod
    def get_gradient_error_intensity(self, gradient_error: float):
        return min(1, abs(gradient_error))

    @staticmethod
    def get_gradient_error_correction(self, gradient_error_intensity: float):
        return max(mystique_constants.minimal_non_zero_ps_correction, mystique_constants.max_ps_correction * gradient_error_intensity / mystique_constants.gradient_error_corresponding_to_max_correction)

    @staticmethod
    def get_estimated_intervals_until_target_is_hit(self, spend_error: float, gradient_error: float):
        if gradient_error == 0:
            return mystique_constants.max_interval
        return -1 * mystique_constants.num_iterations_per_day * spend_error / gradient_error

    @staticmethod
    def get_pacing_signal_correction_weights(self, estimated_intervals_until_target_is_hit: float):
        """returns the spend error and the gradient error weights"""
        if estimated_intervals_until_target_is_hit < 0:
            return 0.5, 0.5
        w1 = min(mystique_constants.max_ps_correction_weight, mystique_constants.ps_correction_weight_factor * estimated_intervals_until_target_is_hit)
        return w1, 1.0-w1

    @staticmethod
    def get_new_pacing_signal(self, previous_ps: float, spend_error: float, gradient_error: float, w1: float, w2: float):
        spend_error_intensity = self.get_spend_error_intensity(spend_error)
        spend_error_correction = self.get_sepnd_error_correction(spend_error_intensity)
        spend_error_sign = np.sign(spend_error)
        gradient_error_intensity = self.get_gradient_error_intensity(gradient_error)
        gradient_error_correction = self.get_gradient_error_correction(gradient_error_intensity)
        gradient_error_sign = np.sign(gradient_error)

        return previous_ps - (w1 * spend_error_correction * spend_error_sign) - (w2 * gradient_error_correction * gradient_error_sign)



