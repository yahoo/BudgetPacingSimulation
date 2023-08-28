import src.constants as constants
from src.system.daily_cosine import DailyCosineWave

# General
num_days_to_simulate = 7
num_iterations_per_day = 1440

# Budget Pacing System
pacing_algorithm = constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR

# Campaigns
num_campaigns = 1000
campaign_min_budget = 1000
campaign_max_budget = 10000
campaign_min_run_period = 1
campaign_max_run_period = 30
campaign_minimal_max_bid = 1.5
campaign_maximal_max_bid = 2
campaign_minimal_bid = 0.01
num_spend_entries_per_day = 1  # Defines the granularity with which to store spend history inside Campaigns.
num_win_entries_per_day = 24  # Defines the granularity with which to store win history inside Campaigns.

# Untracked bids
num_untracked_bids = 10
untracked_bid_max = 1.2

# Auctions
# # Targeting Groups
user_properties = {
    'Gender': {
        0: DailyCosineWave(1, 0.5, 0.2),
        1: DailyCosineWave(1, 0.5, 0.8)
    },
    'Location': {
        0: DailyCosineWave(5, 0.4, 0),
        1: DailyCosineWave(5, 0.2, 0.5),
        2: DailyCosineWave(6, 0.5, 1),
        3: DailyCosineWave(7, 0.8, 1.5),
        4: DailyCosineWave(8, 0.7, 1.8),
        5: DailyCosineWave(9, 0.4, 1.8)
    }
}

# # #  Distributions  # # #
# We calculate the mean of the distribution of the number of auctions in each minute (m) of the day as:
# dc * (1 + amplitude * math.cos((2*math.pi)*(m/num_iterations_per_day + phase))),
# We use that value to define the mean of a Poisson distribution, from which we will sample the number of auctions
traffic_mean_cos_wave = DailyCosineWave(dc=1500, amplitude=0.75, phase=1.2)

