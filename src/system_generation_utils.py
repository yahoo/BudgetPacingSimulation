import random
from typing import Optional

import src.configuration as config
import src.constants as constants
from src.system.campaign import Campaign
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType


def generate_campaigns(n: int):
    return [Campaign(campaign_id=f'campaign_{i}',
                     total_budget=random.uniform(config.campaign_min_budget, config.campaign_max_budget),
                     run_period=random.randint(config.campaign_min_run_period, config.campaign_max_run_period),
                     max_bid=random.uniform(config.campaign_minimal_max_bid, config.campaign_maximal_max_bid))
            for i in range(n)]


def generate_pacing_system(algorithm: constants.BudgetPacingAlgorithms) -> Optional[PacingSystemInterface]:
    if algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_LINEAR:
        return MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
    elif algorithm == constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR:
        return MystiquePacingSystem(TargetSpendStrategyType.NON_LINEAR)
    elif algorithm is None:
        return None
    else:
        raise Exception(f'Unsupported budget pacing algorithm: {algorithm}')

