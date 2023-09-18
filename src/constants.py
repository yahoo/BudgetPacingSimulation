import math
from enum import Enum

from scipy import stats

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
untracked_bids_distribution = stats.lognorm(s=2.14, scale=math.exp(-8.19))

# # Bids of Tracked Campaigns
# from scipy.stats.lognorm docs: "Suppose a normally distributed random variable X has mean mu and
# standard deviation sigma. Then Y = exp(X) is lognormally distributed with s = sigma and scale = exp(mu)."
# We define low budget as <100$ daily budget, medium is between 100$ and 200$, and high is >200$
bids_distribution_low_budget = stats.lognorm(s=3.0, scale=math.exp(-9.06))
bids_distribution_medium_budget = stats.lognorm(s=2.47, scale=math.exp(-8.08))
bids_distribution_high_budget = stats.lognorm(s=1.95, scale=math.exp(-7.76))

# # Distribution of Daily Budgets
# # # The distribution of the log() of the daily budgets is approximated as a gamma distribution
daily_budgets_log_distribution = stats.gamma(a=3.77, loc=0.0, scale=1.0)
