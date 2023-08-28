import numpy as np

from src.system.auction import *
from src.system.clock import Clock
from src.system.daily_cosine import DailyCosineWave
from src.system.serving_system import ServingSystem
from scipy import stats
from scipy.special import softmax


class Marketplace:
    def __init__(self, serving_system: ServingSystem, auction_type: AuctionType = AuctionType.FP,
                 traffic_mean_cos_wave: DailyCosineWave = config.traffic_mean_cos_wave):
        if serving_system is None:
            raise Exception('invalid serving_system parameter')
        self.serving_system = serving_system
        self.auction_type = auction_type
        self.traffic_mean_cos_wave = traffic_mean_cos_wave

    def run_iteration(self):
        # generate and run auctions
        auctions = self._generate_auctions()
        self._run_auctions(auctions)
        # end the iteration
        self.serving_system.end_iteration()
        Clock.advance()

    def _run_auctions(self, auctions: list[AuctionInterface]):
        for auction in auctions:
            self._run_single_auction(auction)

    def _run_single_auction(self, auction: AuctionInterface):
        bids = self.serving_system.get_bids(auction)
        if len(bids) == 0:
            return
        winners = auction.run(bids)
        self.serving_system.update_winners(winners)

    def _generate_auctions(self) -> list[AuctionInterface]:
        num_auctions = self._sample_current_num_of_auctions()
        # generate a probability array for each user property
        probabilities_per_property = {
            feature: softmax([cos_wave.calculate_current_value()
                              for cos_wave in config.user_properties[feature].values()])
            for feature in config.user_properties
        }
        return [self._generate_auction(user_properties_probabilities=probabilities_per_property)
                for _ in range(num_auctions)]

    def _generate_auction(self, user_properties_probabilities: dict[str, list[float]]) -> AuctionInterface:
        if self.auction_type == AuctionType.FP:
            user_properties = {
                feature: np.random.choice(list(config.user_properties[feature].keys()),
                                          p=user_properties_probabilities[feature])
                for feature in user_properties_probabilities
            }
            return AuctionFP(user_properties=user_properties)
        elif self.auction_type == AuctionType.GSP:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def _sample_current_num_of_auctions(self) -> int:
        # Calculate the mean of the Poisson distribution:
        mu = self._calculate_current_mean_num_of_auctions()
        # Sample from the Poisson distribution:
        return stats.poisson.rvs(mu)

    def _calculate_current_mean_num_of_auctions(self) -> float:
        # Calculate the mean of the Poisson distribution from which we sample the number of auctions for each minute.
        # The calculation depends on the current value of the Clock (minute_in_day).
        return self.traffic_mean_cos_wave.calculate_current_value()

