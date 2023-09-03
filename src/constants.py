from enum import Enum

num_minutes_in_hour = 60
num_minutes_in_day = 24 * num_minutes_in_hour


class BudgetPacingAlgorithms(Enum):
    MYSTIQUE_LINEAR = 1
    MYSTIQUE_NON_LINEAR = 2


# output metrics field names
FIELD_CAMPAIGN_ID = 'campaign_id'
FIELD_DAILY_BUDGET = 'daily_budget'
FIELD_DAY_STARTED = 'day_started'
FIELD_DAY_ENDED = 'day_ended'
FIELD_NUM_AUCTIONS_WON_HISTORY = 'num_auctions_won_history'

# Distributions
UNTRACKED_BIDS_LOG_NORM_MU = -8.192
UNTRACKED_BIDS_LOG_NORM_SIGMA = 2.14


