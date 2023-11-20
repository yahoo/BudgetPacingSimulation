# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import abc


class PacingSystemInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'add_campaign') and
                callable(subclass.add_campaign) and
                hasattr(subclass, 'end_iteration') and
                callable(subclass.end_iteration) and
                hasattr(subclass, 'get_pacing_signal') and
                callable(subclass.get_pacing_signal))

    @abc.abstractmethod
    def add_campaign(self, campaign):
        """Add a tracked campaign to the budget pacing system"""
        raise NotImplementedError

    @abc.abstractmethod
    def end_iteration(self, campaign_id, spend_since_last_iteration):
        """updates the current spend of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_pacing_signal(self, campaign_id):
        """Returns the current pacing signal of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_pacing_statistics(self, campaign_id: str) -> dict[str, object]:
        """Returns the pacing statistics of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_global_pacing_statistics(self) -> dict[str, object]:
        """Returns the global pacing statistics"""
        raise NotImplementedError

