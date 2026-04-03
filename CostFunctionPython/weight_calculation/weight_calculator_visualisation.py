"""
weight_chart.py
---------------
Reads a SmartEV weight report (FoundWeights.txt) and produces a bar chart
grouped by dimension, showing the frequency of each weight value within
each dimension.

Usage:  python weight_chart.py
Output: weight_chart.png
"""

import re
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

from config import TARGET_STATIONS

import os

BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "WEIGHTS_LOGS.txt")
OUTPUT_FILE = "weight_chart.png"

# Only chart combos where this station won. Set to None to include all combos.
FILTER_WINNER = TARGET_STATIONS if TARGET_STATIONS else None

DIMS = [
    ("w_urg", "Urgency"),
    ("w_pri", "Price"),
    ("w_pth", "Path"),
    ("w_que", "Queue"),
]

COLOURS = {
    "w_urg": "#f78166",   # coral red
    "w_pri": "#79c0ff",   # sky blue
    "w_pth": "#56d364",   # green
    "w_que": "#e3b341",   # amber
}

ALL_POSSIBLE_WEIGHTS = [0.2, 0.4, 0.6, 0.8, 1.0]


# ──────────────────────────────────────────────────────────────────────────────
# PARSE
# ──────────────────────────────────────────────────────────────────────────────

def parse_combos(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(
        r"[✓✗] Combo #\d+\s+"
        r"w_urg=([\d.]+)\s+w_pri=([\d.]+)\s+w_pth=([\d.]+)\s+w_que=([\d.]+)\s+"
        r"→ Best: (\S+)"
    )
    return [
        {"w_urg": float(m.group(1)), "w_pri": float(m.group(2)),
         "w_pth": float(m.group(3)), "w_que": float(m.group(4)),
         "best":  m.group(5)}
        for m in pattern.finditer(content)
    ]


# ──────────────────────────────────────────────────────────────────────────────
# CHART
# ──────────────────────────────────────────────────────────────────────────────

def draw_chart(combos: list[dict], filter_winner: list[str] | None, out_path: str) -> None:
    subset = (
        [r for r in combos if r["best"] in filter_winner]
        if filter_winner else combos
    )
    if not subset:
        raise ValueError(f"No combos found for winner={filter_winner!r}")

    title_suffix = (
        f"combos where {', '.join(filter_winner)} won — {len(subset)} total"
        if filter_winner else f"all {len(combos)} combos"
    )

    bar_width  = 0.55
    dim_gap    = 1.2   # extra space between dimension groups

    # Build x positions and bar data in dimension order
    bars_x      = []   # x centre of each bar
    bars_height = []   # count
    bars_colour = []   # fill colour
    bars_label  = []   # "0.2", "0.4" etc — for x tick
    group_centres = [] # midpoint x of each dimension group (for group label)
    separator_xs  = [] # x positions of vertical dividers between groups

    cursor = 0.0
    for dim_idx, (key, label) in enumerate(DIMS):
        counts = Counter(r[key] for r in subset)
        # Only show weights that actually appear for this dimension
        weights = sorted(w for w in ALL_POSSIBLE_WEIGHTS if w in counts)

        group_start = cursor
        for w in weights:
            bars_x.append(cursor)
            bars_height.append(counts[w])
            bars_colour.append(COLOURS[key])
            bars_label.append(str(w))
            cursor += bar_width + 0.1

        group_end = cursor - 0.1
        group_centres.append((group_start + group_end) / 2)

        if dim_idx < len(DIMS) - 1:
            separator_xs.append(cursor + dim_gap / 2 - 0.1)
            cursor += dim_gap

    # ── figure ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 6), facecolor="#0d1117")
    ax.set_facecolor("#161b22")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
    ax.tick_params(colors="#8b949e", labelsize=9)
    ax.yaxis.grid(True, color="#21262d", linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)

    # ── bars ──────────────────────────────────────────────────────────────────
    rects = ax.bar(bars_x, bars_height, width=bar_width,
                   color=bars_colour, zorder=3,
                   edgecolor="#0d1117", linewidth=0.6)

    # Value labels on top
    for rect, h in zip(rects, bars_height):
        if h > 0:
            ax.text(rect.get_x() + rect.get_width() / 2, h + 0.3,
                    str(int(h)), ha="center", va="bottom",
                    color="#e6edf3", fontsize=9, fontfamily="monospace")

    # ── x ticks: weight values ────────────────────────────────────────────────
    ax.set_xticks(bars_x)
    ax.set_xticklabels(bars_label, color="#8b949e",
                       fontsize=9, fontfamily="monospace")

    # ── dimension labels below the weight ticks ───────────────────────────────
    y_dim_label = -0.13   # in axes-fraction coordinates
    for (key, label), cx in zip(DIMS, group_centres):
        ax.text(cx, y_dim_label, label,
                transform=ax.get_xaxis_transform(),
                ha="center", va="top",
                color=COLOURS[key], fontsize=11,
                fontfamily="monospace", fontweight="bold")

    # ── vertical separators between dimension groups ──────────────────────────
    for sx in separator_xs:
        ax.axvline(sx, color="#30363d", linewidth=1.2, linestyle="--", zorder=2)

    # ── axes labels ───────────────────────────────────────────────────────────
    ax.set_ylabel("Frequency", color="#8b949e", fontsize=11,
                  fontfamily="monospace", labelpad=10)
    ax.set_title(
        f"SmartEV — Weight frequency per dimension\n{title_suffix}",
        color="#e6edf3", fontsize=13, fontfamily="monospace", pad=16,
    )
    ax.set_xlim(-0.5, cursor - dim_gap + 0.5)
    ax.set_ylim(0, max(bars_height) * 1.2)

    # ── legend ────────────────────────────────────────────────────────────────
    ax.legend(
        handles=[mpatches.Patch(color=COLOURS[k], label=lbl) for k, lbl in DIMS],
        facecolor="#161b22", edgecolor="#30363d",
        labelcolor="#e6edf3", fontsize=10,
        prop={"family": "monospace"}, loc="upper right",
    )

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close(fig)
    print(f"[✓] Chart saved to: {out_path}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    combos = parse_combos(INPUT_FILE)
    print(f"Parsed {len(combos)} combos from {INPUT_FILE!r}")
    if FILTER_WINNER:
        print(f"Filtering to {FILTER_WINNER} wins: "
              f"{sum(1 for r in combos if r['best'] == FILTER_WINNER)} combos")
    draw_chart(combos, filter_winner=FILTER_WINNER, out_path=OUTPUT_FILE)