"""
Global simulation constants.
Tweak these to change EV/grid behaviour without touching the logic.
"""

GRID_SIZE   = 400     # km × km
EV_SPEED    = 80      # km/h
EV_CAPACITY = 75      # kWh
EV_DRAIN    = 0.15    # kWh / min  ->  0.15*60 = 9 kWh/h  ->  9/80 = 0.1125 kWh/km

PRICE_MIN   = 500
PRICE_MAX   = 1500

# kWh consumed per km  (drain_kWh_per_min / speed_km_per_min)
KWH_PER_KM  = EV_DRAIN / (EV_SPEED / 60)   # ≈ 0.1125 kWh/km

RANDOM_SEED = 621601      # set to None for a fresh run each time

# Hardcoded station positions
STATION_COORDS = [
    (60,  80),
    (150, 300),
    (200, 150),
    (300, 80),
    (320, 280),
    (100, 200),
    (250, 350),
    (370, 180),
]

# Only used in WeightExplorer mode: stations considered "good" picks. Set to None to skip the winning/losing breakdown.
TARGET_STATIONS = ["S6", "S2"] #None 