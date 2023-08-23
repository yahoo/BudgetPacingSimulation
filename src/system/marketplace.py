from src.system.auction import *
from src.system.clock import Clock
from src.system.serving_system import ServingSystem
from scipy import stats
import math


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
        bids = self.serving_system.get_bids()
        if len(bids) == 0:
            return
        winners = auction.run(bids)
        self.serving_system.update_winners(winners)

    def _generate_auctions(self) -> list[AuctionInterface]:
        num_auctions = self._sample_current_num_of_auctions()
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

    @staticmethod
    def _sample_current_num_of_auctions() -> int:
        # Calculate the mean of the Poisson distribution:
        mu = Marketplace._calculate_current_mean_num_of_auctions()
        # Sample from the Poisson distribution:
        return stats.poisson.rvs(mu)

    @staticmethod
    def _calculate_current_mean_num_of_auctions() -> float:
        # Calculate the mean of the Poisson distribution from which we sample the number of auctions for each minute.
        # The calculation depends on the current value of the Clock (minute_in_day).
        return config.dist_mean_num_auctions_in_minute_param_a \
            + config.dist_mean_num_auctions_in_minute_param_b * \
            math.cos(
                (2 * math.pi * Clock.minute_in_day() / config.num_iterations_per_day) +
                config.dist_mean_num_auctions_in_minute_param_c
            )
