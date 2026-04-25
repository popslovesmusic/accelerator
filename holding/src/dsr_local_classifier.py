from __future__ import annotations

from typing import Dict, Sequence

import numpy as np


def l2_norm(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(array))))


def safe_ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1.0e-12:
        return 0.0 if abs(numerator) <= 1.0e-12 else float("inf")
    return float(numerator / denominator)


def safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    if left.size == 0 or right.size == 0 or left.size != right.size:
        return 0.0
    left_std = float(np.std(left))
    right_std = float(np.std(right))
    if left_std <= 1.0e-12 or right_std <= 1.0e-12:
        return 1.0 if np.allclose(left, right, atol=1.0e-12, rtol=1.0e-9) else 0.0
    return float(np.corrcoef(left, right)[0, 1])


def is_floor_locked(metrics: Dict[str, float]) -> bool:
    return (
        0.95 <= float(metrics["delta_floor_ratio"]) <= 1.05
        and float(metrics["excess_floor_ratio"]) <= 0.05
        and float(metrics["delta_floor_correlation"]) >= 0.99
        and float(metrics["sign_match_fraction"]) >= 0.99
    )


def has_bounded_support(metrics: Dict[str, float]) -> bool:
    return (
        float(metrics["sigma_floor_ratio"]) <= 0.10
        and float(metrics["rho_floor_ratio"]) <= 0.10
    )


def summarize_dsr_late_tail(
    profile_times: Sequence[float],
    metrics_history: Sequence[Dict[str, float]],
    tail_fraction: float = 0.2,
    min_tail_count: int = 3,
) -> Dict[str, float]:
    time_array = np.asarray(profile_times, dtype=float)
    if time_array.size == 0 or len(metrics_history) != int(time_array.size):
        return {
            "tail_count": 0.0,
            "late_window": 0.0,
            "floor_locked_fraction": 0.0,
            "bounded_support_fraction": 0.0,
            "delta_floor_ratio_spread": float("inf"),
            "max_excess_floor_ratio": float("inf"),
            "min_delta_floor_correlation": 0.0,
            "min_sign_match_fraction": 0.0,
            "max_sigma_floor_ratio": float("inf"),
            "max_rho_floor_ratio": float("inf"),
        }

    tail_count = min(len(metrics_history), max(int(min_tail_count), int(np.ceil(len(metrics_history) * tail_fraction))))
    tail_metrics = list(metrics_history[-tail_count:])
    tail_times = time_array[-tail_count:]

    delta_floor_ratios = np.asarray([float(metric["delta_floor_ratio"]) for metric in tail_metrics], dtype=float)
    excess_floor_ratios = np.asarray([float(metric["excess_floor_ratio"]) for metric in tail_metrics], dtype=float)
    delta_floor_correlations = np.asarray([float(metric["delta_floor_correlation"]) for metric in tail_metrics], dtype=float)
    sign_match_fractions = np.asarray([float(metric["sign_match_fraction"]) for metric in tail_metrics], dtype=float)
    sigma_floor_ratios = np.asarray([float(metric["sigma_floor_ratio"]) for metric in tail_metrics], dtype=float)
    rho_floor_ratios = np.asarray([float(metric["rho_floor_ratio"]) for metric in tail_metrics], dtype=float)
    floor_locked_flags = np.asarray([is_floor_locked(metric) for metric in tail_metrics], dtype=float)
    bounded_support_flags = np.asarray([has_bounded_support(metric) for metric in tail_metrics], dtype=float)

    late_window = float(tail_times[-1] - tail_times[0]) if tail_times.size >= 2 else 0.0

    return {
        "tail_count": float(tail_count),
        "late_window": late_window,
        "floor_locked_fraction": float(np.mean(floor_locked_flags)),
        "bounded_support_fraction": float(np.mean(bounded_support_flags)),
        "delta_floor_ratio_spread": float(np.max(delta_floor_ratios) - np.min(delta_floor_ratios)),
        "max_excess_floor_ratio": float(np.max(excess_floor_ratios)),
        "min_delta_floor_correlation": float(np.min(delta_floor_correlations)),
        "min_sign_match_fraction": float(np.min(sign_match_fractions)),
        "max_sigma_floor_ratio": float(np.max(sigma_floor_ratios)),
        "max_rho_floor_ratio": float(np.max(rho_floor_ratios)),
    }


def compute_dsr_metrics(
    delta: Sequence[float],
    sigma: Sequence[float],
    rho: Sequence[float],
    depth: Sequence[float],
    delta_floor: Sequence[float],
) -> Dict[str, float]:
    delta_array = np.asarray(delta, dtype=float)
    sigma_array = np.asarray(sigma, dtype=float)
    rho_array = np.asarray(rho, dtype=float)
    depth_array = np.asarray(depth, dtype=float)
    floor_array = np.asarray(delta_floor, dtype=float)

    excess_array = delta_array - floor_array
    delta_l2 = l2_norm(delta_array)
    sigma_l2 = l2_norm(sigma_array)
    rho_l2 = l2_norm(rho_array)
    depth_l2 = l2_norm(depth_array)
    delta_floor_l2 = l2_norm(floor_array)
    excess_floor_l2 = l2_norm(excess_array)
    floor_scale = max(float(np.max(np.abs(floor_array))) if floor_array.size else 0.0, 1.0e-12)
    active_floor_mask = np.abs(floor_array) > (1.0e-6 * floor_scale)
    sign_match_fraction = 1.0
    if np.any(active_floor_mask):
        sign_match_fraction = float(np.mean(np.sign(delta_array[active_floor_mask]) == np.sign(floor_array[active_floor_mask])))

    return {
        "point_count": int(delta_array.size),
        "delta_l2": delta_l2,
        "sigma_l2": sigma_l2,
        "rho_l2": rho_l2,
        "depth_l2": depth_l2,
        "delta_floor_l2": delta_floor_l2,
        "excess_floor_l2": excess_floor_l2,
        "delta_floor_ratio": safe_ratio(delta_l2, delta_floor_l2),
        "excess_floor_ratio": safe_ratio(excess_floor_l2, delta_floor_l2),
        "delta_floor_correlation": safe_correlation(delta_array, floor_array),
        "sigma_floor_ratio": safe_ratio(sigma_l2, delta_floor_l2),
        "rho_floor_ratio": safe_ratio(rho_l2, delta_floor_l2),
        "depth_floor_ratio": safe_ratio(depth_l2, delta_floor_l2),
        "sigma_rho_ratio": safe_ratio(sigma_l2, rho_l2),
        "depth_span": float(np.max(depth_array) - np.min(depth_array)) if depth_array.size else 0.0,
        "floor_active_fraction": float(np.mean(active_floor_mask)) if floor_array.size else 0.0,
        "sign_match_fraction": sign_match_fraction,
        "mean_delta": float(np.mean(delta_array)) if delta_array.size else 0.0,
        "mean_sigma": float(np.mean(sigma_array)) if sigma_array.size else 0.0,
        "mean_rho": float(np.mean(rho_array)) if rho_array.size else 0.0,
        "mean_depth": float(np.mean(depth_array)) if depth_array.size else 0.0,
    }
def classify_dsr_metrics(
    metrics: Dict[str, float],
    ratchet_event_steps: int,
    seed_update_steps: int,
    late_tail_summary: Dict[str, float] | None = None,
) -> Dict[str, object]:
    floor_locked = is_floor_locked(metrics)
    bounded_support = has_bounded_support(metrics)
    event_stable = (
        int(ratchet_event_steps) <= 3
        and int(seed_update_steps) <= 3
        and int(seed_update_steps) <= int(ratchet_event_steps) + 1
    )
    late_tail_stable = True
    if late_tail_summary is not None:
        late_tail_stable = (
            float(late_tail_summary["tail_count"]) >= 3.0
            and float(late_tail_summary["late_window"]) >= 5.0
            and float(late_tail_summary["floor_locked_fraction"]) >= 1.0
            and float(late_tail_summary["bounded_support_fraction"]) >= 1.0
            and float(late_tail_summary["delta_floor_ratio_spread"]) <= 0.02
            and float(late_tail_summary["max_excess_floor_ratio"]) <= 0.05
            and float(late_tail_summary["min_delta_floor_correlation"]) >= 0.99
            and float(late_tail_summary["min_sign_match_fraction"]) >= 0.99
            and float(late_tail_summary["max_sigma_floor_ratio"]) <= 0.10
            and float(late_tail_summary["max_rho_floor_ratio"]) <= 0.10
        )

    if floor_locked and bounded_support and event_stable and late_tail_stable:
        label = "bounded_relational_stable"
        converged = True
    elif floor_locked and bounded_support and event_stable:
        label = "late_tail_unstable"
        converged = False
    elif floor_locked and not event_stable:
        label = "event_gating_unstable"
        converged = False
    elif floor_locked:
        label = "floor_locked_unbounded_support"
        converged = False
    else:
        label = "floor_deviant"
        converged = False

    return {
        "label": label,
        "converged": converged,
        "floor_locked": floor_locked,
        "bounded_support": bounded_support,
        "event_stable": event_stable,
        "late_tail_stable": late_tail_stable,
    }
