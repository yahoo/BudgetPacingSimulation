from src.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
from src.campaign import Campaign


def instance_for_target_slope_test():
    return MystiqueTrackedCampaign(10)


def instance_for_mystique_test_init():
    return Campaign(0, 100, 10, 0.5, [])
