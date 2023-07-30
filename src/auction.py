import abc
from enum import Enum

from src import constants
from src.bid import Bid
from dataclasses import dataclass


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
                hasattr(subclass, 'min_bid') and
                callable(subclass.run))

    @abc.abstractmethod
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        raise NotImplementedError


class AuctionFP(AuctionInterface):
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        if len(bids) == 0:
            return []
        winning_bid = max(bids)
        if winning_bid.amount < constants.MINIMAL_BID:
            return []
        return [AuctionWinner(bid=winning_bid, payment=winning_bid.amount)]


