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
                callable(subclass.run))

    @abc.abstractmethod
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        raise NotImplementedError


class AuctionFP(AuctionInterface):
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        if not bids:
            return []
        winning_bid = max(bids)
        if winning_bid.amount < config.campaign_minimal_bid:
            return []
        return [AuctionWinner(bid=winning_bid, payment=winning_bid.amount)]
