# This script generates graphs with campaigns' target/actual spend, together with the value of the pacing signal
import csv
import datetime
import sys

import matplotlib.pyplot as plt

import src.system.budget_pacing.mystique.mystique_constants as mystique_constants
from src import configuration as config
from src import constants as constants

csv.field_size_limit(sys.maxsize)

STATS_FILE_PATH = '../output/without-lifetime/Camp100-UntrackedF1-Traffic3000-0.6-Seed123/BudgetPacingAlgorithms.MYSTIQUE_LINEAR.csv'

if __name__ == '__main__':
    # n_days = 7
    # auctions_each_minute = []
    # auctions_mean_each_minute = []
    # for i in range(config.num_iterations_per_day * n_days):
    #     auctions_each_minute.append(Marketplace._sample_current_num_of_auctions())
    #     auctions_mean_each_minute.append(Marketplace._calculate_current_mean_num_of_auctions())
    #     Clock.advance()
    # plt.plot(range(config.num_iterations_per_day * n_days), auctions_each_minute, label='Number of Auctions')
    # plt.plot(range(config.num_iterations_per_day * n_days), auctions_mean_each_minute, label='Mean number of Auctions')
    # plt.xticks([i*config.num_iterations_per_day for i in range(n_days)], [f'Day{i+1}' for i in range(n_days)])
    # plt.legend()
    # plt.show()
    # exit()

    with open(STATS_FILE_PATH, 'r') as f:
        dict_reader = csv.DictReader(f)
        campaigns_stats_list = list(dict_reader)
    # Choose a campaign
    campaign_stats = campaigns_stats_list[60]
    # Plotting
    day_ended = config.num_days_to_simulate-1 if campaign_stats[constants.FIELD_DAY_ENDED] == '' else int(campaign_stats[constants.FIELD_DAY_ENDED])
    run_period = day_ended - int(campaign_stats[constants.FIELD_DAY_STARTED]) + 1
    # defining the x-axis of our plots
    time_as_dates = [datetime.datetime.fromtimestamp(ts * 60, tz=datetime.timezone.utc) for ts in
                     range(config.num_iterations_per_day * run_period)]

    fig, axs = plt.subplots(2, 1)
    # Plotting Spend
    spend_history = eval(campaign_stats[mystique_constants.FIELD_SPEND_HISTORY])
    daily_budget = eval(campaign_stats[constants.FIELD_DAILY_BUDGET])
    target_spend_history = eval(campaign_stats[mystique_constants.FIELD_TARGET_SPEND_HISTORY])

    # represent each entry of each day an accumulated sum of the spend until that moment of the day
    spend_history_accumulated = [[sum(sublist[: i + 1]) for i in range(len(sublist))] for sublist in spend_history]
    # flatten spend history into a single list
    spend_history_flat = [item for sublist in spend_history_accumulated for item in sublist]
    axs[0].plot(time_as_dates, spend_history_flat, label='Spend')
    target_spend_history_flat = [item*daily_budget for sublist in target_spend_history for item in sublist]
    # since we store the target spend history on hourly basis, we draw the target spend of an hour as a value of the
    # last minute (index 59) of that hour.
    axs[0].plot(time_as_dates[59::60], target_spend_history_flat, label='Target Spend')
    axs[0].plot(time_as_dates, [daily_budget] * len(time_as_dates), label='Budget')

    axs[0].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m\n%H:%M'))
    axs[0].set_title('Spend History')
    axs[0].legend()

    # Plotting Pacing Signal
    pacing_signal_history = eval(campaign_stats[mystique_constants.FIELD_PACING_SIGNAL_HISTORY])
    # flatten pacing signal history into a single list
    pacing_history_flat = [item for sublist in pacing_signal_history for item in sublist]
    axs[1].plot(time_as_dates, pacing_history_flat, label='PS')

    axs[1].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d/%m\n%H:%M'))
    axs[1].set_title('Pacing Signal History')
    axs[1].legend()
    plt.tight_layout()
    plt.show()
