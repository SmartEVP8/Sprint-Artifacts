from Simulation import SpawnCars
from Simulation.CarsOnRoad import CarsOnRoad, DayOfWeek
from Simulation.SpawnCars import spawn_cars
from Simulation.Car import Car
from Simulation.SpawnSchedule import _build_spawn_schedule
import random

TICK_MINUTES = 30

class EventLoop:
    """
    Drives the simulation forward in fixed 30-minute ticks over one week.

    Each tick:
      1. Remove cars whose journey has ended.
      2. Compute how many cars to spawn this tick (a configurable fraction
         of the hourly CarsOnRoad target).
      3. Spawn those cars and add them to the active pool.
      4. Record a snapshot for later visualisation.

    Attributes:
        spawn_fraction: Fraction of the hourly target to spawn each tick.
                        0.5 means "half the hourly target per 30-min tick".
        use_run_mean:   If True, each run draws a random mean journey time
                        that influences 50% of spawned cars. If False, all
                        cars use a uniform random duration between 10-360 min.
        spread_spawns:  If True, cars are distributed evenly across each
                        minute of the tick instead of all spawning at once.
    """
    def __init__(self, spawn_fraction: float, thread_id: int = 0, use_run_mean: bool = True, spread_spawns: bool = False):
        if not (0.0 < spawn_fraction <= 1.0):
            raise ValueError("spawn_fraction must be between 0 and 1")

        self.spawn_fraction = spawn_fraction
        self.thread_id = thread_id
        self.use_run_mean = use_run_mean
        self.spread_spawns = spread_spawns
        self._active_cars: list[Car] = []
        self._completed_journeys: list[int] = []
        self.history: list[dict] = []

    def run(self) -> list[dict]:
        ticks_per_week = (7 * 24 * 60) // TICK_MINUTES
        run_mean = random.uniform(SpawnCars.MIN_JOURNEY_MINUTES, SpawnCars.MAX_JOURNEY_MINUTES) if self.use_run_mean else None

        for tick in range(ticks_per_week):
            total_minutes = tick * TICK_MINUTES
            day_index     = (total_minutes // (24 * 60)) % 7
            hour          = (total_minutes % (24 * 60)) // 60
            minute        = total_minutes % 60

            if self.spread_spawns:
                self._run_tick(DayOfWeek(day_index), hour, run_mean)
            else:
                self._age_cars()
                self._spawn_tick(DayOfWeek(day_index), hour, run_mean)

            self.history.append({
                "tick":        tick,
                "day":         DayOfWeek(day_index).name.capitalize(),
                "hour":        hour,
                "minute":      minute,
                "active_cars": len(self._active_cars),
            })

        peak_entry = max(self.history, key=lambda e: e["active_cars"])
        avg_active = sum(e["active_cars"] for e in self.history) / len(self.history)

        print(
            f"Thread {self.thread_id} finished — "
            f"Total EVs={CarsOnRoad.TOTAL_EVS:,} | "
            f"Spawn Fraction={self.spawn_fraction:.3f} | "
            f"Run Mean={f'{run_mean:.0f} min' if run_mean is not None else 'disabled'} | "
            f"Peak Active Cars={peak_entry['active_cars']:,} | "
            f"Exceeds Total EVs={peak_entry['active_cars'] - CarsOnRoad.TOTAL_EVS:,} | "
            f"Avg Active Cars={avg_active:,.0f} | "
            f"Total Journeys={len(self._completed_journeys):,}"
        )

        return self.history

    def _run_tick(self, day: DayOfWeek, hour: int, run_mean: float | None) -> None:
        hourly_target = CarsOnRoad.get_evs_on_road(day, hour)
        to_spawn      = int(hourly_target * self.spawn_fraction)
        schedule      = _build_spawn_schedule(to_spawn, TICK_MINUTES)

        for minute_offset in range(TICK_MINUTES):
            self._age_cars(minutes=1)
            batch_size = schedule[minute_offset]
            if batch_size > 0:
                self._active_cars.extend(spawn_cars(batch_size, run_mean))

    def _spawn_tick(self, day: DayOfWeek, hour: int, run_mean: float | None) -> None:
        hourly_target = CarsOnRoad.get_evs_on_road(day, hour)
        to_spawn = int(hourly_target * self.spawn_fraction)
        self._active_cars.extend(spawn_cars(to_spawn, run_mean))

    def _age_cars(self, minutes: int = TICK_MINUTES) -> None:
        surviving = []
        for car in self._active_cars:
            car.tick(minutes)
            if car.has_finished:
                self._completed_journeys.append(car.journey_duration_minutes)
            else:
                surviving.append(car)
        self._active_cars = surviving