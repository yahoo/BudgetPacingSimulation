import abc
from enum import Enum
from src.system.clock import Clock

import src.system.budget_pacing.mystique.mystique_constants as mystique_constants
from src.system.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign


class TargetSpendStrategyType(Enum):
    LINEAR = 1
    NON_LINEAR = 2


class TargetSpendStrategyInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'initialize_slope') and
                callable(subclass.initialize_slope) and
                hasattr(subclass, 'update_slope') and
                callable(subclass.update_campaign_spend) and
                hasattr(subclass, 'get_target_slope_and_spend') and
                callable(subclass.get_target_slope_and_spend))

    @abc.abstractmethod
    def initialize_slope(self, mystique_tracked_campaign):
        """initializing slope of target spend"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_slope(self, mystique_tracked_campaign):
        """updating the slope of the campaign according to last day behavior"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_target_slope_and_spend(self, mystique_tracked_campaign):
        """getting the target slope and spend for the next iteration"""
        raise NotImplementedError


class LinearTargetSpendStrategy(TargetSpendStrategyInterface):
    def initialize_slope(self, mystique_tracked_campaign: MystiqueTrackedCampaign):
        target_slope_array = [1] * mystique_constants.num_hours_per_day
        target_spend_array = self.get_target_spend_array(target_slope_array)
        mystique_tracked_campaign.update_target_slope_curve(target_slope_array)
        mystique_tracked_campaign.update_target_spend_curve(target_spend_array)

    def update_slope(self, mystique_tracked_campaign: MystiqueTrackedCampaign):
        target_slope_array = mystique_tracked_campaign.current_target_slope
        target_spend_array = mystique_tracked_campaign.current_target_spend_curve
        mystique_tracked_campaign.update_target_slope_curve(target_slope_array)
        mystique_tracked_campaign.update_target_spend_curve(target_spend_array)

    def get_target_slope_and_spend(self, _: MystiqueTrackedCampaign):
        percent_of_day_passed = (Clock.minute_in_day() + 1) / mystique_constants.num_iterations_per_day
        target_slope = 1
        target_spend = percent_of_day_passed * target_slope
        return target_slope, target_spend

    @staticmethod
    def get_target_spend_array(target_slope_array: list[float]):
        target_spend_array = [0] * mystique_constants.num_hours_per_day
        spend_sum = 0
        for i in range(len(target_spend_array)):
            spend_sum += target_slope_array[i] / mystique_constants.num_hours_per_day
            target_spend_array[i] = spend_sum
        return target_spend_array


class NonLinearTargetSpendStrategy(LinearTargetSpendStrategy):
    min_slope = 0.1
    max_slope = 12
    max_update_factor = 2
    smoothing_factor = 0.5
    epsilon = 0.0002

    def update_slope(self, mystique_tracked_campaign: MystiqueTrackedCampaign):

        avg_daily_ps = mystique_tracked_campaign.get_avg_daily_ps()
        avg_hourly_ps = mystique_tracked_campaign.get_avg_hourly_ps()
        current_target_slope = mystique_tracked_campaign.current_target_slope.copy()
        for i in range(len(mystique_tracked_campaign.current_target_slope)):
            daily_to_hourly_ps_ratio = \
                avg_daily_ps / avg_hourly_ps[i]

            if (avg_daily_ps < self.epsilon) or (avg_hourly_ps[i] < self.epsilon):
                update_factor = 1.0
            else:
                update_factor = min(daily_to_hourly_ps_ratio, self.max_update_factor)

            current_target_slope[i] *= update_factor
            current_target_slope[i] = min(current_target_slope[i], self.max_slope)
            current_target_slope[i] = max(current_target_slope[i], self.min_slope)

        # smoothing
        smoothed_target_slope = current_target_slope.copy()
        length = len(smoothed_target_slope)
        for i in range(length):
            smoothed_target_slope[i] = self.smoothing_factor / 2 * \
                (current_target_slope[i-1] + current_target_slope[(i+1) % length]) + \
                (1 - self.smoothing_factor) * current_target_slope[i]

        mystique_tracked_campaign.update_target_slope_curve(smoothed_target_slope)

    def get_target_slope_and_spend(self, mystique_tracked_campaign: MystiqueTrackedCampaign):
        hour = Clock.hour_in_day()
        minute_in_hour = min(Clock.minute_in_hour() + 1, mystique_constants.num_iterations_per_day - 1)

        # target slope
        target_slope = mystique_tracked_campaign.current_target_slope[hour]

        # target spend
        current_target_spend_curve = mystique_tracked_campaign.current_target_spend_curve

        if hour == 0:
            target_spend = \
                current_target_spend_curve[hour] * minute_in_hour / mystique_constants.num_iterations_per_hour
        else:
            target_spend = current_target_spend_curve[hour-1] + \
                           (current_target_spend_curve[hour] - current_target_spend_curve[hour-1]) * minute_in_hour / \
                           mystique_constants.num_iterations_per_hour

        return target_slope, target_spend


