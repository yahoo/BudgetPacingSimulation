import src.constants as constants

# General
num_days_to_simulate = 1
num_iterations_per_day = 1440
num_auctions_per_iteration = 1000
# Budget Pacing System
pacing_algorithm = constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR

# Campaigns
num_campaigns = 2
campaign_min_budget = 1000
campaign_max_budget = 10000
campaign_min_run_period = 1
campaign_max_run_period = 30
campaign_minimal_max_bid = 0.05
campaign_maximal_max_bid = 15
campaign_minimal_bid = 0.01
num_spend_entries_per_day = 1  # Defines the granularity with which to store spend history inside Campaigns.
num_win_entries_per_day = 24  # Defines the granularity with which to store win history inside Campaigns.

# Untracked bids
num_untracked_bids = 50
untracked_bid_max = 20
