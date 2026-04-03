import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline


def draw(labels: list[str], configurations: dict[str, list[int]], output_dir: str = "JourneyDurationsGraphs") -> None:
    colors = plt.cm.tab10.colors
    x = np.arange(len(labels))

    for (config_name, counts), color in zip(configurations.items(), colors):
        fig, ax = plt.subplots(figsize=(10, 6))

        _draw_bars(ax, x, counts, color)
        _draw_curve(ax, x, counts, color)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=90)
        ax.set_title(config_name)
        ax.set_xlabel("Journey Duration Bucket")
        ax.set_ylabel("Number of EVs")
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        filename = f"{config_name}.png"
        plt.savefig(os.path.join(output_dir, filename), dpi=150)
        plt.close(fig)
        print(f"Saved: {filename}")


def _draw_bars(ax, x, counts: list[int], color) -> None:
    bucket_order = np.argsort(counts)[::-1]

    for bucket_idx in bucket_order:
        ax.bar(
            x[bucket_idx],
            counts[bucket_idx],
            color=color,
            alpha=0.75,
            zorder=int(1e6 - counts[bucket_idx]),
        )


def _draw_curve(ax, x, counts: list[int], color) -> None:
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spline = make_interp_spline(x, counts, k=3)
    y_smooth = np.maximum(spline(x_smooth), 0)
    ax.plot(x_smooth, y_smooth, color=color, linewidth=2.2, zorder=999)