from src.budget_pacing.pacing_system_interface import PacingSystemInterface
import target_slope
from target_slope import TargetSpendSlopeType
import numpy as np


class MystiqueTrackedCampaigns:
    def __init__(self, daily_budget):
        self.daily_budget = daily_budget
        self.spend = [(0, 0)]   # each entry is the current timestamp and the spend reported from the previous iteration
        self.current_target_slope = []
        self.target_slope_history = []
        self.current_target_spend_curve = []
        self.target_spend_history = []

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
