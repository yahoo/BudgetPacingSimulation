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
    output_metrics = serving_system.get_statistics_for_all_campaigns()
    # Write metrics to csv file
    with open(OUTPUT_FILE_PATH, 'w') as f:
        w = csv.DictWriter(f, fieldnames=output_metrics[0].keys())
        w.writeheader()
        w.writerows(output_metrics)

