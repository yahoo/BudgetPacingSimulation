from enum import Enum

num_minutes_in_hour = 60
num_minutes_in_day = 24 * num_minutes_in_hour


class BudgetPacingAlgorithms(Enum):
    MYSTIQUE_LINEAR = 1
    MYSTIQUE_NON_LINEAR = 2
