import math
import random
from typing import Optional

import numpy as np
from scipy import stats

import src.configuration as config
from src import constants as constants
from src.system.campaign import Campaign
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem, MystiqueHardThrottlingPacingSystem
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType


def generate_campaigns(n: int):
    campaigns = []
    for i in range(n):
        # run_period = random.randint(config.campaign_min_run_period, config.num_days_to_simulate)
        run_period = config.num_days_to_simulate
        # Sample daily budget for campaign
        daily_budget = math.exp(config.daily_budgets_log_distribution.rvs())
        # Generate bid distribution according to the sampled budget
        bids_distribution = generate_bid_distribution_for_budget(daily_budget)
        campaigns.append(Campaign(campaign_id=f'campaign_{i}',
                                  run_period=run_period,
                                  total_budget=daily_budget * run_period,
                                  bids_distribution=bids_distribution,
                                  max_bid=bids_distribution.mean() * config.max_bid_as_factor_of_bids_mean,
                                  targeting_groups={
                                      feature: set(
                                          np.random.choice(list(config.user_properties[feature].keys()),
                                                           size=num_target_values,
                                                           replace=False))
                                      for feature in config.user_properties
                                      if (num_target_values := random.randint(0, len(
                                          config.user_properties[feature].keys()))) > 0
                                  }))
    return campaigns


def generate_pacing_system(algorithm: constants.BudgetPacingAlgorithms) -> Optional[PacingSystemInterface]:
    if algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR:
        return MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR:
        return MystiquePacingSystem(TargetSpendStrategyType.NON_LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR_HARD_THROTTLING:
        return MystiqueHardThrottlingPacingSystem(TargetSpendStrategyType.LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR_HARD_THROTTLING:
        return MystiqueHardThrottlingPacingSystem(TargetSpendStrategyType.NON_LINEAR)
    elif algorithm is None:
        return None
    else:
        raise Exception(f'Unsupported budget pacing algorithm: {algorithm}')


def generate_bid_distribution_for_budget(daily_budget: float) -> stats.rv_continuous:
    # The following buckets have been defined according to approximated distributions of real data.
    if daily_budget < config.medium_budget_range_min_value:
        # Low budgets bid distribution
        return config.bids_distribution_low_budget
    elif config.medium_budget_range_min_value <= daily_budget < config.high_budget_range_min_value:
        # Medium budgets bid distribution
        return config.bids_distribution_medium_budget
    else:
        # High budgets bid distribution
        return config.bids_distribution_high_budget
