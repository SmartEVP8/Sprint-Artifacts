from enum import IntEnum


class DayOfWeek(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


class CarsOnRoad:
    """
    Provides congestion values for each hour of each day of the week.
    """

    # Constants
    TOTAL_EVS = 556_000
    BASELINE_CARS = TOTAL_EVS * 3 // 100
    PEAK_CARS = TOTAL_EVS * 75 // 100
    _MAX_CONGESTION = 100

    # Congestion matrix [day][hour]
    _CONGESTION = [
        # Sunday
        [3, 2, 3, 4, 4, 4, 6, 8, 10, 12, 14, 16, 20, 16, 20, 24, 26, 26, 22, 21, 16, 12, 6, 4],

        # Monday
        [3, 2, 3, 4, 16, 32, 88, 96, 72, 48, 32, 24, 32, 40, 48, 52, 48, 28, 32, 28, 28, 16, 8, 4],

        # Tuesday
        [3, 2, 3, 4, 16, 32, 96, 100, 72, 48, 32, 28, 40, 48, 64, 64, 48, 32, 28, 24, 16, 12, 8, 4],

        # Wednesday
        [3, 2, 3, 4, 16, 24, 48, 56, 48, 40, 16, 24, 32, 40, 48, 48, 40, 24, 28, 24, 16, 12, 8, 4],

        # Thursday
        [3, 2, 3, 4, 16, 24, 48, 56, 48, 40, 24, 32, 48, 64, 64, 56, 48, 40, 32, 24, 16, 16, 8, 4],

        # Friday
        [3, 2, 3, 4, 8, 12, 16, 24, 32, 24, 20, 32, 44, 60, 58, 52, 44, 32, 24, 16, 16, 12, 8, 4],

        # Saturday
        [3, 2, 3, 4, 4, 4, 6, 8, 12, 14, 16, 24, 32, 32, 24, 20, 22, 20, 21, 20, 16, 12, 8, 4],
    ]

    @classmethod
    def get_evs_on_road(cls, day: DayOfWeek, hour: int) -> int:
        """
        Gets the estimated number of EVs on the road for a specific day and hour.

        :param day: DayOfWeek enum
        :param hour: int (0-23)
        :return: int
        """
        car_congestion = cls._CONGESTION[day][hour]
        cars = cls.BASELINE_CARS + (
            (cls.PEAK_CARS - cls.BASELINE_CARS) * car_congestion // cls._MAX_CONGESTION
        )

        return min(cars, cls.TOTAL_EVS)