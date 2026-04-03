"""
Data classes and world-generation helpers.

  Station  – a charging point with a position, price, and queue length
  EV       – a vehicle with a spawn, destination, and battery state
  make_stations() / make_ev() – random-world factories
"""

import random
import math
from dataclasses import dataclass

from config import (
    GRID_SIZE, EV_SPEED, EV_CAPACITY, EV_DRAIN, KWH_PER_KM,
    PRICE_MIN, PRICE_MAX, STATION_COORDS,
)


# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Station:
    name:  str
    x:     float
    y:     float
    price: float
    queue: int          # 0-9


@dataclass
class EV:
    x:          float   # spawn
    y:          float
    dest_x:     float
    dest_y:     float
    soc:        float   # 0-1, State of Charge
    capacity:   float = EV_CAPACITY
    speed:      float = EV_SPEED
    drain:      float = EV_DRAIN


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def dist(ax: float, ay: float, bx: float, by: float) -> float:
    return math.hypot(bx - ax, by - ay)


def energy_needed(d_km: float) -> float:
    """kWh needed to travel d_km."""
    return d_km * KWH_PER_KM


def can_reach(ev: EV, tx: float, ty: float) -> bool:
    """True if the EV has enough charge to reach (tx, ty)."""
    return ev.soc * ev.capacity >= energy_needed(dist(ev.x, ev.y, tx, ty))


# ──────────────────────────────────────────────────────────────────────────────
# FACTORIES
# ──────────────────────────────────────────────────────────────────────────────

def make_stations() -> list[Station]:
    stations = []
    for i, (x, y) in enumerate(STATION_COORDS):
        price = random.triangular(PRICE_MIN, PRICE_MAX, (PRICE_MIN + PRICE_MAX) / 2)
        queue = random.randint(0, 9)
        stations.append(Station(name=f"S{i+1}", x=x, y=y, price=round(price, 1), queue=queue))
    return stations


def make_ev() -> EV:
    """Spawn an EV that cannot reach its destination on current charge."""
    while True:
        x,  y  = random.uniform(0, GRID_SIZE), random.uniform(0, GRID_SIZE)
        dx, dy = random.uniform(0, GRID_SIZE), random.uniform(0, GRID_SIZE)
        soc    = random.uniform(0.05, 0.95)
        ev = EV(x=x, y=y, dest_x=dx, dest_y=dy, soc=soc)
        if not can_reach(ev, dx, dy):
            return ev