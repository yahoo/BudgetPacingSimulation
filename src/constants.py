from enum import Enum
from scipy.stats import norm

num_minutes_in_hour = 60
num_minutes_in_day = 24 * num_minutes_in_hour


class BudgetPacingAlgorithms(Enum):
    MYSTIQUE_LINEAR = 1
    MYSTIQUE_NON_LINEAR = 2


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
untracked_bids_log_distribution = norm(loc=-8.19, scale=2.14)
# # Distribution of MU and SIGMA of bid distributions of campaigns
# # # We sample MU and SIGMA for each campaign to set its bid distribution from which we sample its bids
distribution_of_mu_of_bids_log_distribution = norm(loc=-8.32, scale=1.69)
distribution_of_sigma_of_bids_log_distribution = norm(loc=1.34, scale=0.437)
