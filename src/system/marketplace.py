from src.system.auction import *
from src.system.budget_pacing.mystique.clock import Clock
from src.system.campaign import Campaign
from src.system.serving_system import ServingSystem
from src import configuration


class Marketplace:
    def __init__(self, serving_system: ServingSystem, auction_type: AuctionType = AuctionType.FP):
        if serving_system is None:
            raise Exception('invalid serving_system parameter')
        self.serving_system = serving_system
        self.auction_type = auction_type
        self.current_auctions = self._generate_auctions()

    def _calculate_number_of_current_auctions(self) -> int:
        # We will later sample from distribution according to Clock.minutes()
        return configuration.n_auctions_per_iteration

    def _generate_auction(self) -> AuctionInterface:
        if self.auction_type != AuctionType.FP:
            raise NotImplementedError
        return AuctionFP()

    def _generate_auctions(self) -> list[AuctionInterface]:
        n_auctions = self._calculate_number_of_current_auctions()
        return [self._generate_auction() for _ in range(n_auctions)]

    def _get_current_auctions(self) -> list[AuctionInterface]:
        return self.current_auctions

    def _run_single_auction(self, auction: AuctionInterface):
        bids = self.serving_system.get_bids()
        if len(bids) == 0:
            return
        winners = auction.run(bids)
        self.serving_system.update_winners(winners)

    def _run_auctions(self):
        auctions = self._get_current_auctions()
        for auction in auctions:
            self._run_single_auction(auction)

    def add_campaign(self, campaign: Campaign):
        if campaign is None:
            raise Exception('cannot add a None campaign')
        self.serving_system.add_campaign(campaign)

    def _new_day_init(self):
        self.serving_system.new_day_updates()

    def run_iteration(self):
        self._run_auctions()
        Clock.advance()
        # generate new auctions for the new iteration
        self.current_auctions = self._generate_auctions()
        if Clock.minutes() == 0:
            self._new_day_init()
