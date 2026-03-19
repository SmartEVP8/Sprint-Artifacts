import numpy as np
from multiprocessing import Pool
from Simulation.EventLoop import EventLoop
from Simulation.SpawnCarsWeightedJourneys import spawn_cars_weighted
from Visualisation import DrawBarGraph, DrawLineGraph, DrawMultiGraph

# ── Mode selector ────────────────────────────────────────────────────────────
# "bar"   — single run, bar chart, weighted short/long journey distribution
# "line"  — single run, line chart, uniform journey distribution
# "multi" — N runs in parallel, line chart, rainbow coloured by run index
MODE = "multi"

# ── Parameters ───────────────────────────────────────────────────────────────
SPAWN_FRACTION = 0.25
N_RUNS         = 50
USE_RUN_MEAN   = True

def run_simulation(args: tuple[int, float]) -> tuple[float, list[dict]]:
    thread_id, fraction = args
    history = EventLoop(spawn_fraction=fraction, thread_id=thread_id,
                        use_run_mean=USE_RUN_MEAN).run()
    return (fraction, history)


if __name__ == "__main__":
    if MODE == "bar":
        history = EventLoop(spawn_fraction=SPAWN_FRACTION, use_run_mean=False).run()
        DrawBarGraph.draw_bar_graph(history)

    elif MODE == "line":
        history = EventLoop(spawn_fraction=SPAWN_FRACTION,
                            use_run_mean=USE_RUN_MEAN).run()
        DrawLineGraph.draw_line_graph(history)

    elif MODE == "multi":
        args = list(enumerate([SPAWN_FRACTION] * N_RUNS))
        with Pool() as pool:
            histories = pool.map(run_simulation, args)
        DrawMultiGraph.draw_multi_graph(histories)

    else:
        raise ValueError(f"Unknown MODE '{MODE}'. Choose 'bar', 'line', or 'multi'.")