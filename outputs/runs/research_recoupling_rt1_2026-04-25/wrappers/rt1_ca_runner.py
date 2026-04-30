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

from ca_admissibility_sim_v1.ca_engine import AdmissibilityCA


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _as_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return float("nan")


def run(config_path: str, out_dir: str) -> None:
    with open(config_path, "r") as f:
        cfg = json.load(f)

    engine_cfg = cfg["engine_config"]
    rt1_cfg = cfg.get("rt1", {})
    epsilon_floor = float(rt1_cfg.get("epsilon_floor", 1e-6))
    trace_window_steps = int(rt1_cfg.get("trace_window_steps", 50))
    record_every = int(rt1_cfg.get("record_every", 1))

    _ensure_dir(out_dir)

    ca = AdmissibilityCA(engine_cfg)
    steps = int(engine_cfg["steps"])

    admissible_history = deque(maxlen=trace_window_steps + 1)
    history_rows: list[dict] = []

    inadmissible_update_violations_total = 0
    inadmissible_activation_violations_total = 0
    traceability_failures_total = 0
    activation_events_total = 0

    inadmissible_update_fraction_max = 0.0
    inadmissible_activation_fraction_max = 0.0
    traceability_failure_fraction_max = 0.0

    eps_prev = ca.epsilon.copy()

    for step in range(steps):
        eps_before = ca.epsilon.copy()
        admissible_mask = ca.step().astype(bool)
        eps_after = ca.epsilon

        # "Update happened where inadmissible" should be impossible in this engine.
        delta_eps = eps_after - eps_before
        updated = np.abs(delta_eps) > 0.0
        inadmissible_update = updated & (~admissible_mask)

        # Activation event: |epsilon| crosses epsilon_floor from below to above.
        was_inactive = np.abs(eps_before) <= epsilon_floor
        is_active = np.abs(eps_after) > epsilon_floor
        newly_activated = was_inactive & is_active

        # RT-1 Prediction 1 check (operational): newly_activated implies admissible at that step.
        inadmissible_activation = newly_activated & (~admissible_mask)

        # RT-1 Prediction 2 check (operational): for each newly activated cell, find whether it had
        # an admissible precursor within the trace window (including current step as lag=0).
        admissible_history.appendleft(admissible_mask.copy())
        traceability_failures = np.zeros_like(newly_activated, dtype=bool)
        trace_depth_sum = 0
        trace_depth_count = 0

        if np.any(newly_activated):
            active_idxs = np.argwhere(newly_activated)
            for (i, j) in active_idxs:
                found = False
                for lag, past_mask in enumerate(admissible_history):
                    if past_mask[i, j]:
                        trace_depth_sum += lag
                        trace_depth_count += 1
                        found = True
                        break
                if not found:
                    traceability_failures[i, j] = True

        activation_events = int(np.sum(newly_activated))
        admissible_cells = int(np.sum(admissible_mask))
        inadmissible_update_count = int(np.sum(inadmissible_update))
        inadmissible_activation_count = int(np.sum(inadmissible_activation))
        traceability_failure_count = int(np.sum(traceability_failures))

        activation_events_total += activation_events
        inadmissible_update_violations_total += inadmissible_update_count
        inadmissible_activation_violations_total += inadmissible_activation_count
        traceability_failures_total += traceability_failure_count

        inadmissible_update_fraction = inadmissible_update_count / max(1, eps_after.size)
        inadmissible_activation_fraction = inadmissible_activation_count / max(1, activation_events)
        traceability_failure_fraction = traceability_failure_count / max(1, activation_events)

        inadmissible_update_fraction_max = max(inadmissible_update_fraction_max, inadmissible_update_fraction)
        inadmissible_activation_fraction_max = max(inadmissible_activation_fraction_max, inadmissible_activation_fraction)
        traceability_failure_fraction_max = max(traceability_failure_fraction_max, traceability_failure_fraction)

        if step % record_every == 0:
            # Mirror engine's metrics for convenience
            engine_metrics = ca.get_metrics(admissible_mask)
            history_rows.append(
                {
                    "step": step,
                    "active_fraction": _as_float(engine_metrics.get("active_fraction")),
                    "mean_mismatch": _as_float(engine_metrics.get("mean_mismatch")),
                    "mean_residue": _as_float(engine_metrics.get("mean_residue")),
                    "admissible_cells": admissible_cells,
                    "activation_events": activation_events,
                    "activation_fraction_of_admissible": activation_events / max(1, admissible_cells),
                    "inadmissible_update_count": inadmissible_update_count,
                    "inadmissible_update_fraction": inadmissible_update_fraction,
                    "inadmissible_activation_count": inadmissible_activation_count,
                    "inadmissible_activation_fraction": inadmissible_activation_fraction,
                    "traceability_failure_count": traceability_failure_count,
                    "traceability_failure_fraction": traceability_failure_fraction,
                    "trace_depth_mean": (trace_depth_sum / trace_depth_count) if trace_depth_count else 0.0,
                }
            )

        eps_prev = eps_after.copy()

    pd.DataFrame(history_rows).to_csv(os.path.join(out_dir, "metrics.csv"), index=False)

    final_row = history_rows[-1] if history_rows else {}
    final_row = dict(final_row)
    final_row.update(
        {
            "inadmissible_update_fraction_max": inadmissible_update_fraction_max,
            "inadmissible_activation_fraction_max": inadmissible_activation_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max,
        }
    )
    summary = {
        "engine": cfg.get("engine", "ca_admissibility_sim_v1"),
        "config_path": os.path.abspath(config_path),
        "out_dir": os.path.abspath(out_dir),
        "config": cfg,
        "final_metrics": final_row,
        "rt1_final": {
            "activation_events_total": activation_events_total,
            "inadmissible_update_violations_total": inadmissible_update_violations_total,
            "inadmissible_activation_violations_total": inadmissible_activation_violations_total,
            "traceability_failures_total": traceability_failures_total,
            "inadmissible_update_fraction_max": inadmissible_update_fraction_max,
            "inadmissible_activation_fraction_max": inadmissible_activation_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max
        },
        "status": "completed"
    }

    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="RT-1 wrapper runner for ca_admissibility_sim_v1")
    parser.add_argument("--config", required=True, help="Path to RT-1 wrapper config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()
