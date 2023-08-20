from src.system.auction import *
from src.system.clock import Clock
from src.system.serving_system import ServingSystem
from src import configuration


class Marketplace:
    def __init__(self, serving_system: ServingSystem, auction_type: AuctionType = AuctionType.FP):
        if serving_system is None:
            raise Exception('invalid serving_system parameter')
        self.serving_system = serving_system
        self.auction_type = auction_type
        self.current_auctions = self._generate_auctions()

    def run_iteration(self):
        self._run_auctions()
        self.serving_system.end_iteration()
        Clock.advance()
        # generate new auctions for the new iteration
        self.current_auctions = self._generate_auctions()

    def _run_auctions(self):
        auctions = self._get_current_auctions()
        for auction in auctions:
            self._run_single_auction(auction)

    def _run_single_auction(self, auction: AuctionInterface):
        bids, tracked_bids_exist = self.serving_system.get_bids()
        if not tracked_bids_exist:
            return
        winners = auction.run(bids)
        self.serving_system.update_winners(winners)

    def _generate_auctions(self) -> list[AuctionInterface]:
        num_auctions = self._calculate_number_of_current_auctions()
        return [self._generate_auction() for _ in range(num_auctions)]

    def _generate_auction(self) -> AuctionInterface:
        if self.auction_type == AuctionType.FP:
            return AuctionFP()
        elif self.auction_type == AuctionType.GSP:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def _get_current_auctions(self) -> list[AuctionInterface]:
        return self.current_auctions

    def _calculate_number_of_current_auctions(self) -> int:
        # We will later sample from distribution according to Clock.minutes()
        return configuration.num_auctions_per_iteration
