from __future__ import annotations

import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np


CLASS_ORDER = [
    "collapse_to_pressure",
    "collapse_to_exclusion",
    "stable_front",
    "traveling_front",
    "multi_domain_persistent",
    "fragmenting",
    "oscillatory_domain",
    "runaway_or_unphysical",
    "undetermined",
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_kymograph(
    x: np.ndarray,
    times: List[float],
    field_stack: np.ndarray,
    out_path: str,
    title: str,
    cmap: str = "viridis",
) -> None:
    ensure_dir(os.path.dirname(out_path))
    plt.figure(figsize=(10, 4.8))
    plt.imshow(
        field_stack,
        aspect="auto",
        origin="lower",
        extent=[float(x[0]), float(x[-1]), float(times[0]), float(times[-1])],
        cmap=cmap,
    )
    plt.colorbar()
    plt.xlabel("x")
    plt.ylabel("time")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def plot_front_position(front_rows: List[Dict[str, float]], out_path: str) -> None:
    if not front_rows:
        return
    ensure_dir(os.path.dirname(out_path))
    plt.figure(figsize=(8.5, 4.5))
    times = [row["time"] for row in front_rows]
    positions = [row["front_position"] for row in front_rows]
    plt.plot(times, positions, marker="o", linewidth=1.2, markersize=2.5)
    plt.xlabel("time")
    plt.ylabel("front position")
    plt.title("Front Position vs Time")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def plot_front_velocity_vs_parameter(
    summary_rows: List[Dict[str, float | str | bool]],
    parameter_name: str,
    out_path: str,
) -> None:
    filtered = [row for row in summary_rows if parameter_name in row]
    if not filtered:
        return
    ensure_dir(os.path.dirname(out_path))
    xs = [float(row[parameter_name]) for row in filtered]
    ys = [float(row["late_time_mean_front_speed"]) for row in filtered]
    plt.figure(figsize=(8.5, 4.5))
    plt.plot(xs, ys, marker="o")
    plt.xlabel(parameter_name)
    plt.ylabel("late-time mean front speed")
    plt.title(f"Front Velocity vs {parameter_name}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def plot_phase_map(
    summary_rows: List[Dict[str, float | str | bool]],
    x_name: str,
    y_name: str,
    out_path: str,
) -> None:
    filtered = [
        row for row in summary_rows
        if x_name in row and y_name in row and "classification" in row
    ]
    if not filtered:
        return

    ensure_dir(os.path.dirname(out_path))
    class_to_num = {name: index for index, name in enumerate(CLASS_ORDER)}

    x_values = sorted({float(row[x_name]) for row in filtered})
    y_values = sorted({float(row[y_name]) for row in filtered})
    grid = np.full((len(y_values), len(x_values)), np.nan, dtype=float)
    x_index = {value: idx for idx, value in enumerate(x_values)}
    y_index = {value: idx for idx, value in enumerate(y_values)}

    for row in filtered:
        classification = str(row["classification"])
        grid[y_index[float(row[y_name])], x_index[float(row[x_name])]] = class_to_num.get(classification, len(CLASS_ORDER) - 1)

    if len(x_values) == 1:
        x_min = x_values[0] - 0.5
        x_max = x_values[0] + 0.5
    else:
        x_step = min(np.diff(x_values))
        x_min = x_values[0] - 0.5 * x_step
        x_max = x_values[-1] + 0.5 * x_step

    if len(y_values) == 1:
        y_min = y_values[0] - 0.5
        y_max = y_values[0] + 0.5
    else:
        y_step = min(np.diff(y_values))
        y_min = y_values[0] - 0.5 * y_step
        y_max = y_values[-1] + 0.5 * y_step

    plt.figure(figsize=(8.5, 5.5))
    masked = np.ma.masked_invalid(grid)
    cmap = plt.cm.get_cmap("tab10", len(CLASS_ORDER))
    image = plt.imshow(
        masked,
        aspect="auto",
        origin="lower",
        cmap=cmap,
        vmin=-0.5,
        vmax=len(CLASS_ORDER) - 0.5,
        extent=[x_min, x_max, y_min, y_max],
    )
    colorbar = plt.colorbar(image, ticks=range(len(CLASS_ORDER)))
    colorbar.ax.set_yticklabels(CLASS_ORDER)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title(f"Phase Map in ({x_name}, {y_name})")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()
