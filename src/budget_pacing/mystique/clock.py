import src.budget_pacing.mystique.mystique_constants as mystique_constants


# This class will serve as a global clock.
# The class will be imported by different modules which need access to the clock.
# The (static) methods can be called through the class itself, so the class does not need to be instantiated.
class Clock:
    interval = 0  # This field should not be manipulated directly (except in unit tests)

    @classmethod
    def advance(cls):
        assert(cls.interval < mystique_constants.num_iterations_per_day)
        cls.interval += 1
        if cls.interval >= mystique_constants.num_iterations_per_day:
            cls.interval = 0

    @classmethod
    def time(cls):
        return cls.interval

    @classmethod
    def reset(cls):
        cls.interval = 0



