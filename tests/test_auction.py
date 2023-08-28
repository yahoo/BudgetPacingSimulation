import random
import unittest
from src.system.auction import *


class TestAuctions(unittest.TestCase):
    def test_fp_auction(self):
        num_bids = 5
        max_bid = 20
        bids = []
        for i in range(num_bids):
            bids.append(Bid(f'campaign_{i}', random.randint(0, max_bid)))

        auction = AuctionFP(user_properties={})
        winners = auction.run(bids)
        self.assertIsNotNone(winners, "auctions winners list should not be None")
        self.assertEqual(len(winners), 1, "auction winners list should contain a single entry")
        self.assertEqual(winners[0].bid, max(bids))
        # adding a bid that is higher than all existing ones
        winning_campaign_id = 'campaign_winner'
        bids.append(Bid(winning_campaign_id, max_bid*2))
        winners = auction.run(bids)
        self.assertEqual(winners[0].bid.campaign_id, winning_campaign_id, "the newly added highest bid should have won")

    def test_fp_auction_no_bids(self):
        bids = []
        auction = AuctionFP(user_properties={})
        winners = auction.run(bids)
        self.assertIsNotNone(winners, "auctions winners list is None")
        self.assertEqual(len(winners), 0, "auction winners list should be empty")


if __name__ == '__main__':
    unittest.main()
