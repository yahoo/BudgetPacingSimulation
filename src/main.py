from src import system_generation_utils
from src.configuration import *
from src.system.clock import Clock
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem


if __name__ == '__main__':
    campaigns = system_generation_utils.generate_campaigns(num_campaigns)
    serving_system = ServingSystem(tracked_campaigns=campaigns)
    marketplace = Marketplace(serving_system=serving_system)
    # Run
    for _ in range(num_days_to_simulate * num_iterations_per_day):
        marketplace.run_iteration()
        if Clock.minutes_in_day() == 0:
            serving_system.new_day_updates()
