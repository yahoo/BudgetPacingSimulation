import math
from enum import Enum

from scipy.stats import lognorm, gamma

num_minutes_in_hour = 60
num_minutes_in_day = 24 * num_minutes_in_hour


class BudgetPacingAlgorithms(Enum):
    MYSTIQUE_LINEAR = 1
    MYSTIQUE_NON_LINEAR = 2
    MYSTIQUE_LINEAR_HARD_THROTTLING = 3
    MYSTIQUE_NON_LINEAR_HARD_THROTTLING = 4


class AuctionType(Enum):
    FP = 1
    GSP = 2


# output metrics field names
FIELD_CAMPAIGN_ID = 'Campaign'
FIELD_DAILY_BUDGET = 'Daily Budget'
FIELD_DAY_STARTED = 'Day Started'
FIELD_DAY_ENDED = 'Day Ended'
FIELD_BUDGET_UTILIZATION = 'Budget Utilization'
FIELD_DAY_ID = 'Day'
FIELD_CPM = 'CPM'
FIELD_NUM_OVER_BUDGET_CAMPAIGNS = '# Over Budget Campaigns'
FIELD_NUM_WINS = '# Impressions'
FIELD_OVERSPEND = 'Overspend'
FIELD_SPEND = 'Spend'

OVERALL_STATISTICS_ROW_NAME = 'Overall'

# Distributions

# # Untracked Bids
# # # The distribution of the log() of the bids is approximated as a normal distribution
# untracked_bids_log_distribution = norm(loc=-8.19, scale=2.14)
untracked_bids_distribution = lognorm(s=2.14, scale=math.exp(-8.19))

# # Distribution of Daily Budgets
# # # The distribution of the log() of the daily budgets is approximated as a gamma distribution
daily_budgets_log_distribution = gamma(a=3.77, loc=0.0, scale=1.0)  # can also use norm(loc=3.788, scale=2.188)
