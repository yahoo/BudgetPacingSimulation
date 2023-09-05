from enum import Enum

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

