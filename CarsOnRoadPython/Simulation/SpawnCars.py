import random
import Simulation.Car as CarModule
Car = CarModule.Car

MIN_JOURNEY_MINUTES = 10
MAX_JOURNEY_MINUTES = 360  # 6 hours
MEAN_STD_MINUTES    = 90   # standard deviation around the run mean


def _random_journey_minutes(run_mean: float | None) -> int:
    if run_mean is not None and random.random() < 0.5:
        minutes = random.gauss(run_mean, MEAN_STD_MINUTES)
    else:
        minutes = random.uniform(MIN_JOURNEY_MINUTES, MAX_JOURNEY_MINUTES)

    return int(max(MIN_JOURNEY_MINUTES, min(MAX_JOURNEY_MINUTES, minutes)))


def spawn_cars(count: int, run_mean: float | None) -> list[Car]:
    """
    Spawns `count` new Car instances, each with a randomly sampled journey duration.

    :param count:    Number of cars to spawn.
    :param run_mean: The run-level mean journey time in minutes, or None to
                     use a uniform random duration for all cars.
    :return:         List of newly created Car objects.
    """
    return [Car(_random_journey_minutes(run_mean)) for _ in range(count)]