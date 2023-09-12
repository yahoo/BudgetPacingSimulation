import random
import unittest

import src.constants as constants
from src.constants import num_minutes_in_day
from src.system.auction import *
from src.system.budget_pacing.mystique import mystique_constants
from src.system.budget_pacing.mystique.mystique import MystiquePacingSystem
from src.system.budget_pacing.mystique.target_slope import TargetSpendStrategyType
from src.system.budget_pacing.pacing_system_interface import PacingSystemInterface
from src.system.campaign import *
from src.system.serving_system import ServingSystem
from tests.tests_utils import create_campaigns


class TestServingSystem(unittest.TestCase):
    def setUp(self):
        Clock.reset()

    def test_add_campaign(self):
        serving_system = ServingSystem(tracked_campaigns=[])
        campaign = Campaign(campaign_id=f'campaign', total_budget=1000, run_period=7)
        serving_system.add_campaign(campaign)
        self.assertTrue(campaign in serving_system.tracked_campaigns.values(),
                        "expected added campaign to be inside tracked campaigns")
        self.assertRaises(Exception, serving_system.add_campaign, campaign,
                          "should have raised an exception preventing insertion of duplicate elements")

    def test_simple_auction(self):
        num_campaigns = 5
        campaigns = create_campaigns(num_campaigns)
        serving_system = ServingSystem(tracked_campaigns=campaigns)
        bids = serving_system.get_bids(AuctionFP({}))
        self.assertEqual(len(bids), num_campaigns + config.factor_untracked_bids*num_campaigns, "wrong number of generated bids")
        for c in campaigns:
            # assert that each campaign has a bid in the list of bids
            self.assertTrue(c.id in [bid.campaign_id for bid in bids], "no bid exists for campaign")
        # simulating a winning campaign and updating its budget
        campaign_id = campaigns[0].id
        auction_winner = AuctionWinner(bid=Bid(campaign_id, 10), payment=10)
        serving_system.update_winners([auction_winner])
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].spent_today(), auction_winner.payment,
                         "today's spend of the winning campaign should reflect the auction won")
        self.assertEqual(serving_system.tracked_campaigns[campaign_id].num_auctions_won_today(), 1,
                         "the number of auctions won today by the campaign should reflect the auction won")

    def test_with_mock_budget_pacing_always_zero_ps(self):
        config.factor_untracked_bids = 0
        num_campaigns = 5
        campaigns = create_campaigns(num_campaigns)
        serving_system = ServingSystem(pacing_system=MockPacingSystem(pacing_signal=0),
                                       tracked_campaigns=campaigns)
        bids = serving_system.get_bids(AuctionFP({}))
        self.assertEqual(len(bids), 0, "expected list of bids to be empty when all bids are zero")

    def test_campaign_budget_depletion(self):
        # Creating a single campaign, depleting its budget,
        # and checking that the serving system no longer gets bids from it.
        config.factor_untracked_bids = 0
        campaign_daily_budget = config.campaign_minimal_bid
        campaign_run_period = 2
        campaign = Campaign(campaign_id='campaign', total_budget=campaign_daily_budget * campaign_run_period,
                            run_period=campaign_run_period,
                            bids_distribution=stats.uniform(loc=campaign_daily_budget, scale=0.05))
        serving_system = ServingSystem(tracked_campaigns=[campaign])
        bids = serving_system.get_bids(AuctionFP({}))
        self.assertEqual(len(bids), 1, "expected to get a bid from a single campaign")
        # simulating a win for the campaign which depletes its budget
        auction_winner = AuctionWinner(bid=Bid(campaign.id, bids[0].amount),
                                       payment=bids[0].amount)
        serving_system.update_winners([auction_winner])
        self.assertGreaterEqual(campaign.spent_today(), campaign.daily_budget)
        self.assertGreater(campaign.spent_today(), campaign.daily_budget)
        bids_after_depletion = serving_system.get_bids(AuctionFP({}))
        self.assertEqual(bids_after_depletion, [],
                         "expected list of bids to be empty after depleting campaign's budget")

    def test_with_mystique_budget_pacing(self):
        config.factor_untracked_bids = 0
        campaign = create_campaigns(1)[0]
        mystique = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
        serving_system = ServingSystem(pacing_system=mystique,
                                       tracked_campaigns=[campaign])
        # check that campaigns were added to Mystique
        self.assertTrue(campaign.id in mystique.mystique_tracked_campaigns,
                        "campaign was not added to pacing system")
        bids = serving_system.get_bids(AuctionFP({}))
        self.assertEqual(len(bids), 1)
        bid = bids[0]
        self.assertGreater(bid.amount, 0)
        payment = bid.amount
        serving_system.update_winners([AuctionWinner(bid=bid, payment=payment)])
        serving_system.end_iteration()
        # check that the campaign itself was updated
        self.assertEqual(campaign.spent_today(), payment, "expected campaign spend to be equal to payment")
        # check that the tracked campaign in mystique was updated with the spend of the campaign
        mystique_tracked_campaign = mystique.mystique_tracked_campaigns.get(campaign.id)
        self.assertEqual(len(mystique_tracked_campaign.today_spend), 1,
                         "expected mystique tracked campaign to contain a single entry in its daily spend list")
        # simulate days passed
        for _ in range(num_minutes_in_day * 2):
            Clock.advance()
            serving_system.end_iteration()
        self.assertEqual(mystique_tracked_campaign.spend_history[0][0], payment,
                         "expected mystique tracked campaign to contain an entry equal to the amount it payed "
                         "during the last iteration in its daily spend list")
        # check that the CampaignStatistics history were updated
        self.assertEqual(campaign.stats.spend_history[0][0], payment,
                         "expected campaign spend history to include payment")

    def test_targeting_groups(self):
        config.num_untracked_bids = 0
        campaign = create_campaigns(1)[0]
        serving_system = ServingSystem(pacing_system=None, tracked_campaigns=[campaign])
        # test without targeting groups
        bids = serving_system.get_bids(auction=AuctionFP({}))
        self.assertEqual(len(bids), 1, "expected to see a single bid")
        # test with a targeting group different from that of the auction
        property_name = 'Property1'
        # set targeting group for the campaign
        campaign._targeting_groups = {property_name: {4, 5, 6}}
        bids = serving_system.get_bids(AuctionFP({property_name: 1}))
        self.assertEqual(len(bids), 0, "expected to see no bids for the auction")
        # check that all valid values for the target property produce a bid from the campaign
        for target_value in campaign._targeting_groups[property_name]:
            bids = serving_system.get_bids(AuctionFP({property_name: target_value}))
            self.assertEqual(len(bids), 1, "expected to see a single bid")
        # test a property with a different name than the target property
        bids = serving_system.get_bids(AuctionFP({f'{property_name}_different': 4}))
        self.assertEqual(len(bids), 0, "expected to see no bids for the auction")

    def test_global_statistics_with_mystique(self):
        num_days = 2
        config.num_untracked_bids = 0
        num_campaigns = 5
        campaigns = [Campaign(campaign_id=f'campaign_{i}', total_budget=1000, run_period=7, max_bid=1)
                     for i in range(num_campaigns)]
        mystique = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
        serving_system = ServingSystem(pacing_system=mystique,
                                       tracked_campaigns=campaigns)
        for _ in range(num_minutes_in_day * num_days):
            auction_winner = AuctionWinner(bid=Bid(random.choice([campaign.id for campaign in campaigns]), 0.01),
                                           payment=0.005)
            serving_system.update_winners([auction_winner])
            serving_system.end_iteration()
            Clock.advance()
        global_statistics = serving_system.get_global_statistics_csv_rows()
        self.assertEqual(len(global_statistics), num_days + 1, "expected number of rows to be equal to "
                                                               "number of days + 1, which includes a final overall row")
        daily_fields = [
            constants.FIELD_DAY_ID,
            constants.FIELD_CPM,
            constants.FIELD_NUM_OVER_BUDGET_CAMPAIGNS,
            constants.FIELD_NUM_WINS,
            constants.FIELD_OVERSPEND,
            constants.FIELD_SPEND,
            mystique_constants.FIELD_NUM_BC_CAMPAIGNS,
            mystique_constants.FIELD_NUM_BC_CAMPAIGNS
        ]
        for day in range(num_days):
            for field in daily_fields:
                self.assertIn(field, global_statistics[day])
                self.assertTrue(isinstance(global_statistics[day][field], float) or
                                isinstance(global_statistics[day][field], int))
        # Check that the last row includes overall statistics
        self.assertEqual(global_statistics[-1][constants.FIELD_DAY_ID], constants.OVERALL_STATISTICS_ROW_NAME)
        overall_stats_fields = [
            constants.FIELD_CPM,
            constants.FIELD_OVERSPEND,
            constants.FIELD_SPEND,
            constants.FIELD_NUM_WINS
        ]
        for field in overall_stats_fields:
            self.assertIn(field, global_statistics[-1])
            self.assertTrue(isinstance(global_statistics[-1][field], float) or
                            isinstance(global_statistics[-1][field], int),
                            f'expected value {global_statistics[-1][field]} to be int or float')

    def test_statistics_with_mystique_campaign_starts_midday(self):
        mystique = MystiquePacingSystem(TargetSpendStrategyType.NON_LINEAR)
        serving_system = ServingSystem(pacing_system=mystique)
        starting_minute = 200
        # run for {starting_minute} iterations, then insert the campaign
        for _ in range(starting_minute):
            serving_system.end_iteration()
            Clock.advance()
        campaign = Campaign(campaign_id='campaign_1', total_budget=10000, run_period=7, max_bid=0.2)
        serving_system.add_campaign(campaign)
        # run the serving system with the campaign
        for _ in range(num_minutes_in_day - starting_minute):
            auction_winner = AuctionWinner(bid=Bid(campaign_id=campaign.id, amount=0.01), payment=0.005)
            serving_system.update_winners([auction_winner])
            serving_system.end_iteration()
            Clock.advance()
        # check campaign's statistics
        daily_stats_fields = [constants.FIELD_CPM, constants.FIELD_BUDGET_UTILIZATION, constants.FIELD_OVERSPEND]
        stats_per_campaign_list = serving_system.get_statistics_per_campaign_csv_rows()
        # validate structure correctness of statistics
        self.assertEqual(len(stats_per_campaign_list), 1)
        campaign_stats = stats_per_campaign_list[0]
        for field in daily_stats_fields:
            self.assertEqual(len(campaign_stats[field]), 1)
            for value_in_day in campaign_stats[field]:
                self.assertGreaterEqual(value_in_day, 0, "expected value in a day to be >= 0")

    def test_statistics_with_mystique(self):
        num_days = 2
        config.factor_untracked_bids = 0
        num_campaigns = 5
        campaigns = create_campaigns(num_campaigns)
        mystique = MystiquePacingSystem(TargetSpendStrategyType.LINEAR)
        serving_system = ServingSystem(pacing_system=mystique,
                                       tracked_campaigns=campaigns)
        for _ in range(num_minutes_in_day * num_days):
            # simulate an auction
            auction_winner = AuctionWinner(bid=Bid(random.choice([campaign.id for campaign in campaigns]), 0.01),
                                           payment=0.005)
            serving_system.update_winners([auction_winner])
            Clock.advance()
            serving_system.end_iteration()
        stats_per_campaign_list = serving_system.get_statistics_per_campaign_csv_rows()
        # validate structure correctness of statistics
        self.assertEqual(len(stats_per_campaign_list), num_campaigns, "length of list of statistics should be "
                                                                      "equal to the total number of tracked campaigns.")
        campaign_stats = stats_per_campaign_list[0]
        self.assertIsNotNone(campaign_stats)
        # check that basic statistics exist
        daily_stats_fields = [constants.FIELD_CPM,
                              constants.FIELD_BUDGET_UTILIZATION, constants.FIELD_OVERSPEND]
        basic_stats_fields = [constants.FIELD_CAMPAIGN_ID, constants.FIELD_DAY_STARTED, constants.FIELD_DAY_ENDED,
                              constants.FIELD_DAILY_BUDGET,
                              constants.FIELD_NUM_WINS] + daily_stats_fields
        # check that all basic statistics exist
        for field in basic_stats_fields:
            self.assertTrue(field in campaign_stats, f'basic statistic {field} is missing.')
        # check that statistics which have a single entry per day are indeed num_days long
        for field in daily_stats_fields:
            self.assertEqual(len(campaign_stats[field]), num_days)
            for value_in_day in campaign_stats[field]:
                if value_in_day is None:
                    # CPM can be None
                    continue
                self.assertGreaterEqual(value_in_day, 0, "expected value in a day to be >= 0")
        # check expected values for specific basic statistics
        self.assertEqual(len(campaign_stats[constants.FIELD_NUM_WINS]), num_days)
        self.assertEqual(len(campaign_stats[constants.FIELD_NUM_WINS][0]),
                         config.num_win_entries_per_day)
        self.assertEqual(campaign_stats[constants.FIELD_DAY_STARTED], 0)
        self.assertEqual(campaign_stats[constants.FIELD_DAILY_BUDGET], campaigns[0].daily_budget)
        # check that mystique statistics exist
        mystique_stats_fields = [mystique_constants.FIELD_SPEND_HISTORY,
                                 mystique_constants.FIELD_PACING_SIGNAL_HISTORY,
                                 mystique_constants.FIELD_TARGET_SPEND_HISTORY,
                                 mystique_constants.FIELD_TARGET_SLOPE_HISTORY]
        for field in mystique_stats_fields:
            self.assertTrue(field in campaign_stats, f'mystique statistic {field} is missing.')
            self.assertEqual(len(campaign_stats[field]), num_days)
            self.assertGreater(len(campaign_stats[field][0]), 0)


class MockPacingSystem(PacingSystemInterface):
    def __init__(self, pacing_signal=0):
        self.pacing_signal = pacing_signal

    def add_campaign(self, campaign):
        pass

    def end_iteration(self, campaign_id, spend_since_last_iteration):
        pass

    def get_pacing_signal(self, campaign_id):
        return self.pacing_signal

    def get_pacing_statistics(self, campaign_id: str) -> dict[str, object]:
        pass

    def get_global_pacing_statistics(self) -> dict[str, object]:
        pass


if __name__ == '__main__':
    unittest.main()
