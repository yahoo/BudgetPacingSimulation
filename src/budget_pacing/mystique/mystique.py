from src.budget_pacing.pacing_system_interface import PacingSystemInterface
import target_slope
from target_slope import TargetSpendSlopeType
import numpy as np

num_iterations_per_day = 1440
num_iterations_per_hour = 60
previous_pacing_signal_for_initialization = 0.0001
max_ps = 1
error_corresponding_to_max_correction = 0.25
gradient_error_corresponding_to_max_correction = 1.5
max_ps_correction = 0.025
minimal_Non_zero_ps_correction = 0.01
min_daily_budget_for_high_initialization = 10000


class MystiqueTrackedCampaigns:
    def __init__(self, daily_budget):
        self.daily_budget = daily_budget
        self.ps_history = np.array([(0, self.previous_ps)]) # each entry is a timestamp and the ps calculated for this iteration
        self.spend = np.array([(0, 0)])   # each entry is a timestamp and the spend reported from the previous iteration
        self.current_target_slope = np.array([])
        self.target_slope_history = np.array([])
        self.current_target_spend_curve = np.array([])
        self.target_spend_history = np.array([])
        self.previous_ps = 0    # updated again in new_day_init
        self.last_positive_ps = 0   # updated again in new_day_init
        self.new_day_init(daily_budget)

    def new_day_init(self, daily_budget):
        if daily_budget < min_daily_budget_for_high_initialization:
            self.previous_ps = previous_pacing_signal_for_initialization
        else:
            self.previous_ps = max_ps
        self.last_positive_ps = self.previous_ps

    def update_spend(self, timestamp, spend):
        self.spend.append((timestamp, spend))

    def update_target_slope_curve(self, timestamp, target_slope_curve):
        self.target_slope_history.append((timestamp, target_slope_curve))
        self.current_target_slope = target_slope_curve

    def update_target_spend_curve(self, timestamp, target_spend_curve):
        self.target_spend_history.append((timestamp, target_spend_curve))
        self.current_target_spend_curve = target_spend_curve


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

    def update_campaign_spend(self, timestamp, campaign_id, spend_since_last_run):
        if campaign_id in self.campaigns.keys():
            self.campaigns[campaign_id].update_spend(timestamp, spend_since_last_run)

    def get_pacing_signal(self, campaign_id):
        pass
