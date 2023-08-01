import src.configuration as config


# This class will serve as a global clock.
# The class will be imported by different modules which need access to the clock.
# The (static) methods can be called through the class itself, so the class does not need to be instantiated.
class Clock:
    _iterations = 0

    @classmethod
    def advance(cls):
        cls._iterations += 1

    @classmethod
    def minutes(cls):
        return cls._iterations % config.n_iterations_per_day

    @classmethod
    def days(cls):
        return cls._iterations // config.n_iterations_per_day

    @classmethod
    def reset(cls):
        cls._iterations = 0


