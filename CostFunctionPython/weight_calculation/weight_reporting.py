"""
Console output for the WeightExplorer.

For each weight combination, shows:
  - which station won and by what margin over 2nd place
  - a full per-station cost breakdown so you can see how close things were
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


def print_weight_report(
    ev: EV,
    results: list[dict],
    reachable: list,
    seed: int,
    target_stations: list[str] | None = None,
) -> None:
    with open("smartev_weight_report.txt", "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        try:
            _print_header(ev, reachable, seed, total=len(results))
            _print_summary(results, target_stations)
            _print_combo_details(results, target_stations)
        finally:
            sys.stdout = original_stdout


# ──────────────────────────────────────────────────────────────────────────────
# PRIVATE
# ──────────────────────────────────────────────────────────────────────────────

def _print_header(ev: EV, reachable: list, seed: int, total: int) -> None:
    d = dist(ev.x, ev.y, ev.dest_x, ev.dest_y)
    print(DSEP)
    print("SMARTEV WEIGHT EXPLORER")
    print(DSEP)
    print(f"\nEV spawn:       ({ev.x:.1f}, {ev.y:.1f})")
    print(f"EV destination: ({ev.dest_x:.1f}, {ev.dest_y:.1f})")
    print(f"SoC:            {ev.soc:.3f}  ({ev.soc * ev.capacity:.1f} / {ev.capacity} kWh)")
    print(f"Direct distance:{d:.1f} km  →  needs {energy_needed(d):.1f} kWh  (can't reach: ✓)")
    print(f"Seed:           {seed}")
    print()
    print(f"Reachable stations ({len(reachable)}):")
    for s in reachable:
        print(f"  {s.name}  price={s.price:.0f}  queue={s.queue}")
    print()
    print(f"Weight steps: 0.2, 0.4, 0.6, 0.8, 1.0  |  Total combinations: {total}")
    print()


def _print_summary(results: list[dict], target_stations: list[str] | None) -> None:
    tally = Counter(r["best_station"].name for r in results)
    total = len(results)

    print(DSEP)
    print("SUMMARY: Station selection frequency across all weight combinations")
    print()
    for name, count in sorted(tally.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = "█" * (count // 10)
        tag = " ✓" if target_stations and name in target_stations else ""
        print(f"  {name:>4}{tag}  {bar}  ({count:>4}/{total}  {pct:5.1f}%)")
    print()


def _print_combo_details(results: list[dict], target_stations: list[str] | None) -> None:
    print(DSEP)
    print("DETAILED RESULTS: per weight combination")
    if target_stations:
        print(f"(Target stations: {', '.join(target_stations)}  — margin = gap between 1st and 2nd place)")
    print()

    for r in results:
        best        = r["best_station"]
        second      = r["second_station"]
        margin      = r["margin"]
        is_target   = target_stations and best.name in target_stations
        target_tag  = "✓" if is_target else "✗"

        print(SEP)
        print(
            f"  {target_tag} Combo #{r['id']:04d}  "
            f"w_urg={r['w_urgency']}  w_pri={r['w_price']}  "
            f"w_pth={r['w_path']}  w_que={r['w_queue']}"
        )
        print(
            f"  → Best: {best.name}  "
            f"(2nd: {second.name if second else '–'}  margin: {margin:.2f})"
        )
        print()
        print(f"  {'Station':<8} {'Urgency':>10} {'Price':>10} {'Path':>10} "
              f"{'Queue':>8} {'TOTAL':>12}")
        print(f"  {'-------':<8} {'-------':>10} {'-----':>10} {'----':>10} "
              f"{'-----':>8} {'-----':>12}")
        for sc in r["station_costs"]:
            marker = " ◄" if sc["station"] == best else ""
            print(
                f"  {sc['station'].name:<8} {sc['urgency']:>10.2f} {sc['price']:>10.2f} "
                f"{sc['path']:>10.2f} {sc['queue']:>8.2f} {sc['total']:>12.2f}{marker}"
            )
        print()