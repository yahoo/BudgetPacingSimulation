import random

from src.configuration import *
from src.system.campaign import Campaign


def generate_campaigns(n: int):
    return [Campaign(campaign_id=f'campaign_{i}',
                     total_budget=random.uniform(campaign_min_budget, campaign_max_budget),
                     run_period=random.randint(campaign_min_run_period, campaign_max_run_period),
                     max_bid=random.uniform(campaign_minimal_max_bid, campaign_maximal_max_bid))
            for i in range(n)]
