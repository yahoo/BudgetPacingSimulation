from enum import Enum

num_minutes_in_hour = 60
num_minutes_in_day = 24 * num_minutes_in_hour


class BudgetPacingAlgorithms(str, Enum):  # inheritance from str enables comparing with strings
    MYSTIQUE_LINEAR = 'linear-soft'
    MYSTIQUE_NON_LINEAR = 'non-linear-soft'
    MYSTIQUE_LINEAR_HARD_THROTTLING = 'linear-hard'
    MYSTIQUE_NON_LINEAR_HARD_THROTTLING = 'non-linear-hard'


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

