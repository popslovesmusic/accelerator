import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fsa_rule_engine_sim_v1.fsa_engine import FSAAgent, RuleEngine


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def run(config_path: str, out_dir: str) -> None:
    with open(config_path, "r") as f:
        cfg = json.load(f)

    engine_cfg = cfg["engine_config"]
    cdhds_cfg = cfg.get("cdhds", {})
    record_every = int(cdhds_cfg.get("record_every", 1))
    epsilon_zero_state = int(cdhds_cfg.get("epsilon_zero_state", 0))

    seed = int(engine_cfg.get("seed", 42))
    np.random.seed(seed)

    _ensure_dir(out_dir)

    engine = RuleEngine(engine_cfg)
    n_agents = int(engine_cfg["n_agents"])
    steps = int(engine_cfg["steps"])

    agents = [FSAAgent(start_node=1) for _ in range(n_agents)]

    history_rows: list[dict] = []

    forbidden_occupancy_events_total = 0
    transitions_from_forbidden_total = 0
    transitions_to_forbidden_total = 0
    active_without_admissible_continuation_total = 0

    for step in range(steps):
        before_states = np.array([a.current_state for a in agents], dtype=int)
        before_active = np.array([1 if a.active else 0 for a in agents], dtype=int)

        # Check forbidden occupancy before stepping (should be 0 if rules hold).
        forbidden_before = int(np.sum((before_states == epsilon_zero_state) & (before_active == 1)))
        if forbidden_before:
            forbidden_occupancy_events_total += forbidden_before

        # For active agents, check that an admissible continuation exists (existence ⇒ mapping).
        no_cont = 0
        for a in agents:
            if not a.active:
                continue
            if not engine.get_admissible_continuations(a.current_state, a.residue):
                no_cont += 1
        active_without_admissible_continuation_total += no_cont

        # Step all agents.
        for a in agents:
            a.step(engine)

        after_states = np.array([a.current_state for a in agents], dtype=int)
        after_active = np.array([1 if a.active else 0 for a in agents], dtype=int)

        transitioned = (before_active == 1) & (after_active == 1) & (after_states != before_states)
        transitions_count = int(np.sum(transitioned))

        from_forbidden = int(np.sum(transitioned & (before_states == epsilon_zero_state)))
        to_forbidden = int(np.sum(transitioned & (after_states == epsilon_zero_state)))
        transitions_from_forbidden_total += from_forbidden
        transitions_to_forbidden_total += to_forbidden

        active_count = int(np.sum(after_active))
        mean_residue = float(np.mean([a.residue for a in agents if a.active])) if active_count else 0.0

        if step % record_every == 0:
            history_rows.append(
                {
                    "step": step,
                    "active_count": active_count,
                    "mean_residue": mean_residue,
                    "transitions_count": transitions_count,
                    "forbidden_active_before": forbidden_before,
                    "active_without_admissible_continuation": no_cont,
                    "transitions_from_forbidden": from_forbidden,
                    "transitions_to_forbidden": to_forbidden,
                }
            )

    pd.DataFrame(history_rows).to_csv(os.path.join(out_dir, "metrics.csv"), index=False)

    final_row = dict(history_rows[-1] if history_rows else {})
    final_row.update(
        {
            "forbidden_occupancy_events_total": forbidden_occupancy_events_total,
            "transitions_from_forbidden_total": transitions_from_forbidden_total,
            "transitions_to_forbidden_total": transitions_to_forbidden_total,
            "active_without_admissible_continuation_total": active_without_admissible_continuation_total,
        }
    )
    summary = {
        "engine": cfg.get("engine", "fsa_rule_engine_sim_v1"),
        "config_path": os.path.abspath(config_path),
        "out_dir": os.path.abspath(out_dir),
        "config": cfg,
        "final_metrics": final_row,
        "cdhds_final": {
            "forbidden_occupancy_events_total": forbidden_occupancy_events_total,
            "transitions_from_forbidden_total": transitions_from_forbidden_total,
            "transitions_to_forbidden_total": transitions_to_forbidden_total,
            "active_without_admissible_continuation_total": active_without_admissible_continuation_total,
        },
        "status": "completed",
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="CDHDS wrapper runner for fsa_rule_engine_sim_v1")
    parser.add_argument("--config", required=True, help="Path to CDHDS wrapper config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.config, args.out)


if __name__ == "__main__":
    main()
