from __future__ import annotations


def build_ode_summary(config: dict, timeseries: list[dict], regime: str, collapse_time: str) -> dict:
    epsilon_values = [row["epsilon"] for row in timeseries]
    rho_values = [row["rho"] for row in timeseries]
    residue_values = [row["residue"] for row in timeseries]
    thresholds = config.get("classifier_settings", {})
    settle_fraction = float(
        thresholds.get("persistence_settle_window_fraction", thresholds.get("settling_window_fraction", 0.1))
    )
    tail_start = max(0, int(len(epsilon_values) * (1.0 - settle_fraction)))
    tail_epsilon = epsilon_values[tail_start:]
    epsilon_min = min(epsilon_values)
    epsilon_argmin_index = epsilon_values.index(epsilon_min)
    epsilon_argmin_time = timeseries[epsilon_argmin_index]["t"]
    epsilon_last_window_mean = sum(tail_epsilon) / len(tail_epsilon)
    epsilon_last_window_min = min(tail_epsilon)
    epsilon_last_window_max = max(tail_epsilon)
    epsilon_last_window_std = (
        sum((value - epsilon_last_window_mean) ** 2 for value in tail_epsilon) / len(tail_epsilon)
    ) ** 0.5
    near_floor_bandwidth = epsilon_last_window_max - epsilon_last_window_min
    near_floor_oscillation_amplitude = 0.5 * near_floor_bandwidth
    near_floor_threshold = epsilon_last_window_mean * 1.05 if epsilon_last_window_mean > 0 else epsilon_last_window_max
    time_to_near_floor_window = next(
        (row["t"] for row in timeseries if row["epsilon"] <= near_floor_threshold),
        timeseries[-1]["t"],
    )
    sorted_tail = sorted(set(round(value, 12) for value in tail_epsilon))
    delta_epsilon_min_resolved = (
        min(sorted_tail[index + 1] - sorted_tail[index] for index in range(len(sorted_tail) - 1))
        if len(sorted_tail) > 1
        else 0.0
    )

    return {
        "run_id": config["run_id"],
        "equation_mode": config["equation_mode"],
        "experiment_family": config["experiment_family"],
        "stage_id": config.get("stage_id", ""),
        "initial_condition_family": config.get("initial_condition_family", ""),
        "seed": config["seed"],
        "epsilon_final": epsilon_values[-1],
        "rho_final": rho_values[-1],
        "residue_final": residue_values[-1],
        "epsilon_mean": sum(epsilon_values) / len(epsilon_values),
        "rho_mean": sum(rho_values) / len(rho_values),
        "residue_mean": sum(residue_values) / len(residue_values),
        "epsilon_max": max(epsilon_values),
        "rho_max": max(rho_values),
        "residue_max": max(residue_values),
        "epsilon_min_observed": epsilon_min,
        "epsilon_argmin_time": epsilon_argmin_time,
        "epsilon_last_window_mean": epsilon_last_window_mean,
        "epsilon_last_window_std": epsilon_last_window_std,
        "epsilon_last_window_min": epsilon_last_window_min,
        "epsilon_last_window_max": epsilon_last_window_max,
        "epsilon_floor_estimate": epsilon_last_window_mean,
        "near_floor_bandwidth": near_floor_bandwidth,
        "near_floor_oscillation_amplitude": near_floor_oscillation_amplitude,
        "time_to_near_floor_window": time_to_near_floor_window,
        "delta_epsilon_min_resolved": delta_epsilon_min_resolved,
        "rho_negative_flag": any(value < 0.0 for value in rho_values),
        "collapse_time": collapse_time,
        "regime_classification": regime,
    }
