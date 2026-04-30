import argparse
import json
import os
from collections import deque

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rd_moving_boundary_sim_v1.rd_engine import RDEngine


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _pearson_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a.reshape(-1).astype(float)
    b = b.reshape(-1).astype(float)
    if a.size != b.size or a.size == 0:
        return float("nan")
    a0 = a - np.mean(a)
    b0 = b - np.mean(b)
    denom = np.sqrt(np.sum(a0 * a0) * np.sum(b0 * b0))
    if denom <= 0:
        return float("nan")
    return float(np.sum(a0 * b0) / denom)


def run(config_path: str, out_dir: str) -> None:
    with open(config_path, "r") as f:
        cfg = json.load(f)

    engine_cfg = cfg["engine_config"]
    noise_cfg = cfg.get("initial_noise", {})
    rt1_cfg = cfg.get("rt1", {})

    epsilon_floor = float(rt1_cfg.get("epsilon_floor", 1e-6))
    D_thresh = float(rt1_cfg.get("domain_admissibility_thresh", 0.1))
    trace_window_steps = int(rt1_cfg.get("trace_window_steps", 100))
    record_every = int(rt1_cfg.get("record_every", 1))

    seed = int(engine_cfg.get("seed", 42))
    rng = np.random.default_rng(seed)

    _ensure_dir(out_dir)

    rd = RDEngine(engine_cfg)

    domain_noise_std = float(noise_cfg.get("domain_noise_std", 0.0))
    signal_noise_std = float(noise_cfg.get("signal_noise_std", 0.0))

    if domain_noise_std > 0.0:
        rd.D = np.clip(rd.D + rng.normal(scale=domain_noise_std, size=rd.D.shape), 0.0, 1.0)
    if signal_noise_std > 0.0:
        rd.S = np.maximum(rd.S + rng.normal(scale=signal_noise_std, size=rd.S.shape), 0.0)

    steps = int(engine_cfg["steps"])
    dt = float(engine_cfg["dt"])

    admissible_history = deque(maxlen=trace_window_steps + 1)
    history_rows: list[dict] = []

    inadmissible_activation_violations_total = 0
    activation_events_total = 0
    traceability_failures_total = 0

    inadmissible_activation_fraction_max = 0.0
    signal_outside_domain_fraction_max = 0.0
    traceability_failure_fraction_max = 0.0

    D_sum = np.zeros_like(rd.D, dtype=float)

    for step in range(steps):
        D_before = rd.D.copy()
        S_before = rd.S.copy()

        admissible_before = D_before > D_thresh
        admissible_history.appendleft(admissible_before.copy())

        rd.step()

        D_after = rd.D
        S_after = rd.S
        D_sum += D_after

        # Activation: S crosses epsilon_floor from below to above.
        was_inactive = S_before <= epsilon_floor
        is_active = S_after > epsilon_floor
        newly_activated = was_inactive & is_active

        activation_events = int(np.sum(newly_activated))
        activation_events_total += activation_events

        inadmissible_activation = newly_activated & (~admissible_before)
        inadmissible_activation_count = int(np.sum(inadmissible_activation))
        inadmissible_activation_violations_total += inadmissible_activation_count

        inadmissible_activation_fraction = inadmissible_activation_count / max(1, activation_events)
        inadmissible_activation_fraction_max = max(inadmissible_activation_fraction_max, inadmissible_activation_fraction)

        # P1 (continuous-style): signal mass outside admissible domain at current time.
        outside = (D_after <= D_thresh) & (S_after > epsilon_floor)
        outside_mass = float(np.sum(S_after[outside]))
        total_mass = float(np.sum(S_after))
        signal_outside_domain_fraction = outside_mass / total_mass if total_mass > 0 else 0.0
        signal_outside_domain_fraction_max = max(signal_outside_domain_fraction_max, signal_outside_domain_fraction)

        # Traceability: newly activated cells should have an admissible precursor in window.
        traceability_failures = 0
        trace_depth_sum = 0
        trace_depth_count = 0
        if activation_events > 0:
            idxs = np.argwhere(newly_activated)
            for (i, j) in idxs:
                found = False
                for lag, past_adm in enumerate(admissible_history):
                    if past_adm[i, j]:
                        trace_depth_sum += lag
                        trace_depth_count += 1
                        found = True
                        break
                if not found:
                    traceability_failures += 1

        traceability_failures_total += traceability_failures
        traceability_failure_fraction = traceability_failures / max(1, activation_events)
        traceability_failure_fraction_max = max(traceability_failure_fraction_max, traceability_failure_fraction)

        base_metrics = rd.get_metrics()
        if step % record_every == 0:
            history_rows.append(
                {
                    "step": step,
                    "time": step * dt,
                    "active_area": float(base_metrics.get("active_area", 0.0)),
                    "total_signal": float(base_metrics.get("total_signal", 0.0)),
                    "max_signal": float(base_metrics.get("max_signal", 0.0)),
                    "activation_events": activation_events,
                    "inadmissible_activation_count": inadmissible_activation_count,
                    "inadmissible_activation_fraction": inadmissible_activation_fraction,
                    "signal_outside_domain_fraction": signal_outside_domain_fraction,
                    "traceability_failures": traceability_failures,
                    "traceability_failure_fraction": traceability_failure_fraction,
                    "trace_depth_mean": (trace_depth_sum / trace_depth_count) if trace_depth_count else 0.0,
                    "admissible_area_fraction": float(np.mean(admissible_before)),
                    "signal_active_fraction": float(np.mean(S_after > epsilon_floor)),
                }
            )

    pd.DataFrame(history_rows).to_csv(os.path.join(out_dir, "metrics.csv"), index=False)

    D_avg = D_sum / max(1, steps)
    corridor_signal_corr = _pearson_corr(D_avg, (rd.S > epsilon_floor).astype(float))

    final_row = history_rows[-1] if history_rows else {}
    final_row = dict(final_row)
    final_row.update(
        {
            "inadmissible_activation_fraction_max": inadmissible_activation_fraction_max,
            "signal_outside_domain_fraction_max": signal_outside_domain_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max,
            "corridor_signal_corr": corridor_signal_corr,
        }
    )
    summary = {
        "engine": cfg.get("engine", "rd_moving_boundary_sim_v1"),
        "config_path": os.path.abspath(config_path),
        "out_dir": os.path.abspath(out_dir),
        "config": cfg,
        "final_metrics": final_row,
        "rt1_final": {
            "activation_events_total": activation_events_total,
            "inadmissible_activation_violations_total": inadmissible_activation_violations_total,
            "traceability_failures_total": traceability_failures_total,
            "inadmissible_activation_fraction_max": inadmissible_activation_fraction_max,
            "signal_outside_domain_fraction_max": signal_outside_domain_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max,
            "corridor_signal_corr": corridor_signal_corr
        },
        "status": "completed"
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="RT-1 wrapper runner for rd_moving_boundary_sim_v1")
    parser.add_argument("--config", required=True, help="Path to RT-1 wrapper config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()
