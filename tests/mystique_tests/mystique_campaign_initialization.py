import tests.test_utils as test_utils
from src.system.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
from src.system.campaign import Campaign
import src.system.budget_pacing.mystique.mystique_constants as mystique_constants


def instance_for_target_slope_test():
    return MystiqueTrackedCampaign(10)


def instance_for_mystique_test_init(campaign_id: str):
    return Campaign(campaign_id, 100, 10, 0.5, test_utils.all_targeting_groups)


def instance_for_budget_above_threshold(campaign_id: str):
    return Campaign(campaign_id, mystique_constants.min_daily_budget_for_high_initialization + 1, 1, 0.5,
                    test_utils.all_targeting_groups)
