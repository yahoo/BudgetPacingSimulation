from src import system_generation_utils
import src.configuration as config
from src.system.marketplace import Marketplace
from src.system.serving_system import ServingSystem
import csv
import time

OUTPUT_FOLDER_PATH = '../output'
OUTPUT_FILE_PATH = f'{OUTPUT_FOLDER_PATH}/simulation_statistics.csv'


def get_miliseconds(start, end):
    return (end - start) * 10 ** 3

def get_seconds(start,end):
    ms = get_miliseconds(start,end)
    return ms/1000

def get_minutes(start,end):
    s = get_seconds(start,end)
    return s/60


if __name__ == '__main__':
    start = time.time()
    campaigns = system_generation_utils.generate_campaigns(config.num_campaigns)
    pacing_system = system_generation_utils.generate_pacing_system(config.pacing_algorithm)
    serving_system = ServingSystem(pacing_system=pacing_system, tracked_campaigns=campaigns)
    marketplace = Marketplace(serving_system=serving_system)
    # Run
    start_iter = time.time()
    day=0
    for i in range(config.num_days_to_simulate * config.num_iterations_per_day):
        marketplace.run_iteration()
        if(i%1440==0):
            end_iter = time.time()
            output = "The time of execution of day " + str(day) + " is :"
            seconds = get_seconds(start_iter, end_iter)
            print(output,
                  seconds, "s")
            day += 1
            start_iter = time.time()

    # Get output metrics as rows
    output_statistics = serving_system.get_statistics_for_all_campaigns()

    end = time.time()
    minutes = get_minutes(start,end)
    print("The time of execution of above program is :",
          minutes, "minutes")
    # Write metrics to csv file
    with open(OUTPUT_FILE_PATH, 'w') as f:
        all_fields = output_statistics[0].keys()
        w = csv.DictWriter(f, fieldnames=all_fields)
        w.writeheader()
        w.writerows(output_statistics)

