# Copyright Yahoo, Licensed under the terms of the Apache license . See LICENSE file in project root for terms.

import math

from src import constants
from src.system.clock import Clock

# We calculate the value of the cosine wave in each minute (m) of the day as:
# a * (1 + b * math.cos((2*math.pi)*(m/num_iterations_per_day + c))),
# where a, b, c are marketplace parameters:
# a: DC
# b: cosine amplitude, as a fraction of DC
# c: phase offset, as a fraction of the day (e.g., 0.25 means "shift the wave by a quarter of a day")


class DailyCosineWave:
    def __init__(self, dc: float, amplitude: float, phase: float):
        assert dc > 0
        assert 0 <= amplitude <= 1
        assert 0 <= phase <= 1
        self.dc = dc
        self.amplitude = amplitude
        self.phase = phase

    def calculate_current_value(self) -> float:
        current_fraction_of_day = Clock.minute_in_day() / constants.num_minutes_in_day
        return self.dc * (1 + self.amplitude * math.cos((2 * math.pi) * (current_fraction_of_day + self.phase)))
