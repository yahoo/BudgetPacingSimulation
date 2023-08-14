import abc


class PacingSystemInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'add_campaign') and
                callable(subclass.add_campaign) and
                hasattr(subclass, 'conclude_iteration') and
                callable(subclass.start_iteration) and
                hasattr(subclass, 'get_pacing_signal') and
                callable(subclass.get_pacing_signal))

    @abc.abstractmethod
    def add_campaign(self, campaign):
        """Add a tracked campaign to the budget pacing system"""
        raise NotImplementedError

    @abc.abstractmethod
    def start_iteration(self, campaign_id, spend_since_last_iteration):
        """updates the current spend of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_pacing_signal(self, campaign_id):
        """Returns the current pacing signal of the campaign"""
        raise NotImplementedError

    @abc.abstractmethod
    def new_day_init(self):
        raise NotImplementedError
