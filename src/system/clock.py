import src.constants as constants


# This class will serve as a global clock.
# The class will be imported by different modules which need access to the clock.
# The (static) methods can be called through the class itself, so the class does not need to be instantiated.
class Clock:
    _iterations = 0

    @classmethod
    def advance(cls):
        cls._iterations += 1

    @classmethod
    def minute_in_day(cls):
        return cls._iterations % constants.num_minutes_in_day

    @classmethod
    def minute_in_hour(cls):
        return cls.minute_in_day() % constants.num_minutes_in_hour

    @classmethod
    def hour_in_day(cls):
        return cls.minute_in_day() // constants.num_minutes_in_hour

    @classmethod
    def days(cls):
        return cls._iterations // constants.num_minutes_in_day

    @classmethod
    def reset(cls):
        cls._iterations = 0


