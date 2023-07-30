import functools


@functools.total_ordering  # this adds implementations of __le__, __gt__, __ge__, etc.
class Bid:
    def __init__(self, campaign_id: str, amount: float):
        self.campaign_id = campaign_id
        self.amount = amount

    def __eq__(self, other):
        if other is None:
            return False
        return self.campaign_id == other.campaign_id and self.amount == other.amount

    def __lt__(self, other):
        if other is None:
            return False
        return self.amount < other.amount


