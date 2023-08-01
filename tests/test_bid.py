import random
import unittest
from src.system.bid import *


class TestBids(unittest.TestCase):
    def test_max_min_comparison(self):
        n_bids = 5
        bids = []
        amounts = []
        for i in range(n_bids):
            amount = random.randint(0, 20)
            amounts.append(amount)
            bids.append(Bid(f'campaign_{i}', amount))
        self.assertEqual(max(amounts), max(bids).amount)
        self.assertEqual(min(amounts), min(bids).amount)

    def test_bids_equal(self):
        bid1 = Bid('bid1', 5)
        bid2 = Bid('bid2', 8)
        self.assertNotEqual(bid1, bid2, "bids from different campaigns should not be equal")
        bid2.campaign_id = bid1.campaign_id
        bid2.amount = bid1.amount
        self.assertEqual(bid1, bid2, "bids with same campaign_id and amount should be equal")


if __name__ == '__main__':
    unittest.main()
