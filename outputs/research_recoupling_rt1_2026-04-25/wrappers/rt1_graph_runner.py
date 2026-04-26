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

from graph_dynamics_sim_v1.network_engine import NetworkDynamics


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run(config_path: str, out_dir: str) -> None:
    with open(config_path, "r") as f:
        cfg = json.load(f)

    engine_cfg = cfg["engine_config"]
    rt1_cfg = cfg.get("rt1", {})
    trace_window_steps = int(rt1_cfg.get("trace_window_steps", 200))
    record_every = int(rt1_cfg.get("record_every", 1))

    _ensure_dir(out_dir)

    seed = int(engine_cfg.get("seed", 42))
    np.random.seed(seed)

    n = int(engine_cfg["n_nodes"])
    phi = np.random.uniform(0, 2 * np.pi, n)
    net = NetworkDynamics(engine_cfg)

    steps = int(engine_cfg["steps"])
    dt = float(engine_cfg["dt"])

    candidate_history = deque(maxlen=trace_window_steps + 1)
    history_rows: list[dict] = []

    inadmissible_edge_add_violations_total = 0
    edge_add_events_total = 0
    traceability_failures_total = 0

    inadmissible_edge_add_fraction_max = 0.0
    traceability_failure_fraction_max = 0.0

    for step in range(steps):
        # 1) Update phases (admissibility is evaluated on the phase state that determines rewiring)
        phi = net.step_phi(phi, dt)

        # 2) Compute admissibility for recoupling candidates before rewiring
        dphi_mat = phi[np.newaxis, :] - phi[:, np.newaxis]
        stress = np.abs(np.sin(dphi_mat))
        A_before = net.A.copy()

        theta_recouple = float(engine_cfg["recouple_threshold"])
        candidate_recouple = (stress < theta_recouple) & (A_before == 0)
        np.fill_diagonal(candidate_recouple, False)

        candidate_history.appendleft(candidate_recouple.copy())

        # 3) Rewire (engine uses its own stochasticity)
        net.rewire(phi)
        A_after = net.A

        # 4) Events + RT-1 checks
        edge_added = (A_after == 1) & (A_before == 0)
        np.fill_diagonal(edge_added, False)

        # Only count each undirected edge once
        triu = np.triu_indices(n, k=1)
        edge_added_count = int(np.sum(edge_added[triu]))
        candidate_count = int(np.sum(candidate_recouple[triu]))

        inadmissible_added = edge_added & (~candidate_recouple)
        inadmissible_added_count = int(np.sum(inadmissible_added[triu]))

        edge_add_events_total += edge_added_count
        inadmissible_edge_add_violations_total += inadmissible_added_count

        inadmissible_edge_add_fraction = inadmissible_added_count / max(1, edge_added_count)
        inadmissible_edge_add_fraction_max = max(inadmissible_edge_add_fraction_max, inadmissible_edge_add_fraction)

        # Traceability: for each added edge, check it was a candidate within the trace window (including current step)
        traceability_failures = 0
        trace_depth_sum = 0
        trace_depth_count = 0
        if edge_added_count > 0:
            added_pairs = np.argwhere(np.triu(edge_added, k=1))
            for (i, j) in added_pairs:
                found = False
                for lag, past_candidates in enumerate(candidate_history):
                    if past_candidates[i, j]:
                        trace_depth_sum += lag
                        trace_depth_count += 1
                        found = True
                        break
                if not found:
                    traceability_failures += 1

        traceability_failures_total += traceability_failures
        traceability_failure_fraction = traceability_failures / max(1, edge_added_count)
        traceability_failure_fraction_max = max(traceability_failure_fraction_max, traceability_failure_fraction)

        # Base metrics
        degrees = np.sum(A_after, axis=1)
        avg_degree = float(np.mean(degrees))
        edge_count = int(np.sum(A_after) // 2)
        order_param = float(np.abs(np.mean(np.exp(1j * phi))))

        recouple_asymmetry = (edge_added_count / candidate_count) if candidate_count else 0.0

        if step % record_every == 0:
            history_rows.append(
                {
                    "step": step,
                    "time": step * dt,
                    "order_parameter": order_param,
                    "edge_count": edge_count,
                    "avg_degree": avg_degree,
                    "candidate_pairs": candidate_count,
                    "edge_added": edge_added_count,
                    "recouple_asymmetry": recouple_asymmetry,
                    "inadmissible_edge_added": inadmissible_added_count,
                    "inadmissible_edge_add_fraction": inadmissible_edge_add_fraction,
                    "traceability_failures": traceability_failures,
                    "traceability_failure_fraction": traceability_failure_fraction,
                    "trace_depth_mean": (trace_depth_sum / trace_depth_count) if trace_depth_count else 0.0,
                }
            )

    pd.DataFrame(history_rows).to_csv(os.path.join(out_dir, "metrics.csv"), index=False)

    final_row = history_rows[-1] if history_rows else {}
    final_row = dict(final_row)
    final_row.update(
        {
            "inadmissible_edge_add_fraction_max": inadmissible_edge_add_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max,
        }
    )
    summary = {
        "engine": cfg.get("engine", "graph_dynamics_sim_v1"),
        "config_path": os.path.abspath(config_path),
        "out_dir": os.path.abspath(out_dir),
        "config": cfg,
        "final_metrics": final_row,
        "rt1_final": {
            "edge_add_events_total": edge_add_events_total,
            "inadmissible_edge_add_violations_total": inadmissible_edge_add_violations_total,
            "traceability_failures_total": traceability_failures_total,
            "inadmissible_edge_add_fraction_max": inadmissible_edge_add_fraction_max,
            "traceability_failure_fraction_max": traceability_failure_fraction_max
        },
        "status": "completed"
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="RT-1 wrapper runner for graph_dynamics_sim_v1")
    parser.add_argument("--config", required=True, help="Path to RT-1 wrapper config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()
