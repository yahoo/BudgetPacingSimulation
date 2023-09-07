import csv

import src.configuration as config
from src import system_generation_utils
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem

OUTPUT_FOLDER_PATH = '../output'
OUTPUT_FILE_PATH = f'{OUTPUT_FOLDER_PATH}/simulation_statistics.csv'


if __name__ == '__main__':
    campaigns = system_generation_utils.generate_campaigns(config.num_campaigns)
    pacing_system = system_generation_utils.generate_pacing_system(config.pacing_algorithm)
    serving_system = ServingSystem(pacing_system=pacing_system, tracked_campaigns=campaigns)
    marketplace = Marketplace(serving_system=serving_system,
                              auction_type=config.auction_type,
                              traffic_mean_cos_wave=config.traffic_mean_cos_wave)
    # Run
    for _ in range(config.num_days_to_simulate * config.num_iterations_per_day):
        marketplace.run_iteration()
    # Write per-campaign metrics to csv file
    with open(OUTPUT_FILE_PATH, 'w') as f:
        if not config.output_only_summarized_statistics:
            # Get the per-campaign output metrics as rows
            statistics_per_campaign = serving_system.get_statistics_per_campaign_csv_rows()
            all_fields = statistics_per_campaign[0].keys()
            w = csv.DictWriter(f, fieldnames=all_fields)
            w.writeheader()
            w.writerows(statistics_per_campaign)
        # Append global statistics to csv file
        global_statistics = serving_system.get_global_statistics_csv_rows()
        w = csv.DictWriter(f, fieldnames=global_statistics[0].keys())
        w.writeheader()
        w.writerows(global_statistics)


