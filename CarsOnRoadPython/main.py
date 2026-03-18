import numpy as np
from multiprocessing import Pool
from Simulation.EventLoop import EventLoop
from Visualisation.DrawGraph import draw_multi_graph


def run_simulation(args: tuple[int, float]) -> tuple[float, list[dict]]:
    thread_id, fraction = args
    
    # use_run_mean=False means each car's journey time is uniformly random between 10-360 min, 
    # which adds more variability to the results and better simulates real-world conditions.
    # With use_run_mean=True, each run draws a single random mean journey time that influences
    # 50% of spawned cars, which leads to more distinguishable patterns, but less realistic variability.
    history = EventLoop(spawn_fraction=fraction, thread_id=thread_id, use_run_mean=True).run()
    return (fraction, history)


if __name__ == "__main__":

    # Adjust this to test different spawn fractions (e.g., 0.1, 0.2, ..., 0.5)
    fraction = 0.3
    args = list(enumerate([fraction] * 100))

    with Pool() as pool:
        histories = pool.map(run_simulation, args)

    draw_multi_graph(histories)