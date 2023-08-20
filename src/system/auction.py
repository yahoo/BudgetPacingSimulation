import abc
from enum import Enum

from src.system.bid import Bid
from dataclasses import dataclass
import src.configuration as config


@dataclass
class AuctionWinner:
    bid: Bid
    payment: float


class AuctionType(Enum):
    FP = 1
    GSP = 2


class AuctionInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'run') and
                callable(subclass.run) and
                hasattr(subclass, 'targeting_group') and
                callable(subclass.targeting_group))

    @abc.abstractmethod
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        raise NotImplementedError

    @abc.abstractmethod
    def targeting_group(self) -> int:
        raise NotImplementedError


class AuctionFP(AuctionInterface):
    def __init__(self, targeting_group: int):
        assert 0 <= targeting_group < config.num_targeting_groups
        self._targeting_group = targeting_group

    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        if len(bids) == 0:
            return []
        winning_bid = max(bids)
        if winning_bid.amount < config.campaign_minimal_bid:
            return []
        return [AuctionWinner(bid=winning_bid, payment=winning_bid.amount)]

    def targeting_group(self) -> int:
        return self._targeting_group
