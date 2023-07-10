import abc
import numpy as np
from enum import Enum

from mystique import num_iterations_per_day
from mystique import num_iterations_per_hour


class TargetSpendSlopeType(Enum):
    LINEAR = 1
    NON_LINEAR = 2


class TargetSpendSlopeInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'initialize_slope') and
                callable(subclass.initialize_slope) and
                hasattr(subclass, 'update_slope') and
                callable(subclass.update_campaign_spend) and
                hasattr(subclass, 'get_target_slope_and_spend') and
                callable(subclass.get_target_slope_and_spend))

    @abc.abstractmethod
    def initialize_slope(self, timestamp, mystique_tracked_campaign):
        """initializing slope of target spend"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_slope(self, timestamp, mystique_tracked_campaign):
        """updating the slope of the campaign according to last day behavior"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_target_slope_and_spend(self, timestamp, mystique_tracked_campaign):
        """getting the target slope and spend corresponding to the timestamp"""
        raise NotImplementedError



class LinearTargetSpendSlope(TargetSpendSlopeInterface):
    def initialize_slope(self, timestamp, mystique_tracked_campaign):
        target_slope_array = np.ones(24)
        target_spend_array = self.get_target_spend_array(target_slope_array)
        mystique_tracked_campaign.update_target_slope_curve(timestamp, target_slope_array)
        mystique_tracked_campaign.update_target_spend_curve(timestamp, target_spend_array)

    def update_slope(self, timestamp, mystique_tracked_campaign):
        target_slope_array = mystique_tracked_campaign.current_target_slope
        target_spend_array = mystique_tracked_campaign.current_target_spend_curve
        mystique_tracked_campaign.update_target_slope_curve(timestamp, target_slope_array)
        mystique_tracked_campaign.update_target_spend_curve(timestamp, target_spend_array)

    def get_target_slope_and_spend(self, timestamp, mystique_tracked_campaign):
        minutes_since_day_started = timestamp % num_iterations_per_day
        hour_in_day = min(int(minutes_since_day_started / num_iterations_per_hour), 23)
        percent_of_day_passed = minutes_since_day_started / num_iterations_per_day
        target_slope = 1
        target_spend = percent_of_day_passed * target_slope
        return target_slope, target_spend

    @staticmethod
    def get_target_spend_array(target_slope_array):
        target_spend_array = np.zeros(24)
        spend_sum = 0
        for i in range(24):
            spend_sum += target_slope_array[i] / 24
            target_spend_array[i] = spend_sum
        return target_spend_array


class NonLinearTargetSpendSlope(LinearTargetSpendSlope):
    min_slope = 0.1
    max_slope = 12
    max_update_factor = 2
    smoothing_factor = 0.5
    epsilon = 0.0002

    def update_slope(self, timestamp, mystique_tracked_campaign):
        pass

    def get_target_slope_and_spend(self, timestamp, mystique_tracked_campaign):
        pass

