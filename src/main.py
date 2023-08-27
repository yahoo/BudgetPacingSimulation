from src import system_generation_utils
import src.configuration as config
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem
import csv

OUTPUT_FOLDER_PATH = '../output'
OUTPUT_FILE_PATH = f'{OUTPUT_FOLDER_PATH}/simulation_statistics.csv'


if __name__ == '__main__':
    campaigns = system_generation_utils.generate_campaigns(config.num_campaigns)
    pacing_system = system_generation_utils.generate_pacing_system(config.pacing_algorithm)
    serving_system = ServingSystem(pacing_system=pacing_system, tracked_campaigns=campaigns)
    marketplace = Marketplace(serving_system=serving_system)
    # Run
    for _ in range(config.num_days_to_simulate * config.num_iterations_per_day):
        marketplace.run_iteration()
    # Get output metrics as rows
    output_statistics = serving_system.get_statistics_for_all_campaigns()
    # Write metrics to csv file
    with open(OUTPUT_FILE_PATH, 'w') as f:
        all_fields = output_statistics[0].keys()
        w = csv.DictWriter(f, fieldnames=all_fields)
        w.writeheader()
        w.writerows(output_statistics)
