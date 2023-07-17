import unittest

from src.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
import mystique_campaign_initialization


class TestMystiquePacingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.mystique_linear = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)

    def testAddCampaign(self):
        campaign = mystique_campaign_initialization.instance_for_mystique_test_init()
        self.mystique_linear.add_campaign(campaign)

        campaign_id = campaign.campaign_id
        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(campaign.daily_budget, mystique_tracked_campaign.daily_budget, "daily budget initialization not correct")


