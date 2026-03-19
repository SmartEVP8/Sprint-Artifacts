import random
import Simulation.Car as CarModule
Car = CarModule.Car

MIN_JOURNEY_MINUTES = 10    # 10 minutes
SHORT_JOURNEY_MAX   = 120   # 2 hours
MAX_JOURNEY_MINUTES = 360   # 6 hours
SHORT_TRIP_WEIGHT   = 4.0


def _random_journey_minutes() -> int:
    """
    Samples a journey duration skewed toward shorter trips using a
    piecewise-uniform distribution.
    """
    short_range = SHORT_JOURNEY_MAX   - MIN_JOURNEY_MINUTES   # 110 min
    long_range  = MAX_JOURNEY_MINUTES - SHORT_JOURNEY_MAX      # 240 min

    w_short = SHORT_TRIP_WEIGHT * short_range
    w_long  = 1.0               * long_range
    p_short = w_short / (w_short + w_long)

    u = random.random()
    if u < p_short:
        return int(MIN_JOURNEY_MINUTES + (u / p_short) * short_range)
    else:
        return int(SHORT_JOURNEY_MAX + ((u - p_short) / (1.0 - p_short)) * long_range)


def spawn_cars_weighted(count: int) -> list[Car]:
    """
    Spawns `count` Car instances with a weighted short/long journey distribution.

    :param count: Number of cars to spawn.
    :return:      List of newly created Car objects.
    """
    return [Car(_random_journey_minutes()) for _ in range(count)]