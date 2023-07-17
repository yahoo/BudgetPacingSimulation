from src.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
from src.campaign import Campaign
import src.budget_pacing.mystique.mystique_constants as mystique_constants


def instance_for_target_slope_test():
    return MystiqueTrackedCampaign(10)


def instance_for_mystique_test_init():
    return Campaign(0, 100, 10, 0.5, [])


def instance_for_budget_above_threshold():
    return Campaign(1, mystique_constants.min_daily_budget_for_high_initialization + 1, 1, 0.5, [])
