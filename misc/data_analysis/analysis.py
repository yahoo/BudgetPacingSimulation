import csv
import sys
import math
import random

import matplotlib.pyplot as plt
import numpy as np
import scipy
import src.system.budget_pacing.mystique.mystique_constants as mystique_constants
from src import configuration as config
from src import constants as constants

csv.field_size_limit(sys.maxsize)

BID_DATA_FILE_PATH = 'campaign-bid-distribution.csv'
BUDGET_DATA_FILE_PATH = 'bidsPerBudgetForAnalysis.csv'


def plot_bid_distributions_mean(bids_by_id: list[(str, float)]):
    histogram = {}
    for bid_by_id in bids_by_id:
        histogram[bid_by_id[0]] = histogram.get(bid_by_id[0], 0) + 1

    dist_mean_by_campaign = {}
    dist_var_by_campaign = {}
    for campaign_id in histogram.copy():
        if histogram[campaign_id] < 250:
            # drop campaigns with a low number of bids
            histogram.pop(campaign_id)
            continue
        campaign_bids_log = [math.log(entry[1]) for entry in bids_by_id if entry[0] == campaign_id]
        res = scipy.stats.fit(dist=scipy.stats.norm, data=campaign_bids_log,
                              bounds=[(-50, 50), (0, 50)])
        dist_mean_by_campaign[campaign_id] = res.params.loc
        dist_var_by_campaign[campaign_id] = res.params.scale

    plt.title(r'Distribution of $\mu$ and $\sigma$ for the LogNorm distributions of bids')
    # Plot distribution of mean (mu)
    plt.subplot(1, 2, 1)
    res = scipy.stats.fit(dist=scipy.stats.norm, data=list(dist_mean_by_campaign.values()),
                          bounds=[(-50, 50), (0, 50)])
    print('mean distribution', res)
    ax = res.plot()
    ax.set_xlabel(r'$\mu$')
    # Plot distribution of variance (sigma)
    plt.subplot(1, 2, 2)
    res = scipy.stats.fit(dist=scipy.stats.norm, data=list(dist_var_by_campaign.values()),
                          bounds=[(-50, 50), (0, 50)])
    print('variance distribution', res)
    ax = res.plot()
    ax.set_xlabel(r'$\sigma$')
    # plt.tight_layout()
    plt.show()


def plot_bid_distributions_random_campaigns(bids_by_id: list[(str, float)]):
    histogram = {}
    for bid_by_id in bids_by_id:
        histogram[bid_by_id[0]] = histogram.get(bid_by_id[0], 0) + 1

    for campaign_id in histogram.copy():
        if histogram[campaign_id] < 300:
            # drop campaigns with a low number of bids
            histogram.pop(campaign_id)

    clean_bids = [(line['campaign_id'], float(line['bid'])) for line in campaigns_stats_list]

    chosen_campaigns = random.sample(histogram.keys(), 9)
    for i in range(len(chosen_campaigns)):
        plt.subplot(3, 3, i + 1)
        chosen_campaign_bids_log = [math.log(entry[1]) for entry in clean_bids if entry[0] == chosen_campaigns[i]]
        res = scipy.stats.fit(dist=scipy.stats.norm, data=chosen_campaign_bids_log,
                              bounds=[(-50, 50), (0, 50)])
        print(res)
        ax = res.plot()
        ax.set_xlabel('')
        # ax.set_xlabel('ln(bid)')
    # plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # with open(BID_DATA_FILE_PATH, 'r') as f:
    #     dict_reader = csv.DictReader(f)
    #     campaigns_stats_list = list(dict_reader)
    # plot_bid_distributions_mean(bids_by_id=[(line['campaign_id'], float(line['bid']))
    #                                         for line in campaigns_stats_list
    #                                         # ignore entries with extremely large bids
    #                                         if float(line['bid']) < 100])
    with open(BUDGET_DATA_FILE_PATH, 'r') as f:
        dict_reader = csv.DictReader(f)
        data_list = list(dict_reader)
    # data = set((line['campaign_id'], budget) for line in data_list if (budget := float(line['budget'])) < 10000 and budget > 0)
    data = set((float(line['bid']), budget, line['campaign_id']) for line in data_list if (budget := float(line['budget'])) > 0)
    # budget_per_campaign = {}
    # for line in data:
    #     campaign_id = line[2]
    #     campaign_budget = line[1]
    #     if campaign_id not in budget_per_campaign:
    #         budget_per_campaign[campaign_id] = campaign_budget
    budgets = [budget for (_, budget, _) in data]
    # print(len(budgets))
    # print(len(budget_per_campaign.keys()))
    # res = scipy.stats.fit(dist=scipy.stats.norm, data=[math.log(budget) for budget in budget_per_campaign.values()], bounds=[(-5, 10)])
    # print(res)
    # res.plot()
    # plt.show()
    # exit()

    # budget_ranges = [(0, 50), (50, 100), (100, 150),
    #                  (150, 200), (200, 300), (300, 400),
    #                  (400,500), (500, 1000), (1000, math.inf)]
    budget_ranges = [(0, 100), (100, 200), (200, math.inf)]
    bids_by_budget_range = {
        budget_range: [] for budget_range in budget_ranges
    }
    for line in data:
        bid = line[0]
        budget = line[1]
        campaign = line[2]
        budget_range = [(low, high) for (low, high) in budget_ranges if low <= budget < high][0]
        bids_by_budget_range[budget_range].append((bid, campaign))

    for (i, (budget_range, bids)) in enumerate(bids_by_budget_range.items()):
        plt.subplot(3, 1, i + 1)
        # chosen_bids_log = [math.log(entry[0]) for entry in bids_by_budget_range[budget_range]]
        chosen_bids = [entry[0] for entry in bids_by_budget_range[budget_range]]
        res = scipy.stats.fit(dist=scipy.stats.lognorm, data=chosen_bids,
                              # bounds=[(1, 4), (0, 0.0001), (math.exp(-10), math.exp(-6))])
                              bounds=[(1, 4)])
        print(res)
        ax = res.plot()
        ax.get_legend().remove()
        ax.set_xlabel(rf'Normal($\mu$={res.params.loc:.3}, $\sigma$={res.params.scale:.3})')
        ax.set_title(f'Budget Range:{budget_range}\n#Bids={len(bids)}, #Campaigns={len(set((campaign := entry[1]) for entry in bids_by_budget_range[budget_range]))}')
    plt.tight_layout()
    plt.show()


