# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import math
import random
from typing import Optional

from scipy import stats
from dataclasses import dataclass

import src.configuration as config
from src import constants as constants
from src.system.campaign import Campaign
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem, MystiqueHardThrottlingPacingSystem
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType


@dataclass
class CampaignConfiguration:
    run_period: int
    total_budget: float
    bids_distribution: stats.rv_continuous
    max_bid: float
    targeting_groups: dict


def generate_campaign_configuration() -> CampaignConfiguration:
    run_period = config.num_days_to_simulate
    # Sample daily budget for campaign
    daily_budget = math.exp(config.daily_budgets_log_distribution.rvs())
    # Generate bid distribution according to the sampled budget
    bids_distribution = generate_bid_distribution_for_budget(daily_budget)
    return CampaignConfiguration(run_period=run_period,
                                 total_budget=daily_budget * run_period,
                                 bids_distribution=bids_distribution,
                                 max_bid=bids_distribution.mean() * config.max_bid_factor_of_bids_mean,
                                 targeting_groups={
                                     feature: set(
                                         random.sample(list(config.user_properties[feature].keys()),
                                                       k=num_target_values))
                                     for feature in config.user_properties
                                     if (num_target_values := random.randint(0, len(
                                         config.user_properties[feature].keys()))) > 0
                                 })


def generate_campaigns(n: int):
    # set random seed to get consistent campaigns across experiments
    config.daily_budgets_log_distribution.random_state = config.campaign_generation_seed_value
    random.seed(config.campaign_generation_seed_value)
    campaigns = []
    for i in range(n):
        campaign_config = generate_campaign_configuration()
        campaigns.append(Campaign(campaign_id=f'campaign_{i}',
                                  run_period=campaign_config.run_period,
                                  total_budget=campaign_config.total_budget,
                                  bids_distribution=campaign_config.bids_distribution,
                                  max_bid=campaign_config.max_bid,
                                  targeting_groups=campaign_config.targeting_groups))
    return campaigns


def generate_pacing_system(algorithm: constants.BudgetPacingAlgorithms) -> Optional[PacingSystemInterface]:
    if algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR:
        print('Running Mystique Linear')
        return MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR:
        print('Running Mystique Non-Linear')
        return MystiquePacingSystem(TargetSpendStrategyType.NON_LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR_HARD_THROTTLING:
        print('Running Mystique Linear Hard Throttling')
        return MystiqueHardThrottlingPacingSystem(TargetSpendStrategyType.LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR_HARD_THROTTLING:
        print('Running Mystique Non-Linear Hard Throttling')
        return MystiqueHardThrottlingPacingSystem(TargetSpendStrategyType.NON_LINEAR)
    elif algorithm is None:
        print('Running without budget pacing')
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
