# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

# This script creates a summary of a simulation's result by combining the Overall values of the different pacing systems
# The script reads the values defined in the configuration.py file generates a summary for that configuration's results
import csv
import os
import sys

import src.configuration as config

csv.field_size_limit(sys.maxsize)

OUTPUT_FOLDER_PATH = '../output'
trial_folder = (f'{OUTPUT_FOLDER_PATH}/'
                    f'Camp{config.num_campaigns}-UntrackedF{config.factor_untracked_bids}-'
                    f'Traffic{config.traffic_mean_cos_wave.dc}-{config.traffic_mean_cos_wave.amplitude}-'
                    f'Seed{config.campaign_generation_seed_value}')

OUTPUT_SUMMARY_FILE_PATH = f'{trial_folder}/summary-Camp{config.num_campaigns}-F{config.factor_untracked_bids}-' \
                           f'T{config.traffic_mean_cos_wave.dc}-Seed{config.campaign_generation_seed_value}.csv'

if __name__ == '__main__':
    if os.path.exists(OUTPUT_SUMMARY_FILE_PATH):
        exit()

    keys = []
    row_by_system = {}
    for stat_file in os.listdir(path=trial_folder):
        with open(f'{trial_folder}/{stat_file}', 'r') as f:
            csv_reader = csv.reader(f)
            rows_list = list(csv_reader)
        alg = stat_file.split('.')[-2]
        row_by_system[alg] = rows_list[-1]
        if not keys:
            keys = rows_list[-config.num_days_to_simulate-2]
    keys[0] = 'System'
    # Write to output
    with open(OUTPUT_SUMMARY_FILE_PATH, 'w') as f:
        w = csv.writer(f)
        w.writerow(keys)
        for pacing_system in row_by_system:
            row_by_system[pacing_system][0] = pacing_system
            w.writerow(row_by_system[pacing_system])

