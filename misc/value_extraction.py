# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

# This script extracts the 'total value' metric for each campaign
import csv
import os
import sys

import src.system.budget_pacing.mystique.mystique_constants as mystique_constants
from src import constants as constants

csv.field_size_limit(sys.maxsize)

RESULTS_FOLDER_PATH = ''

n_days = 7

if __name__ == '__main__':
    for folder in list(os.listdir(RESULTS_FOLDER_PATH))[1:]:
        if not folder.startswith('Camp'):
            continue
        total_value_by_pacing = {}
        for stat_file in os.listdir(f'{RESULTS_FOLDER_PATH}/{folder}'):
            if not stat_file.endswith('.csv') or stat_file.startswith('summary'):
                continue
            print(folder)
            print(stat_file)
            with open(f'{RESULTS_FOLDER_PATH}/{folder}/{stat_file}', 'r') as f:
                dict_reader = csv.DictReader(f)
                campaigns_stats_list = list(dict_reader)
                output_file_path = f'{RESULTS_FOLDER_PATH}/{folder}/{stat_file.removesuffix(".csv") + "_new.csv"}'
                if os.path.exists(output_file_path):
                    continue
                total_value_per_day = [0] * n_days
                for campaign in campaigns_stats_list[:100]:
                    total_value = 0
                    daily_budget = eval(campaign['Daily Budget'])
                    if stat_file.startswith('No_Pacing'):
                        budget_util = eval(campaign['Budget Utilization'])
                    else:
                        spend_history = eval(campaign['Spend History'])
                        ps_history = eval(campaign.get('Pacing Signal History'))

                    for day in range(n_days):
                        if stat_file.startswith('No_Pacing'):
                            total_value += budget_util[day] * daily_budget
                            total_value_per_day[day] += budget_util[day] * daily_budget
                            continue
                        for minute in range(constants.num_minutes_in_day):
                            if spend_history[day][minute] == 0:
                                continue
                            if stat_file.removesuffix('.csv').endswith('soft'):
                                ps = ps_history[day][
                                    minute - 1] if minute > 0 else mystique_constants.max_ps if daily_budget > mystique_constants.min_daily_budget_for_high_initialization else mystique_constants.pacing_signal_for_initialization
                                total_value += spend_history[day][minute] / ps_history[day][minute - 1]
                                # the index offset in ps_history is because of how the ps history is stored
                                total_value_per_day[day] += spend_history[day][minute] / ps_history[day][minute - 1]
                            elif stat_file.removesuffix('.csv').endswith('hard'):
                                total_value += spend_history[day][minute]
                                total_value_per_day[day] += spend_history[day][minute]
                            else:
                                raise 'ERROR'
                    campaign['Total Value'] = total_value
                # with open(output_file_path, 'w') as new_f:
                #     all_fields = campaigns_stats_list[0].keys()
                #     w = csv.DictWriter(new_f, fieldnames=all_fields)
                #     w.writeheader()
                #     campaigns_stats_list[100]['Total Value'] = 'Total Value'
                #     for day in range(n_days):
                #         campaigns_stats_list[101 + day]['Total Value'] = total_value_per_day[day]
                #     campaigns_stats_list[-1]['Total Value'] = sum(total_value_per_day)
                #     w.writerows(campaigns_stats_list)
            total_value_by_pacing[stat_file.removesuffix('.csv')] = sum(total_value_per_day)
        summary_file_name = \
        list(filter(lambda name: name.startswith('summary') and name.endswith('.csv'), os.listdir(f'{RESULTS_FOLDER_PATH}/{folder}')))[0]
        with open(f'{RESULTS_FOLDER_PATH}/{folder}/{summary_file_name}', 'r') as summary_f:
            dict_reader = csv.DictReader(summary_f)
            rows = list(dict_reader)
            for row in rows:
                row['Total Value'] = total_value_by_pacing[row['System']]
        with open(f'{RESULTS_FOLDER_PATH}/{folder}/{summary_file_name}', 'w') as summary_new:
            all_fields = rows[0].keys()
            w = csv.DictWriter(summary_new, fieldnames=all_fields)
            w.writeheader()
            w.writerows(rows)
