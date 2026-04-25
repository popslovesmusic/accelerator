from __future__ import annotations

import argparse
import json
import math
import subprocess
from datetime import datetime, UTC
from pathlib import Path

from classifier import DEFAULT_THRESHOLDS, classify_ode_run
from integrators import euler_step, rk4_step
from initial_conditions import build_initial_state
from io_schema import (
    compute_sha256,
    ensure_run_directory,
    write_json,
    write_run_summary_markdown,
    write_summary_csv,
    write_timeseries_csv,
)
from metrics import build_ode_summary
from model import OdeParameters, ode_rhs


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "artifacts" / "runs"


def load_config(config_path: Path) -> tuple[dict, str]:
    raw_text = config_path.read_text(encoding="utf-8")
    return json.loads(raw_text), raw_text


def get_code_version() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "untracked"


def validate_config(config: dict) -> None:
    required_top_level = [
        "run_id",
        "experiment_family",
        "equation_mode",
        "parameters",
        "time_settings",
        "initial_conditions",
        "seed",
        "notes",
    ]
    for field in required_top_level:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    required_parameters = ["k", "b", "c", "alpha", "beta", "gamma", "v", "s", "h", "kappa", "lambda"]
    required_time = ["dt", "t_final", "sample_every"]
    required_initial = ["epsilon0", "rho0", "R0"]

    for field in required_parameters:
        if field not in config["parameters"]:
            raise ValueError(f"Missing required parameter field: {field}")
    for field in required_time:
        if field not in config["time_settings"]:
            raise ValueError(f"Missing required time_settings field: {field}")
    for field in required_initial:
        if field not in config["initial_conditions"]:
            raise ValueError(f"Missing required initial_conditions field: {field}")

    if "termination_rules" in config:
        if "runaway_epsilon_threshold" not in config["termination_rules"]:
            raise ValueError("Missing termination_rules.runaway_epsilon_threshold")
        if "runaway_rho_threshold" not in config["termination_rules"]:
            raise ValueError("Missing termination_rules.runaway_rho_threshold")


def simulate_ode(config: dict) -> tuple[list[dict], dict]:
    params = OdeParameters.from_dict(config["parameters"])
    time_settings = config["time_settings"]
    dt = float(time_settings["dt"])
    t_final = float(time_settings["t_final"])
    sample_every = int(time_settings["sample_every"])
    integrator_name = time_settings.get("integrator", "rk4")
    thresholds = config.get("classifier_settings", DEFAULT_THRESHOLDS)
    if "persistence_settle_window_fraction" in thresholds and "settling_window_fraction" not in thresholds:
        thresholds = {
            **thresholds,
            "settling_window_fraction": thresholds["persistence_settle_window_fraction"],
        }
    termination_rules = config.get("termination_rules", {})
    runaway_epsilon_threshold = float(termination_rules.get("runaway_epsilon_threshold", thresholds["runaway_threshold"]))
    runaway_rho_threshold = float(termination_rules.get("runaway_rho_threshold", thresholds["runaway_threshold"]))
    nan_or_inf_invalidates_run = bool(termination_rules.get("nan_or_inf_invalidates_run", True))

    if dt <= 0 or t_final <= 0 or sample_every <= 0:
        raise ValueError("dt, t_final, and sample_every must be positive.")

    integrator = rk4_step if integrator_name == "rk4" else euler_step
    state = build_initial_state(config["initial_conditions"])
    rhs = lambda local_state: ode_rhs(local_state, params)

    total_steps = int(round(t_final / dt))
    rows = [{"step": 0, "t": 0.0, "epsilon": state[0], "rho": state[1], "residue": state[2]}]
    collapse_time = ""
    invalid_run = False
    invalid_reason = ""
    terminated_early = False

    for step in range(1, total_steps + 1):
        state = integrator(rhs, state, dt)
        t_now = step * dt
        if nan_or_inf_invalidates_run and any(not math.isfinite(value) for value in state):
            invalid_run = True
            invalid_reason = "nan_or_inf_state"
            terminated_early = True
            rows.append({"step": step, "t": t_now, "epsilon": state[0], "rho": state[1], "residue": state[2]})
            break
        if abs(state[0]) >= runaway_epsilon_threshold or abs(state[1]) >= runaway_rho_threshold:
            terminated_early = True
            rows.append({"step": step, "t": t_now, "epsilon": state[0], "rho": state[1], "residue": state[2]})
            break
        if collapse_time == "" and state[0] <= thresholds["epsilon_collapse_threshold"]:
            collapse_time = f"{t_now:.6f}"
        if step % sample_every == 0 or step == total_steps:
            rows.append({"step": step, "t": t_now, "epsilon": state[0], "rho": state[1], "residue": state[2]})

    regime = "invalid" if invalid_run else classify_ode_run(rows, thresholds)
    summary = build_ode_summary(config, rows, regime, collapse_time)
    summary["integrator"] = integrator_name
    summary["dt"] = dt
    summary["t_final"] = t_final
    summary["sample_every"] = sample_every
    summary["terminated_early"] = terminated_early
    summary["invalid_reason"] = invalid_reason
    return rows, summary


def write_outputs(config_path: Path, config: dict, raw_config_text: str, timeseries: list[dict], summary: dict) -> Path:
    run_dir = ensure_run_directory(RUNS_ROOT, config["run_id"])
    manifest = {
        "run_id": config["run_id"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "code_version": get_code_version(),
        "config_path": str(config_path.relative_to(REPO_ROOT)),
        "config_sha256": compute_sha256(raw_config_text),
        "seed": config["seed"],
        "equation_mode": config["equation_mode"],
        "experiment_family": config["experiment_family"],
        "notes": config["notes"],
        "stage_id": config.get("stage_id", ""),
        "initial_condition_family": config.get("initial_condition_family", ""),
        "parameters": config["parameters"],
        "time_settings": config["time_settings"],
        "classifier_settings": config.get("classifier_settings", {}),
        "termination_rules": config.get("termination_rules", {}),
    }
    write_json(run_dir / "run_manifest.json", manifest)
    write_json(run_dir / "config_snapshot.json", config)
    write_timeseries_csv(run_dir / "timeseries_global.csv", timeseries)
    write_summary_csv(run_dir / "final_summary.csv", summary)
    write_run_summary_markdown(run_dir / "run_summary.md", manifest, summary)
    return run_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a governed Paper 1 ODE simulation.")
    parser.add_argument("config", type=Path, help="Path to the JSON config file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = args.config.resolve()
    config, raw_config_text = load_config(config_path)
    validate_config(config)
    if config.get("equation_mode") != "ode":
        raise ValueError("Only equation_mode='ode' is supported in this driver.")
    timeseries, summary = simulate_ode(config)
    run_dir = write_outputs(config_path, config, raw_config_text, timeseries, summary)
    print(run_dir)


if __name__ == "__main__":
    main()
