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

    @abc.abstractmethod
    def min_bid(self) -> float:
        raise NotImplementedError


class AuctionFP(AuctionInterface):
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        if len(bids) == 0:
            return []
        winning_bid = max(bids)
        return [AuctionWinner(bid=winning_bid, payment=winning_bid.amount)]

    def min_bid(self) -> float:
        return constants.AUCTIONS_MIN_BID_DEFAULT

