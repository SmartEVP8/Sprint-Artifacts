"""
Cost function variants for each dimension:

  URGENCY_VARIANTS  – how urgency (SoC) is penalised
  PRICE_VARIANTS    – how station price is penalised
  PATH_VARIANTS     – how path deviation is penalised
  QUEUE_VARIANTS    – how queue length is penalised

Each entry is a (label, fn) tuple where fn(ev, station, ctx) -> float.
ctx is a dict pre-computed once per evaluation round:
  ctx["min_price"], ctx["max_price"], ctx["avg_price"]
"""

import math
from world import EV, Station
from config import EV_SPEED


# ──────────────────────────────────────────────────────────────────────────────
# ROUTING HELPERS  (only needed internally by path variants)
# ──────────────────────────────────────────────────────────────────────────────

def _travel_time_min(d_km: float) -> float:
    return (d_km / EV_SPEED) * 60


def _euclidean(ax, ay, bx, by):
    return math.hypot(bx - ax, by - ay)


def _detour_extra_minutes(ev: EV, s: Station, ctx: dict = None) -> float:
    d_via    = _euclidean(ev.x, ev.y, s.x, s.y) + _euclidean(s.x, s.y, ev.dest_x, ev.dest_y)
    d_direct = _euclidean(ev.x, ev.y, ev.dest_x, ev.dest_y)
    return _travel_time_min(d_via - d_direct)


def _detour_extra_km(ev: EV, s: Station) -> float:
    d_via    = _euclidean(ev.x, ev.y, s.x, s.y) + _euclidean(s.x, s.y, ev.dest_x, ev.dest_y)
    d_direct = _euclidean(ev.x, ev.y, ev.dest_x, ev.dest_y)
    return d_via - d_direct


def _total_route_minutes(ev: EV, s: Station) -> float:
    d_via = _euclidean(ev.x, ev.y, s.x, s.y) + _euclidean(s.x, s.y, ev.dest_x, ev.dest_y)
    return _travel_time_min(d_via)


def _original_journey_minutes(ev: EV) -> float:
    return _travel_time_min(_euclidean(ev.x, ev.y, ev.dest_x, ev.dest_y))


def _original_journey_km(ev: EV) -> float:
    return _euclidean(ev.x, ev.y, ev.dest_x, ev.dest_y)


# ──────────────────────────────────────────────────────────────────────────────
# URGENCY
# Note: U1-U5 increase cost with higher SoC (fuller battery = pickier EV).
#       U6 inverts this: low SoC = high cost (desperate EV = less picky).
#       Which direction is "correct" depends on what urgency models in your sim.
# ──────────────────────────────────────────────────────────────────────────────

#def urg_soc_linear(ev, s, ctx):         return ev.soc * 100
#def urg_soc_squared(ev, s, ctx):       return (ev.soc ** 2) * 100
#def urg_half_soc(ev, s, ctx):          return 0.5 * ev.soc * 100
#def urg_ax2_plus(ev, s, ctx):          return 1.0 * (ev.soc ** 2) + 100 * ev.soc
#2def urg_inv_sqrt(ev, s, ctx):         return (ev.soc ** -0.5) + ev.soc
# def urg_inverted_linear(ev, s, ctx):  return (1 - ev.soc) * 100
def urg_exponential_curve(ev, s, ctx):  return 0.02 * ((ev.soc * 100) ** 2)

URGENCY_VARIANTS = [
    #("U1: SoC*100",             urg_soc_linear),
    # ("U2: SoC²*100",          urg_soc_squared),
    # ("U3: 0.5*SoC*100",       urg_half_soc),
    # ("U4: ax²+100*SoC",       urg_ax2_plus),
    #("U5: SoC⁻⁰·⁵+SoC",         urg_inv_sqrt),
    # ("U6: (1-SoC)*100",       urg_inverted_linear),
    ("U7: 0.02 * SoC²",          urg_exponential_curve),
]


# ──────────────────────────────────────────────────────────────────────────────
# PRICE
# ──────────────────────────────────────────────────────────────────────────────

#def price_relative(ev, s, ctx):
    #return ((ctx["max_price"] - ctx["min_price"]) / max(s.price, 1)) * 100

def price_neg_avg_diff(ev, s, ctx):
    return -(ctx["avg_price"] - s.price)        

#def price_shift(ev, s, ctx):
    #return s.price - ctx["min_price"] + (ctx["max_price"] - ctx["min_price"]) / 2

#def price_sq_avg_diff(ev, s, ctx):
    #return (ctx["avg_price"] - s.price) ** 2

#def price_ratio(ev, s, ctx):
    #return (s.price / ctx["avg_price"]) * 100   

#def price_above_avg(ev, s, ctx):
    #return max(0.0, s.price - ctx["avg_price"]) # only penalises above-average prices

PRICE_VARIANTS = [
    # ("P1: (max-min)/currentPrice*100",      price_relative),
    ("P2: -(avgPrice-currentPrice)",          price_neg_avg_diff),
    # ("P3: currentPrice-minPrice+(range/2)", price_shift),
    # ("P4: (avgPrice-currentPrice)²",        price_sq_avg_diff),
    # ("P5: currentPrice/avgPrice*100",       price_ratio),
    # ("P6: max(0, currentPrice-avgPrice)",   price_above_avg),
]


# ──────────────────────────────────────────────────────────────────────────────
# PATH DEVIATION
# ──────────────────────────────────────────────────────────────────────────────

def path_extra_seconds(ev, s, ctx):
    return _detour_extra_minutes(ev, s)

#def path_ratio(ev, s, ctx):
    #orig  = _original_journey_minutes(ev)
    #total = _total_route_minutes(ev, s)
    #return (1 - (orig / total)) * 100

#def path_log_ratio(ev, s, ctx):
    #orig  = _original_journey_minutes(ev)
    #total = _total_route_minutes(ev, s)
    #return math.log(max(total / max(orig, 0.01), 1.0)) * 100

#def path_km_ratio(ev, s, ctx):
    #detour_km = _detour_extra_km(ev, s)
    #orig_km   = _original_journey_km(ev)
    #return (detour_km / max(orig_km, 0.01)) * 100

#def path_quadratic_normalised(ev, s, ctx):
    #detour_min = _detour_extra_minutes(ev, s)
    #orig_min   = _original_journey_minutes(ev)
    #return (detour_min ** 2) / max(orig_min, 0.01)

# Free-detour-zone: detours under FREE_DETOUR_THRESHOLD minutes cost nothing
# FREE_DETOUR_THRESHOLD = 5.0

#def path_free_zone(ev, s, ctx):
    #extra = _detour_extra_minutes(ev, s)
    #return max(0.0, extra - FREE_DETOUR_THRESHOLD) * 60   # same unit as D1

PATH_VARIANTS = [
    ("D1: extraMinutes",                  _detour_extra_minutes),
    #("D2: (1 - (orig / total)) * 100",    path_ratio),
    # ("D3: log(total/orig)*100",         path_log_ratio),
    # ("D4: (detourKm/origKm)*100",       path_km_ratio),
    # ("D5: detourMin²/origMin",          path_quadratic_normalised),
    #("D6: freeZone(5min)*extraSeconds",  path_free_zone),
]


# ──────────────────────────────────────────────────────────────────────────────
# QUEUE SIZE
# ──────────────────────────────────────────────────────────────────────────────

MAX_QUEUE_SIZE = 15

#def queue_squared(ev, s, ctx):       return float(s.queue ** 2)
#def queue_linear(ev, s, ctx):        return float(s.queue)
def queue_cubed(ev, s, ctx):         return float(s.queue ** 3)
#def queue_normalised(ev, s, ctx):    return (s.queue / MAX_QUEUE_SIZE) * 100
#def queue_empty_bonus(ev, s, ctx):   return 0.0 if s.queue == 0 else float(s.queue * 10)

QUEUE_VARIANTS = [
    #("Q1: queue²",                queue_squared),
    #("Q2: queue",                queue_linear),
    ("Q3: queue³",                queue_cubed),
    # ("Q4: (queue/max)*100",     queue_normalised),
    #("Q5: 0 if empty else q+10",  queue_empty_bonus),
]