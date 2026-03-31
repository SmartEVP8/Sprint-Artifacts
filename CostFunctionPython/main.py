"""
SmartEV Cost Function Explorer — entry point.

Modes:
  MODE = "CostFunctionEvaluator"  – runs all variant combos, one winner per combo
  MODE = "WeightExplorer"         – runs all weight combos for the single active variant

Run:  python main.py
"""

import random
import numpy as np

from config import RANDOM_SEED, TARGET_STATIONS
from world import make_stations, make_ev, can_reach
from evaluator import evaluate_combos
from reporting import print_report
from visualisation import draw_grid
from weight_calculation.weight_calculator import explore_weights
from weight_calculation.weight_reporting import print_weight_report

# ── Switch mode here ──────────────────────────────────────────────────────────
MODE = "WeightExplorer"   # "CostFunctionEvaluator" | "WeightExplorer"

# ─────────────────────────────────────────────────────────────────────────────

OUTPUT_IMAGE = "smartev_grid.png"


def main() -> None:
    seed = RANDOM_SEED if RANDOM_SEED is not None else random.randint(0, 1_000_000)
    random.seed(seed)
    np.random.seed(seed)

    stations = make_stations()

    print(f"\nMode: {MODE}")
    print("Generating EV that cannot reach destination directly...")
    for attempt in range(1, 10_001):
        ev = make_ev()
        if not can_reach(ev, ev.dest_x, ev.dest_y):
            break
    else:
        raise RuntimeError(
            "Could not generate an EV that needs charging in 10 000 tries. "
            "Check grid/SoC settings."
        )
    print(f"  Found after {attempt} attempt(s).\n")

    if MODE == "CostFunctionEvaluator":
        _run_cost_evaluator(ev, stations, seed)
    elif MODE == "WeightExplorer":
        _run_weight_explorer(ev, stations, seed)
    else:
        raise ValueError(f"Unknown MODE: {MODE!r}. Use 'CostFunctionEvaluator' or 'WeightExplorer'.")


def _run_cost_evaluator(ev, stations, seed):
    results, reachable = evaluate_combos(ev, stations)
    print_report(ev, results, reachable, seed)
    draw_grid(ev, stations, results, seed, out_path=OUTPUT_IMAGE)


def _run_weight_explorer(ev, stations, seed):
    print("Running weight explorer (10,000 combinations)...")
    results, reachable = explore_weights(ev, stations)
    print_weight_report(ev, results, reachable, seed, target_stations=TARGET_STATIONS)
    draw_grid(ev, stations, results, seed, out_path=OUTPUT_IMAGE)


if __name__ == "__main__":
    main()