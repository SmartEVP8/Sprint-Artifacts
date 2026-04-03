"""
Matplotlib grid visualisation for the SmartEV cost explorer.

Draws:
  - 400×400 km grid with 50 km guide lines
  - All stations (■) labelled with name and queue size
  - EV spawn point (▲) and destination (★)
  - One path line per cost-function combo, numbered at its midpoint
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import GRID_SIZE
from world import EV, Station


def draw_grid(
    ev: EV,
    stations: list[Station],
    results: list[dict],
    seed: int,
    out_path: str = "smartev_grid.png",
) -> None:
    fig, ax = plt.subplots(figsize=(12, 12), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(-10, GRID_SIZE + 10)
    ax.set_ylim(-10, GRID_SIZE + 10)
    ax.set_aspect("equal")
    ax.tick_params(colors="#8b949e")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")

    ax.set_title("SmartEV — Cost Function Permutations", color="#e6edf3",
                 fontsize=15, pad=14, fontfamily="monospace")
    ax.set_xlabel("km →", color="#8b949e", fontfamily="monospace")
    ax.set_ylabel("km →", color="#8b949e", fontfamily="monospace")

    _draw_grid_lines(ax)
    _draw_combo_paths(ax, ev, results)
    _draw_stations(ax, stations)
    _draw_ev(ax, ev)
    _draw_destination(ax, ev)
    _draw_legend(ax)

    ax.text(0, -8, f"Seed: {seed}", color="#8b949e", fontsize=8,
        fontfamily="monospace", va="top")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print(f"\n[✓] Grid saved to: {out_path}")


# ──────────────────────────────────────────────────────────────────────────────
# PRIVATE
# ──────────────────────────────────────────────────────────────────────────────

def _combo_colors(n: int):
    cmap = plt.get_cmap("tab20")
    return [cmap(i % 20) for i in range(n)]


def _draw_grid_lines(ax) -> None:
    for v in range(0, GRID_SIZE + 1, 50):
        ax.axhline(v, color="#21262d", linewidth=0.5, zorder=0)
        ax.axvline(v, color="#21262d", linewidth=0.5, zorder=0)


def _draw_combo_paths(ax, ev: EV, results: list[dict]) -> None:
    colors = _combo_colors(len(results))
    for r, col in zip(results, colors):
        s = r["best_station"]
        ax.plot([ev.x, s.x, ev.dest_x], [ev.y, s.y, ev.dest_y],
                color=col, linewidth=0.9, alpha=0.55, zorder=1)
        # Number label on the spawn→station leg midpoint
        ax.text((ev.x + s.x) / 2, (ev.y + s.y) / 2, str(r["id"]),
                color=col, fontsize=5.5, ha="center", va="center",
                alpha=0.85, fontfamily="monospace", zorder=2)


def _draw_stations(ax, stations: list[Station]) -> None:
    for s in stations:
        ax.scatter(s.x, s.y, s=140, color="#58a6ff", zorder=5,
                   marker="s", edgecolors="#1f6feb", linewidths=1.2)
        ax.text(s.x, s.y + 11, f"{s.name}\n(qSize: {s.queue})",
                color="#58a6ff", fontsize=7.5, ha="center", va="bottom",
                fontfamily="monospace", zorder=6,
                bbox=dict(boxstyle="round,pad=0.2", fc="#0d1117",
                          ec="#1f6feb", lw=0.7, alpha=0.85))


def _draw_ev(ax, ev: EV) -> None:
    ax.scatter(ev.x, ev.y, s=200, color="#3fb950", zorder=7,
               marker="^", edgecolors="#238636", linewidths=1.5)
    ax.text(ev.x + 6, ev.y + 6, f"EV\nSoC={ev.soc:.2f}",
            color="#3fb950", fontsize=7.5, fontfamily="monospace", zorder=8)


def _draw_destination(ax, ev: EV) -> None:
    ax.scatter(ev.dest_x, ev.dest_y, s=200, color="#f85149", zorder=7,
               marker="*", edgecolors="#da3633", linewidths=1.5)
    ax.text(ev.dest_x + 6, ev.dest_y + 6, "DEST",
            color="#f85149", fontsize=7.5, fontfamily="monospace", zorder=8)


def _draw_legend(ax) -> None:
    ax.legend(
        handles=[
            mpatches.Patch(color="#3fb950", label="EV spawn (▲)"),
            mpatches.Patch(color="#f85149", label="Destination (★)"),
            mpatches.Patch(color="#58a6ff", label="Station ■  (queue)"),
        ],
        loc="lower right",
        facecolor="#161b22", edgecolor="#30363d",
        labelcolor="#e6edf3", fontsize=8,
        prop={"family": "monospace"},
    )