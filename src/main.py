from src import utils
from src.configuration import *
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem


if __name__ == '__main__':
    campaigns = utils.generate_campaigns(n_campaigns)
    serving_system = ServingSystem(tracked_campaigns=campaigns,
                                   n_fake_bids=n_fake_bids, fake_bid_max=fake_bid_max)
    marketplace = Marketplace(serving_system=serving_system)
    # Run
    for _ in range(n_iterations):
        marketplace.run_iteration()
