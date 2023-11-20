# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import src.configuration as config
from scipy import stats
from src.system.campaign import Campaign


def create_campaigns(n):
    return [Campaign(campaign_id=f'campaign_{i}', total_budget=100000, run_period=7,
                     bids_distribution=stats.uniform(loc=config.campaign_minimal_bid, scale=0.05))
            for i in range(n)]
