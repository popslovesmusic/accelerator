import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rd_moving_boundary_sim_v1.rd_engine import RDEngine


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run(config_path: str, out_dir: str) -> None:
    with open(config_path, "r") as f:
        cfg = json.load(f)

    engine_cfg = cfg["engine_config"]
    noise_cfg = cfg.get("initial_noise", {})
    cdhds_cfg = cfg.get("cdhds", {})

    epsilon_floor = float(cdhds_cfg.get("epsilon_floor", 1e-6))
    D_thresh = float(cdhds_cfg.get("domain_admissibility_thresh", 0.1))
    recouple_window_steps = int(cdhds_cfg.get("recouple_window_steps", 50))
    record_every = int(cdhds_cfg.get("record_every", 1))

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

    # Pending outside-activation events that must be "recoupled" (D crosses threshold) within window.
    # Store as dict: (i,j) -> remaining_steps
    pending: dict[tuple[int, int], int] = {}

    history_rows: list[dict] = []

    outside_activation_events_total = 0
    outside_activation_recoupled_total = 0
    outside_activation_no_recouple_total = 0
    delta_recouple_events_total = 0

    outside_activation_no_recouple_fraction_max = 0.0
    signal_outside_domain_fraction_max = 0.0

    for step in range(steps):
        D_before = rd.D.copy()
        S_before = rd.S.copy()

        admissible_before = D_before > D_thresh
        forbidden_before = ~admissible_before

        rd.step()

        D_after = rd.D
        S_after = rd.S

        # Define activation event on S crossing floor from below -> above.
        was_inactive = S_before <= epsilon_floor
        is_active = S_after > epsilon_floor
        newly_activated = was_inactive & is_active

        outside_new_activation = newly_activated & forbidden_before
        outside_new_count = int(np.sum(outside_new_activation))
        outside_activation_events_total += outside_new_count

        # Add to pending set
        if outside_new_count > 0:
            for (i, j) in np.argwhere(outside_new_activation):
                pending[(int(i), int(j))] = recouple_window_steps

        # Delta event: local recoupling when D crosses threshold from forbidden -> admissible.
        delta_recouple = (D_before <= D_thresh) & (D_after > D_thresh)
        delta_recouple_events_total += int(np.sum(delta_recouple))

        # Check pending events: did they recouple this step?
        recoupled_now = []
        for (i, j), remaining in list(pending.items()):
            if D_after[i, j] > D_thresh:
                recoupled_now.append((i, j))
                del pending[(i, j)]
                outside_activation_recoupled_total += 1
            else:
                remaining -= 1
                if remaining <= 0:
                    del pending[(i, j)]
                    outside_activation_no_recouple_total += 1
                else:
                    pending[(i, j)] = remaining

        outside_activation_no_recouple_fraction = outside_activation_no_recouple_total / max(1, outside_activation_events_total)
        outside_activation_no_recouple_fraction_max = max(
            outside_activation_no_recouple_fraction_max, outside_activation_no_recouple_fraction
        )

        # Mass fraction of signal outside admissible domain (after step).
        outside_after = (D_after <= D_thresh) & (S_after > epsilon_floor)
        outside_mass = float(np.sum(S_after[outside_after]))
        total_mass = float(np.sum(S_after))
        signal_outside_domain_fraction = outside_mass / total_mass if total_mass > 0 else 0.0
        signal_outside_domain_fraction_max = max(signal_outside_domain_fraction_max, signal_outside_domain_fraction)

        if step % record_every == 0:
            base_metrics = rd.get_metrics()
            history_rows.append(
                {
                    "step": step,
                    "time": step * dt,
                    "active_area": float(base_metrics.get("active_area", 0.0)),
                    "total_signal": float(base_metrics.get("total_signal", 0.0)),
                    "max_signal": float(base_metrics.get("max_signal", 0.0)),
                    "delta_recouple_events": int(np.sum(delta_recouple)),
                    "outside_activation_events": outside_new_count,
                    "pending_outside_activations": int(len(pending)),
                    "outside_activation_no_recouple_total": outside_activation_no_recouple_total,
                    "outside_activation_events_total": outside_activation_events_total,
                    "outside_activation_no_recouple_fraction": outside_activation_no_recouple_fraction,
                    "signal_outside_domain_fraction": signal_outside_domain_fraction,
                }
            )

    pd.DataFrame(history_rows).to_csv(os.path.join(out_dir, "metrics.csv"), index=False)

    final_row = dict(history_rows[-1] if history_rows else {})
    final_row.update(
        {
            "outside_activation_no_recouple_fraction_max": outside_activation_no_recouple_fraction_max,
            "signal_outside_domain_fraction_max": signal_outside_domain_fraction_max,
        }
    )

    summary = {
        "engine": cfg.get("engine", "rd_moving_boundary_sim_v1"),
        "config_path": os.path.abspath(config_path),
        "out_dir": os.path.abspath(out_dir),
        "config": cfg,
        "final_metrics": final_row,
        "cdhds_final": {
            "outside_activation_events_total": outside_activation_events_total,
            "outside_activation_recoupled_total": outside_activation_recoupled_total,
            "outside_activation_no_recouple_total": outside_activation_no_recouple_total,
            "outside_activation_no_recouple_fraction_max": outside_activation_no_recouple_fraction_max,
            "delta_recouple_events_total": delta_recouple_events_total,
            "signal_outside_domain_fraction_max": signal_outside_domain_fraction_max,
        },
        "status": "completed",
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="CDHDS wrapper runner for rd_moving_boundary_sim_v1")
    parser.add_argument("--config", required=True, help="Path to CDHDS wrapper config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()

