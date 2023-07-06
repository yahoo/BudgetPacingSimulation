import abc


class PacingSystemInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'add_campaign') and
                callable(subclass.add_campaign) and
                hasattr(subclass, 'update_campaign_spend') and
                callable(subclass.update_campaign_spend) and
                hasattr(subclass, 'get_pacing_signal') and
                callable(subclass.get_pacing_signal))

    @abc.abstractmethod
    def add_campaign(self, campaign):
        """Add a tracked campaign to the budgt pacing system"""
        raise NotImplementedError

    @abc.abstractmethod
    def update_campaign_spend(self, timestamp, campaign_id, spend_since_last_run):
        """updates the current spend of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_pacing_signal(self, campaign_id):
        """Returns the current pacing signal of the campaign"""
        raise NotImplementedError