"""
Evaluates every combination of cost-function variants for a given EV and
list of stations.

Returns a list of result dicts, one per (urgency × price × path × queue) combo.
Each dict contains:
  id             – combo number (1-based)
  label          – human-readable combo description
  best_station   – Station with the lowest total cost
  station_costs  – list of per-station breakdowns, sorted best→worst
"""

from world import EV, Station, can_reach
from costs import URGENCY_VARIANTS, PRICE_VARIANTS, PATH_VARIANTS, QUEUE_VARIANTS


def evaluate_combos(ev: EV, stations: list[Station]) -> list[dict]:
    min_p = min(s.price for s in stations)
    max_p = max(s.price for s in stations)
    avg_p = sum(s.price for s in stations) / len(stations)
    ctx = {"min_price": min_p, "max_price": max_p, "avg_price": avg_p}

    reachable = [s for s in stations if can_reach(ev, s.x, s.y)]
    if not reachable:
        raise RuntimeError("EV cannot reach any station — try again.")

    results = []
    combo_id = 0

    for u_lbl, u_fn in URGENCY_VARIANTS:
        for p_lbl, p_fn in PRICE_VARIANTS:
            for d_lbl, d_fn in PATH_VARIANTS:
                for q_lbl, q_fn in QUEUE_VARIANTS:
                    combo_id += 1

                    station_costs = []
                    for s in reachable:
                        u_val = min(u_fn(ev, s, ctx), 1e6)
                        p_val = p_fn(ev, s, ctx)
                        d_val = d_fn(ev, s, ctx)
                        q_val = q_fn(ev, s, ctx)

                        station_costs.append({
                            "station": s,
                            "urgency": u_val,
                            "price":   p_val,
                            "path":    d_val,
                            "queue":   q_val,
                            "total":   u_val + p_val + d_val + q_val,
                        })

                    station_costs.sort(key=lambda r: r["total"])
                    best = station_costs[0]["station"]

                    results.append({
                        "id":            combo_id,
                        "label":         f"#{combo_id:02d}  {u_lbl} | {p_lbl} | {d_lbl} | {q_lbl}",
                        "u_label":       u_lbl,
                        "p_label":       p_lbl,
                        "d_label":       d_lbl,
                        "q_label":       q_lbl,
                        "best_station":  best,
                        "station_costs": station_costs,
                    })

    return results, reachable