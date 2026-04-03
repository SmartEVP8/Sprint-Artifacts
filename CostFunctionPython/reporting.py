"""
Console output for the SmartEV cost explorer.
Prints a per-combo breakdown table and a summary frequency tally.
"""

from collections import Counter
from world import EV, dist, energy_needed

import sys

SEP  = "─" * 90
DSEP = "=" * 90

class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def print_report(ev: EV, results: list[dict], reachable: list, seed: int) -> None:
    with open("smartev_report.txt", "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)  # print to both

        try:
            _print_header(ev, reachable)
            for r in results:
                _print_combo(r)
            _print_summary(results, seed)
        finally:
            sys.stdout = original_stdout  # restore
            
# ──────────────────────────────────────────────────────────────────────────────
# PRIVATE
# ──────────────────────────────────────────────────────────────────────────────

def _print_header(ev: EV, reachable: list) -> None:
    d = dist(ev.x, ev.y, ev.dest_x, ev.dest_y)
    print(DSEP)
    print("SMARTEV COST FUNCTION EXPLORER")
    print(DSEP)
    print(f"\nEV spawn:       ({ev.x:.1f}, {ev.y:.1f})")
    print(f"EV destination: ({ev.dest_x:.1f}, {ev.dest_y:.1f})")
    print(f"SoC:            {ev.soc:.3f}  ({ev.soc * ev.capacity:.1f} / {ev.capacity} kWh)")
    print(f"Direct distance:{d:.1f} km  →  needs {energy_needed(d):.1f} kWh  (can't reach: ✓)")
    print()
    print(f"Reachable stations ({len(reachable)}):")
    for s in reachable:
        print(f"  {s.name}  price={s.price:.0f}  queue={s.queue}")
    print()


def _print_combo(r: dict) -> None:
    print(SEP)
    print(f"  Combo {r['label']}")
    print(f"  → Best station: {r['best_station'].name}  "
          f"(price={r['best_station'].price:.0f}, queue={r['best_station'].queue})")
    print()
    print(f"  {'Station':<6} {'Urgency':>10} {'Price':>10} {'Path':>10} {'Queue':>8} {'TOTAL':>12}")
    print(f"  {'-------':<6} {'-------':>10} {'-----':>10} {'----':>10} {'-----':>8} {'-----':>12}")
    for sc in r["station_costs"]:
        marker = " ◄" if sc["station"] == r["best_station"] else ""
        print(f"  {sc['station'].name:<6} {sc['urgency']:>10.2f} {sc['price']:>10.2f} "
              f"{sc['path']:>10.2f} {sc['queue']:>8.2f} {sc['total']:>12.2f}{marker}")
    print()


def _print_summary(results: list[dict], seed: int) -> None:
    tally = Counter(r["best_station"].name for r in results)
    print(DSEP)
    print("SUMMARY: Station selection frequency across all combinations")
    print()
    for name, count in sorted(tally.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"  {name:>4}  {bar}  ({count}/{len(results)})")
    print()
    print(f"  Seed: {seed}")
    print()