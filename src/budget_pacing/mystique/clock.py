import src.budget_pacing.mystique.mystique_constants as mystique_constants


# This class will serve as a global clock.
# The class will be imported by different modules which need access to the clock.
# The (static) methods can be called through the class itself, so the class does not need to be instantiated.
class Clock:
    _interval = 0

    @classmethod
    def advance(cls):
        cls._interval += 1

    @classmethod
    def time(cls):
        return cls._interval % mystique_constants.num_iterations_per_day

    @classmethod
    def day(cls):
        return cls._interval // mystique_constants.num_iterations_per_day

    @classmethod
    def reset(cls):
        cls._interval = 0


