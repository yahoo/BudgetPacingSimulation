# Budget Pacing Simulation Framework

## Running the Simulation
### Running a single simulation
1. Set up the desired configuration in `src/configuration.py`.
   1. Choose the desired pacing algorithm by defining the `pacing_algorithm` variable, e.g.: `pacing_algorithm = constants.BudgetPacingAlgorithms.MYSTIQUE_NON_LINEAR`.
2. Run `src/main.py`.

### Running multiple simulations simultaneously
If you're running the simulations through PyCharm, you can use the run configurations defined in the `runConfigurations` directory.
First, set up the desired configuration in `src/configuration.py`, without changing the value of the `pacing_algorithm` variable.
Then run the `runConfigurations/All-Pacing-Systems.run.xml` compound configuration, which will run the simulation with each of the following pacing systems:
1. Mystique Linear
2. Mystique Non-Linear
3. Mystique Linear Hard Throttling
4. Mystique Non-Linear Hard Throttling
5. Without Budget Pacing

The predefined run configurations set the `PACING_SYSTEM` environment variable which is read by the `src/configuration.py` file.

### Output
The simulation outputs the statistics into a directory, that is dedicated to the current configuration, which will be created inside the `output` folder.

## Reference
If you use Optuna in one of your research projects, please cite our WWW paper "Mystique: A Budget Pacing System for Performance Optimization in Online Advertising":

```
@inproceedings{stram2024Mystique,
  title={Mystique: A Budget Pacing System for Performance Optimization in Online Advertising},
  author={Stram, Rotem and Abboud, Rani and Shtoff, Alex and Somekh, Oren and Raviv, Ariel and Koren, Yair},
  booktitle={Proceedings of the ACM Web Conference 2024},
  year={2024}
}