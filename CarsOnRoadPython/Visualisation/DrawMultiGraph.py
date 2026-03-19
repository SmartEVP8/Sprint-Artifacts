import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter, MultipleLocator

from Simulation.CarsOnRoad import CarsOnRoad

# One colour per day (Sunday–Saturday)
DAY_COLORS = {
    "Sunday":    "#a78bfa",  # purple
    "Monday":    "#f87171",  # red
    "Tuesday":   "#fb923c",  # orange
    "Wednesday": "#facc15",  # yellow
    "Thursday":  "#4ade80",  # green
    "Friday":    "#60a5fa",  # blue
    "Saturday":  "#f472b6",  # pink
}

TICKS_PER_DAY = 48


def _add_day_labels(ax: plt.Axes, y_max: float) -> None:
    """Adds vertical day dividers and day name labels to the x-axis."""
    for d in range(1, 7):
        ax.axvline(d * TICKS_PER_DAY - 0.5, color="gray", linewidth=0.6,
                   linestyle="--", alpha=0.4, zorder=2)

    for d in range(7):
        centre   = d * TICKS_PER_DAY + TICKS_PER_DAY / 2
        day_name = list(DAY_COLORS.keys())[d]
        ax.text(
            centre, -y_max * 0.08,
            day_name,
            ha="center", va="top",
            fontsize=8, fontweight="bold",
            color=DAY_COLORS[day_name],
            transform=ax.transData,
            clip_on=False,
        )


def _set_x_axis(ax: plt.Axes, history: list[dict]) -> None:
    """Sets x-axis tick labels to HH:MM format, one label per hour."""
    ticks   = [entry["tick"]   for entry in history]
    hours   = [entry["hour"]   for entry in history]
    minutes = [entry["minute"] for entry in history]

    label_ticks = ticks[::2]
    label_times = [f"{h:02d}:{m:02d}" for h, m in zip(hours, minutes)][::2]
    ax.set_xticks(label_ticks)
    ax.set_xticklabels(label_times, fontsize=6, rotation=45, ha="right")


def _set_y_axis(ax: plt.Axes, y_max: float) -> None:
    """Sets y-axis range, tick spacing, and label format."""
    ax.set_ylim(0, y_max)
    ax.yaxis.set_major_locator(MultipleLocator(50_000))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_ylabel("Active EVs on road")


def draw_graph(history: list[dict]) -> None:
    """
    Draws a single-run line graph of active EVs on the road.

    :param history: The list of tick snapshots returned by EventLoop.run().
    """
    ticks       = [entry["tick"]        for entry in history]
    active_cars = [entry["active_cars"] for entry in history]

    fig, ax = plt.subplots(figsize=(28, 6))

    ax.plot(ticks, active_cars, color="steelblue", linewidth=1.2, label="Active EVs")
    ax.axhline(CarsOnRoad.TOTAL_EVS, color="red", linewidth=1.2, linestyle="--",
               label=f"Total EVs ({CarsOnRoad.TOTAL_EVS:,})", zorder=3)

    y_max = max(active_cars) * 1.15
    _set_x_axis(ax, history)
    _set_y_axis(ax, y_max)
    _add_day_labels(ax, y_max)

    day_patches = [mpatches.Patch(color=c, label=d) for d, c in DAY_COLORS.items()]
    ax.legend(
        handles=day_patches + [
            plt.Line2D([0], [0], color="steelblue", linewidth=1.2, label="Active EVs"),
            plt.Line2D([0], [0], color="red", linewidth=1.2, linestyle="--",
                       label=f"Total EVs ({CarsOnRoad.TOTAL_EVS:,})"),
        ],
        fontsize=7, loc="upper right",
    )

    ax.set_title("Active EVs on Road — One Week Simulation (30-min ticks)")
    ax.grid(axis="y", linewidth=0.3, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("ev_graph.png", dpi=150, bbox_inches="tight")
    print("Saved → ev_graph.png")
    plt.show()


def draw_multi_graph(histories: list[tuple[float, list[dict]]]) -> None:
    fig, ax = plt.subplots(figsize=(28, 6))

    colormap = cm.rainbow
    n = len(histories)

    for i, (fraction, history) in enumerate(histories):
        ticks       = [entry["tick"]        for entry in history]
        active_cars = [entry["active_cars"] for entry in history]
        color       = colormap(i / (n - 1))
        ax.plot(ticks, active_cars, color=color, linewidth=0.8, alpha=0.5, zorder=2)

    ax.axhline(CarsOnRoad.TOTAL_EVS, color="black", linewidth=1.2, linestyle="--",
               label=f"Total EVs ({CarsOnRoad.TOTAL_EVS:,})", zorder=3)

    all_active = [e["active_cars"] for _, h in histories for e in h]
    y_max = max(all_active) * 1.15

    _set_x_axis(ax, histories[0][1])
    _set_y_axis(ax, y_max)
    _add_day_labels(ax, y_max)

    sm = cm.ScalarMappable(cmap=colormap, norm=plt.Normalize(vmin=1, vmax=n))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.01)
    cbar.set_label("Run index", fontsize=8)

    ax.set_title(f"Active EVs on Road — {n} Runs (spawn_fraction={histories[0][0]:.3f})")
    ax.grid(axis="y", linewidth=0.3, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("ev_graph_multi.png", dpi=150, bbox_inches="tight")
    print("Saved → ev_graph_multi.png")
    plt.show()