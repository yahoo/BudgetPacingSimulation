import math
import random

import src.constants as constants
from src.constants import AuctionType
from src.system.daily_cosine import DailyCosineWave
from scipy import stats

# General
num_days_to_simulate = 7
num_iterations_per_day = 1440
auction_type = AuctionType.FP
output_only_summarized_statistics = False

# Budget Pacing System
pacing_algorithm = constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR

# Campaigns
num_campaigns = 100
campaign_min_budget = 5
campaign_max_budget = 1500
campaign_min_run_period = 1
campaign_minimal_bid = 0
num_spend_entries_per_day = 1  # Defines the granularity with which to store spend history inside Campaigns.
num_win_entries_per_day = 24  # Defines the granularity with which to store win history inside Campaigns.
max_bid_factor_of_bids_mean = 10  # Defines the maximal bid for campaigns as a factor of the distribution's mean

# Untracked bids
factor_untracked_bids = 2

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
        2: DailyCosineWave(6, 0.5, 0.4),
        3: DailyCosineWave(7, 0.8, 0.5),
        4: DailyCosineWave(8, 0.7, 0.8),
        5: DailyCosineWave(9, 0.4, 0.8)
    }
}


# # #  Distributions  # # #
# # Traffic
# We calculate the mean of the distribution of the number of auctions in each minute (m) of the day as:
# dc * (1 + amplitude * math.cos((2*math.pi)*(m/num_iterations_per_day + phase))),
# We use that value to define the mean of a Poisson distribution, from which we will sample the number of auctions
traffic_mean_cos_wave = DailyCosineWave(dc=1500, amplitude=0.75, phase=0.2)

# # Untracked Bids
# # # The distribution of the log() of the bids is approximated as a normal distribution
# untracked_bids_log_distribution = norm(loc=-8.19, scale=2.14)
untracked_bids_distribution = stats.lognorm(s=2.14, scale=math.exp(-8.19))

# # Bids of Tracked Campaigns
# from scipy.stats.lognorm docs: "Suppose a normally distributed random variable X has mean mu and
# standard deviation sigma. Then Y = exp(X) is lognormally distributed with s = sigma and scale = exp(mu)."
# We define low budget as <100$ daily budget, medium is between 100$ and 200$, and high is >200$
medium_budget_range_min_value = 100
high_budget_range_min_value = 200

bids_distribution_low_budget = stats.lognorm(s=3.0, scale=math.exp(-9.06))
bids_distribution_medium_budget = stats.lognorm(s=2.47, scale=math.exp(-8.08))
bids_distribution_high_budget = stats.lognorm(s=1.95, scale=math.exp(-7.76))

# # Distribution of Daily Budgets
# # # The distribution of the log() of the daily budgets is approximated as a gamma distribution
daily_budgets_log_distribution = stats.gamma(a=3.77, loc=0.0, scale=1.0)

# Set the following seeds to generate consistent campaigns across simulations
daily_budgets_log_distribution.random_state = 42
random.seed(42)
