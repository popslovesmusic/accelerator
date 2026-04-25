from __future__ import annotations


DEFAULT_THRESHOLDS = {
    "epsilon_collapse_threshold": 1e-3,
    "settling_window_fraction": 0.1,
    "steady_tolerance": 1e-3,
    "oscillation_amplitude_threshold": 1e-2,
    "runaway_threshold": 1e3,
}


def classify_ode_run(timeseries: list[dict], thresholds: dict | None = None) -> str:
    rules = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    epsilon_values = [row["epsilon"] for row in timeseries]
    rho_values = [row["rho"] for row in timeseries]
    labels = set(rules.get("labels", []))

    if max(abs(value) for value in epsilon_values + rho_values) >= rules["runaway_threshold"]:
        return "runaway"

    tail_start = max(0, int(len(epsilon_values) * (1.0 - rules["settling_window_fraction"])))
    tail = epsilon_values[tail_start:]
    tail_span = max(tail) - min(tail)
    tail_mean = sum(tail) / len(tail)
    final_epsilon = epsilon_values[-1]
    final_rho = rho_values[-1]

    if "near_floor_persistent" in labels or "near_floor_oscillatory" in labels or "near_floor_convergent" in labels:
        relative_threshold = float(rules.get("near_floor_band_relative_threshold", 0.01))
        near_floor_limit = max(rules["epsilon_collapse_threshold"] * 10.0, tail_mean * (1.0 + relative_threshold))
        if final_epsilon <= near_floor_limit:
            if "near_floor_convergent" in labels and tail_span <= rules["oscillation_amplitude_threshold"]:
                return "near_floor_convergent"
            if tail_span >= rules["oscillation_amplitude_threshold"]:
                return "near_floor_oscillatory"
            return "near_floor_persistent"
        if tail_span <= rules["steady_tolerance"]:
            return "persistent_above_floor"
        return "other_transitional"

    if final_epsilon <= rules["epsilon_collapse_threshold"] and final_rho > final_epsilon:
        return "collapse_to_pressure"
    if final_epsilon > rules["epsilon_collapse_threshold"] and tail_span <= rules["steady_tolerance"]:
        return "persistent_steady"
    if final_epsilon > rules["epsilon_collapse_threshold"] and tail_span >= rules["oscillation_amplitude_threshold"]:
        return "oscillatory_persistent"
    return "other_transitional"
