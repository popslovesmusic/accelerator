from __future__ import annotations

from typing import Dict, List

import numpy as np


def classify_run(
    timeseries_rows: List[Dict[str, float]],
    front_rows: List[Dict[str, float]],
    blew_up: bool,
    negative_undershoot_events: int,
    late_fraction: float = 0.2,
) -> str:
    if blew_up or negative_undershoot_events > 0:
        return "runaway_or_unphysical"

    if not timeseries_rows:
        return "runaway_or_unphysical"

    n_tail = max(1, int(len(timeseries_rows) * late_fraction))
    tail = timeseries_rows[-n_tail:]
    mean_ratio = float(np.mean([row["mean_node_ratio"] for row in tail]))
    exclusion_fraction = float(np.mean([row["exclusion_fraction"] for row in tail]))
    interface_counts = np.array([row["interface_count"] for row in tail], dtype=float)

    if mean_ratio < 0.5 and exclusion_fraction < 0.1:
        return "collapse_to_pressure"
    if mean_ratio > 2.0 and exclusion_fraction > 0.9:
        return "collapse_to_exclusion"

    if front_rows:
        late_start = tail[0]["time"]
        late_fronts = [row for row in front_rows if row["time"] >= late_start]
        late_velocities = np.array([abs(row["front_velocity"]) for row in late_fronts], dtype=float)
        if np.all(interface_counts == 1):
            mean_velocity = float(np.mean(late_velocities)) if len(late_velocities) else 0.0
            velocity_std = float(np.std(late_velocities)) if len(late_velocities) else 0.0
            if mean_velocity < 1.0e-3:
                return "stable_front"
            if mean_velocity >= 1.0e-3 and velocity_std < max(1.0e-3, 0.5 * mean_velocity):
                return "traveling_front"
        if np.max(interface_counts) > 1:
            return "multi_domain_persistent"

    if len(timeseries_rows) > 4:
        interface_diff = np.diff([row["interface_count"] for row in timeseries_rows])
        if np.any(interface_diff > 1) and np.any(interface_diff < 0):
            return "fragmenting"

        mean_eps = np.array([row["mean_eps"] for row in tail], dtype=float)
        if len(mean_eps) > 3 and float(np.std(mean_eps)) > 0.05:
            return "oscillatory_domain"

    return "undetermined"


def final_summary_row(
    run_id: str,
    classification: str,
    timeseries_rows: List[Dict[str, float]],
    front_rows: List[Dict[str, float]],
    resolution_check_pass: bool = False,
    stability_check_pass: bool = False,
) -> Dict[str, float | str | bool]:
    last = timeseries_rows[-1]
    late_window = front_rows[max(0, len(front_rows) // 2):]
    late_speed = float(np.mean([abs(row["front_velocity"]) for row in late_window])) if late_window else 0.0
    late_width = float(np.mean([row["front_width"] for row in late_window])) if late_window else 0.0
    late_sharpness = float(np.mean([row["front_sharpness"] for row in late_window])) if late_window else 0.0
    late_asymmetry = float(np.mean([row["residue_asymmetry"] for row in late_window])) if late_window else 0.0

    return {
        "run_id": run_id,
        "classification": classification,
        "final_mean_eps": last["mean_eps"],
        "final_mean_rho": last["mean_rho"],
        "final_mean_R": last["mean_R"],
        "final_exclusion_fraction": last["exclusion_fraction"],
        "final_interface_count": last["interface_count"],
        "late_time_mean_front_speed": late_speed,
        "late_time_mean_front_width": late_width,
        "late_time_mean_sharpness": late_sharpness,
        "late_time_residue_asymmetry": late_asymmetry,
        "resolution_check_pass": resolution_check_pass,
        "stability_check_pass": stability_check_pass,
    }
