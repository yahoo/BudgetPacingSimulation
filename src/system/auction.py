import abc

from src.system.bid import Bid
from dataclasses import dataclass
import src.configuration as config


@dataclass
class AuctionWinner:
    bid: Bid
    payment: float


class AuctionInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'run') and
                callable(subclass.run) and
                hasattr(subclass, 'user_properties') and
                callable(subclass.user_properties))

    @abc.abstractmethod
    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        raise NotImplementedError

    @abc.abstractmethod
    def user_properties(self) -> dict[str, int]:
        raise NotImplementedError


class AuctionFP(AuctionInterface):
    def __init__(self, user_properties: dict[str, int]):
        assert user_properties is not None
        self._user_properties = user_properties

    def run(self, bids: list[Bid]) -> list[AuctionWinner]:
        if not bids:
            return []
        winning_bid = max(bids)
        if winning_bid.amount < config.campaign_minimal_bid:
            return []
        return [AuctionWinner(bid=winning_bid, payment=winning_bid.amount)]

    def user_properties(self) -> dict[str, int]:
        return self._user_properties
