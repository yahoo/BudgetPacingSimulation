import abc
import numpy as np
from enum import Enum


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
                hasattr(subclass, 'get_pacing_signal'))

    @abc.abstractmethod
    def initialize_slope(self, timestamp, mystique_tracked_campaign):
        """Add a tracked campaign to the budgt pacing system"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_slope(self, timestamp, mystique_tracked_campaign):
        """Add a tracked campaign to the budgt pacing system"""
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

    @staticmethod
    def get_target_spend_array(target_slope_array):
        target_spend_array = np.zeros(24)
        spend_sum = 0
        for i in range(24):
            spend_sum += target_slope_array[i] / 24
            target_spend_array[i] = spend_sum
        return target_spend_array


class NonLinearTargetSpendSlope(LinearTargetSpendSlope):
    def update_slope(self, timestamp, mystique_tracked_campaign):
        pass

