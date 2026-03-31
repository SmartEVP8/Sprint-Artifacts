"""
WeightExplorer
--------------
Evaluates weight combinations for the single active cost function.

Price and Path are constrained to [0.4, 0.6, 0.8, 1.0] (we want them influential).
Urgency and Queue sweep [0.2, 0.4, 0.6, 0.8, 1.0] as before.

For each combo records: winner, 2nd place, and margin between them.
"""

from world import EV, Station, can_reach
from costs import URGENCY_VARIANTS, PRICE_VARIANTS, PATH_VARIANTS, QUEUE_VARIANTS


WEIGHT_STEPS_FULL = [round(x * 0.2, 1) for x in range(1, 6)]        # [0.2, 0.4, 0.6, 0.8, 1.0]
WEIGHT_STEPS_URGENCY = [round(x * 0.2, 1) for x in range(1, 6)]     # [0.2, 0.4, 0.6, 0.8, 1.0]
WEIGHT_STEPS_PATH = [round(x * 0.2, 1) for x in range(4, 6)]        # [0.8, 1.0]
WEIGHT_STEPS_QUEUE = [round(x * 0.2, 1) for x in range(4, 6)]       # [0.8, 1.0]
WEIGHT_STEPS_PRICE = [round(x * 0.4, 1) for x in range(1, 2)]       # [0.4]

def explore_weights(ev: EV, stations: list[Station]) -> tuple[list[dict], list[Station]]:
    assert len(URGENCY_VARIANTS) == 1, "WeightExplorer expects exactly 1 urgency variant"
    assert len(PRICE_VARIANTS)   == 1, "WeightExplorer expects exactly 1 price variant"
    assert len(PATH_VARIANTS)    == 1, "WeightExplorer expects exactly 1 path variant"
    assert len(QUEUE_VARIANTS)   == 1, "WeightExplorer expects exactly 1 queue variant"

    _, u_fn = URGENCY_VARIANTS[0]
    _, p_fn = PRICE_VARIANTS[0]
    _, d_fn = PATH_VARIANTS[0]
    _, q_fn = QUEUE_VARIANTS[0]

    min_p = min(s.price for s in stations)
    max_p = max(s.price for s in stations)
    avg_p = sum(s.price for s in stations) / len(stations)
    ctx = {"min_price": min_p, "max_price": max_p, "avg_price": avg_p}

    reachable = [s for s in stations if can_reach(ev, s.x, s.y)]
    if not reachable:
        raise RuntimeError("EV cannot reach any station — try again.")

    # Pre-compute raw (unweighted) costs once per station
    raw = {
        s.name: {
            "station": s,
            "urgency": min(u_fn(ev, s, ctx), 1e6),
            "price":   p_fn(ev, s, ctx),
            "path":    d_fn(ev, s, ctx),
            "queue":   q_fn(ev, s, ctx),
        }
        for s in reachable
    }

    results = []
    combo_id = 0

    # Going through the weights for each that we care fo, defined up in the weight steps. 
    # If you want to go through each step, you can just exchange all with WEIGHT_STEPS_FULL
    for w_u in WEIGHT_STEPS_URGENCY:
        for w_p in WEIGHT_STEPS_PRICE:
            for w_d in WEIGHT_STEPS_PATH:
                for w_q in WEIGHT_STEPS_QUEUE:
                    combo_id += 1

                    station_costs = []
                    for s in reachable:
                        r = raw[s.name]
                        total = (w_u * r["urgency"]
                               + w_p * r["price"]
                               + w_d * r["path"]
                               + w_q * r["queue"])
                        station_costs.append({
                            "station": s,
                            "urgency": r["urgency"],
                            "price":   r["price"],
                            "path":    r["path"],
                            "queue":   r["queue"],
                            "total":   total,
                        })

                    station_costs.sort(key=lambda x: x["total"])

                    best   = station_costs[0]
                    second = station_costs[1] if len(station_costs) > 1 else None
                    margin = (second["total"] - best["total"]) if second else float("inf")

                    results.append({
                        "id":             combo_id,
                        "w_urgency":      w_u,
                        "w_price":        w_p,
                        "w_path":         w_d,
                        "w_queue":        w_q,
                        "best_station":   best["station"],
                        "second_station": second["station"] if second else None,
                        "margin":         margin,
                        "station_costs":  station_costs,
                    })

    return results, reachable