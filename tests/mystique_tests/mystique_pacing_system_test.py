import unittest

from src.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.budget_pacing.mystique.mystique_tracked_campaign import MystiqueTrackedCampaign
import mystique_campaign_initialization
import src.budget_pacing.mystique.mystique_constants as mystique_constants


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
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.daily_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.pacing_signal_for_initialization, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.pacing_signal_for_initialization, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.pacing_signal_for_initialization, "last positive pacing signal initialization not correct")

        campaign = mystique_campaign_initialization.instance_for_budget_above_threshold()
        self.mystique_linear.add_campaign(campaign)

        campaign_id = campaign.campaign_id
        self.assertTrue(campaign_id in self.mystique_linear.mystique_tracked_campaigns.keys(), "Campaign not added to Mystique's tracked campaigns")

        mystique_tracked_campaign = self.mystique_linear.mystique_tracked_campaigns[campaign_id]
        self.assertEqual(mystique_tracked_campaign.daily_budget, campaign.total_budget, "daily budget initialization not correct")
        self.assertEqual(mystique_tracked_campaign.ps, mystique_constants.max_ps, "pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.previous_ps, mystique_constants.max_ps, "previous pacing signal initialization not correct")
        self.assertEqual(mystique_tracked_campaign.last_positive_ps, mystique_constants.max_ps, "last positive pacing signal initialization not correct")



