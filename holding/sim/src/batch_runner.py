from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

from run_driver import RUNS_ROOT, load_config, simulate_ode, validate_config, write_outputs


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_batch_config(batch_path: Path) -> dict:
    return json.loads(batch_path.read_text(encoding="utf-8"))


def normalize_batch_config(raw_batch_config: dict) -> dict:
    return raw_batch_config["batch_config"] if "batch_config" in raw_batch_config else raw_batch_config


def build_run_config(base_config: dict, override: dict, run_suffix: str) -> dict:
    merged = json.loads(json.dumps(base_config))
    merged["run_id"] = f"{base_config['run_id']}_{run_suffix}"
    merged["notes"] = override.get("notes", f"{base_config['notes']} Batch override: {run_suffix}.")
    for section in ("parameters", "time_settings", "initial_conditions", "classifier_settings"):
        if section in override:
            merged.setdefault(section, {})
            merged[section].update(override[section])
    for field in ("experiment_family", "equation_mode", "seed", "termination_rules", "near_floor_sampling"):
        if field in override:
            merged[field] = override[field]
    return merged


def slugify_value(value: object) -> str:
    if isinstance(value, float):
        return str(value).replace("-", "m").replace(".", "p")
    return str(value).replace("-", "_")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def resolve_baseline_template(base_config: dict, template: dict) -> dict:
    resolved = {}
    for key, value in template.items():
        if value in {"USE_CURRENT_BASELINE", "USE_CURRENT_BASELINE_UNLESS_SCANNED"}:
            resolved[key] = base_config["parameters"][key]
        else:
            resolved[key] = value
    return resolved


def parameter_combinations(vary: dict) -> list[dict]:
    if "kappa_lambda_pairs" in vary:
        pair_values = vary["kappa_lambda_pairs"]
        other_keys = [key for key in vary.keys() if key != "kappa_lambda_pairs"]
        combinations = []
        for pair in pair_values:
            for other_values in itertools.product(*(vary[key] for key in other_keys)):
                combination = {"kappa": pair["kappa"], "lambda": pair["lambda"]}
                combination.update({key: value for key, value in zip(other_keys, other_values)})
                combinations.append(combination)
        return combinations
    keys = list(vary.keys())
    return [{key: value for key, value in zip(keys, values)} for values in itertools.product(*(vary[key] for key in keys))]


def expand_stage_runs(batch_config: dict, base_config: dict) -> list[dict]:
    global_settings = batch_config["global_settings"]
    classifier_settings = batch_config["classifier_settings"]
    base_parameters = resolve_baseline_template(base_config, batch_config["fixed_parameters_template"])
    expanded_runs = []
    for stage in batch_config["scan_stages"]:
        for initial_family in batch_config["initial_condition_families"]:
            for combination in parameter_combinations(stage["vary"]):
                parameters = dict(base_parameters)
                initial_conditions = {
                    "epsilon0": initial_family["epsilon0"],
                    "rho0": initial_family["rho0"],
                    "R0": initial_family["R0"],
                }
                for key, value in combination.items():
                    if key in {"epsilon0", "rho0", "R0"}:
                        initial_conditions[key] = value
                    else:
                        parameters[key] = value
                suffix_parts = [initial_family["name"], *[f"{key}_{slugify_value(value)}" for key, value in combination.items()]]
                run_config = {
                    "run_id": f"{base_config['run_id']}_{stage['stage_id']}_{'_'.join(suffix_parts)}",
                    "experiment_family": batch_config["governance"]["experiment_family"],
                    "equation_mode": batch_config["governance"]["equation_mode"],
                    "parameters": parameters,
                    "time_settings": {
                        "dt": global_settings["dt"],
                        "t_final": global_settings["t_final"],
                        "sample_every": global_settings["sample_every"],
                        "integrator": global_settings["integrator"],
                    },
                    "initial_conditions": initial_conditions,
                    "seed": batch_config["seed_policy"]["seeds"][0],
                    "notes": initial_family["notes"],
                    "stage_id": stage["stage_id"],
                    "initial_condition_family": initial_family["name"],
                    "classifier_settings": classifier_settings,
                    "termination_rules": global_settings["termination_rules"],
                }
                if "near_floor_sampling" in global_settings:
                    run_config["near_floor_sampling"] = global_settings["near_floor_sampling"]
                expanded_runs.append(run_config)
    return expanded_runs


def load_candidate_rows() -> list[dict]:
    candidate_path = REPO_ROOT / "artifacts" / "runs" / "ode_epsilon_floor_extraction_scan_v1" / "top_floor_candidate_runs.csv"
    if not candidate_path.exists():
        return []
    with candidate_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def dedupe_candidates(candidate_rows: list[dict], limit: int = 3) -> list[dict]:
    unique = []
    seen = set()
    for row in candidate_rows:
        key = tuple(row[field] for field in ("k", "beta", "c", "kappa", "lambda", "v"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
        if len(unique) >= limit:
            break
    return unique


def build_refinement_runs(batch_config: dict, base_config: dict) -> list[dict]:
    candidate_rows = dedupe_candidates(load_candidate_rows())
    if not candidate_rows:
        raise FileNotFoundError("Missing prior candidate file: artifacts/runs/ode_epsilon_floor_extraction_scan_v1/top_floor_candidate_runs.csv")

    global_settings = batch_config["global_settings"]
    classifier_settings = batch_config["classifier_settings"]
    base_parameters = (
        resolve_baseline_template(base_config, batch_config["fixed_parameters_template"])
        if "fixed_parameters_template" in batch_config
        else dict(base_config["parameters"])
    )
    runs = []

    for candidate_index, candidate in enumerate(candidate_rows, start=1):
        candidate_id = f"candidate_{candidate_index:02d}"
        candidate_parameters = dict(base_parameters)
        for key in ("k", "beta", "c", "kappa", "lambda", "v"):
            candidate_parameters[key] = float(candidate[key])
        candidate_parameters["alpha"] = 8.0
        candidate_parameters["gamma"] = 1.0

        candidate_initials = []
        for initial_family in batch_config["initial_condition_families"]:
            if "epsilon0_pair" in initial_family:
                for epsilon0 in initial_family["epsilon0_pair"]:
                    candidate_initials.append(
                        {
                            "name": initial_family["name"],
                            "state_tag": f"{initial_family['name']}_eps_{slugify_value(epsilon0)}",
                            "epsilon0": epsilon0,
                            "rho0": initial_family["rho0"],
                            "R0": initial_family["R0"],
                            "notes": initial_family["notes"],
                        }
                    )
            else:
                candidate_initials.append(
                    {
                        "name": initial_family["name"],
                        "state_tag": initial_family["name"],
                        "epsilon0": initial_family["epsilon0"],
                        "rho0": initial_family["rho0"],
                        "R0": initial_family["R0"],
                        "notes": initial_family["notes"],
                    }
                )

        for stage in batch_config["scan_stages"]:
            stage_id = stage["stage_id"]
            if stage_id == "R1_candidate_local_box":
                for initial_state in candidate_initials:
                    for parameter_name in stage["refine_parameters"]:
                        center = candidate_parameters.get(parameter_name, base_parameters.get(parameter_name, 0.0))
                        for index, value in enumerate([center * factor for factor in (0.9, 0.95, 1.0, 1.05, 1.1)], start=1):
                            parameters = dict(candidate_parameters)
                            parameters[parameter_name] = value
                            for dt in global_settings["dt_values"]:
                                for t_final in global_settings["t_final_values"]:
                                    run_id = (
                                        f"{base_config['run_id']}_{stage_id}_{candidate_id}_{initial_state['name']}_"
                                        f"{initial_state['state_tag']}_param_{parameter_name}_pt_{index}_dt_{slugify_value(dt)}_tf_{slugify_value(t_final)}"
                                    )
                                    runs.append(
                                        {
                                            "run_id": run_id,
                                            "experiment_family": batch_config["governance"]["experiment_family"],
                                            "equation_mode": batch_config["governance"]["equation_mode"],
                                            "parameters": parameters,
                                            "time_settings": {
                                                "dt": dt,
                                                "t_final": t_final,
                                                "sample_every": global_settings["sample_every"],
                                                "integrator": global_settings["integrator"],
                                            },
                                            "initial_conditions": {
                                                "epsilon0": initial_state["epsilon0"],
                                                "rho0": initial_state["rho0"],
                                                "R0": initial_state["R0"],
                                            },
                                            "seed": batch_config["seed_policy"]["seeds"][0],
                                            "notes": initial_state["notes"],
                                            "stage_id": stage_id,
                                            "candidate_id": candidate_id,
                                            "initial_condition_family": initial_state["name"],
                                            "classifier_settings": classifier_settings,
                                            "termination_rules": global_settings["termination_rules"],
                                            "near_floor_sampling": global_settings["near_floor_sampling"],
                                            "refined_parameter": parameter_name,
                                            "local_refine_value": value,
                                        }
                                    )
            elif stage_id == "R2_time_horizon_refinement":
                for initial_state in candidate_initials:
                    for t_final in stage["vary"]["t_final"]:
                        runs.append(
                            {
                                "run_id": f"{base_config['run_id']}_{stage_id}_{candidate_id}_{initial_state['state_tag']}_tf_{slugify_value(t_final)}",
                                "experiment_family": batch_config["governance"]["experiment_family"],
                                "equation_mode": batch_config["governance"]["equation_mode"],
                                "parameters": dict(candidate_parameters),
                                "time_settings": {
                                    "dt": global_settings["dt_values"][1],
                                    "t_final": t_final,
                                    "sample_every": global_settings["sample_every"],
                                    "integrator": global_settings["integrator"],
                                },
                                "initial_conditions": {
                                    "epsilon0": initial_state["epsilon0"],
                                    "rho0": initial_state["rho0"],
                                    "R0": initial_state["R0"],
                                },
                                "seed": batch_config["seed_policy"]["seeds"][0],
                                "notes": initial_state["notes"],
                                "stage_id": stage_id,
                                "candidate_id": candidate_id,
                                "initial_condition_family": initial_state["name"],
                                "classifier_settings": classifier_settings,
                                "termination_rules": global_settings["termination_rules"],
                                "near_floor_sampling": global_settings["near_floor_sampling"],
                            }
                        )
            elif stage_id == "R3_dt_convergence_probe":
                for initial_state in candidate_initials:
                    for dt in stage["vary"]["dt"]:
                        runs.append(
                            {
                                "run_id": f"{base_config['run_id']}_{stage_id}_{candidate_id}_{initial_state['state_tag']}_dt_{slugify_value(dt)}",
                                "experiment_family": batch_config["governance"]["experiment_family"],
                                "equation_mode": batch_config["governance"]["equation_mode"],
                                "parameters": dict(candidate_parameters),
                                "time_settings": {
                                    "dt": dt,
                                    "t_final": max(global_settings["t_final_values"]),
                                    "sample_every": global_settings["sample_every"],
                                    "integrator": global_settings["integrator"],
                                },
                                "initial_conditions": {
                                    "epsilon0": initial_state["epsilon0"],
                                    "rho0": initial_state["rho0"],
                                    "R0": initial_state["R0"],
                                },
                                "seed": batch_config["seed_policy"]["seeds"][0],
                                "notes": initial_state["notes"],
                                "stage_id": stage_id,
                                "candidate_id": candidate_id,
                                "initial_condition_family": initial_state["name"],
                                "classifier_settings": classifier_settings,
                                "termination_rules": global_settings["termination_rules"],
                                "near_floor_sampling": global_settings["near_floor_sampling"],
                            }
                        )
            elif stage_id == "R4_micro_ic_resolution_probe":
                for epsilon0 in stage["vary"]["epsilon0_micro_scan"]:
                    runs.append(
                        {
                            "run_id": f"{base_config['run_id']}_{stage_id}_{candidate_id}_epsilon0_{slugify_value(epsilon0)}",
                            "experiment_family": batch_config["governance"]["experiment_family"],
                            "equation_mode": batch_config["governance"]["equation_mode"],
                            "parameters": dict(candidate_parameters),
                            "time_settings": {
                                "dt": global_settings["dt_values"][1],
                                "t_final": max(global_settings["t_final_values"]),
                                "sample_every": global_settings["sample_every"],
                                "integrator": global_settings["integrator"],
                            },
                            "initial_conditions": {"epsilon0": epsilon0, "rho0": 0.25, "R0": 0.0},
                            "seed": batch_config["seed_policy"]["seeds"][0],
                            "notes": "Micro initial-condition refinement probe.",
                            "stage_id": stage_id,
                            "candidate_id": candidate_id,
                            "initial_condition_family": "micro_ic_probe",
                            "classifier_settings": classifier_settings,
                            "termination_rules": global_settings["termination_rules"],
                            "near_floor_sampling": global_settings["near_floor_sampling"],
                            "epsilon0_micro_scan": epsilon0,
                        }
                    )
    return runs


def summarize_classifications(rows: list[dict]) -> list[dict]:
    keys = ["stage_id", "candidate_id", "initial_condition_family", "regime_classification"]
    counts: dict[tuple[str, str, str, str], int] = {}
    for row in rows:
        key = tuple(row.get(field, "") for field in keys)
        counts[key] = counts.get(key, 0) + 1
    return [{**dict(zip(keys, key)), "run_count": count} for key, count in sorted(counts.items())]


def build_parameter_regime_table(rows: list[dict]) -> list[dict]:
    keys = [
        "run_id", "candidate_id", "stage_id", "initial_condition_family", "regime_classification",
        "k", "b", "c", "alpha", "beta", "gamma", "kappa", "lambda", "v", "s", "h",
        "epsilon_final", "rho_final", "residue_final", "rho_negative_flag",
    ]
    return [{key: row.get(key, "") for key in keys} for row in rows]


def build_top_runs_by_regime(rows: list[dict], top_n: int = 3) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["regime_classification"], []).append(row)
    output = []
    for regime, group in sorted(grouped.items()):
        for rank, row in enumerate(sorted(group, key=lambda item: item["epsilon_final"], reverse=True)[:top_n], start=1):
            output.append(
                {
                    "regime_classification": regime,
                    "rank_within_regime": rank,
                    "run_id": row["run_id"],
                    "candidate_id": row.get("candidate_id", ""),
                    "stage_id": row["stage_id"],
                    "initial_condition_family": row["initial_condition_family"],
                    "epsilon_final": row["epsilon_final"],
                    "rho_final": row["rho_final"],
                    "residue_final": row["residue_final"],
                    "kappa": row["kappa"],
                    "lambda": row["lambda"],
                    "v": row["v"],
                    "k": row["k"],
                    "beta": row["beta"],
                    "gamma": row["gamma"],
                }
            )
    return output


def build_epsilon_floor_refinement_summary(rows: list[dict]) -> list[dict]:
    keys = [
        "run_id", "candidate_id", "stage_id", "initial_condition_family", "regime_classification",
        "epsilon_floor_estimate", "epsilon_last_window_mean", "epsilon_last_window_std",
        "epsilon_last_window_min", "epsilon_last_window_max", "near_floor_bandwidth",
        "near_floor_oscillation_amplitude", "time_to_near_floor_window", "delta_epsilon_min_resolved", "dt", "t_final",
    ]
    return [{key: row.get(key, "") for key in keys} for row in rows]


def build_near_floor_band_stability_table(rows: list[dict]) -> list[dict]:
    filtered = [row for row in rows if row["stage_id"] in {"R2_time_horizon_refinement", "R3_dt_convergence_probe"}]
    keys = ["candidate_id", "stage_id", "run_id", "dt", "t_final", "epsilon_floor_estimate", "near_floor_bandwidth", "near_floor_oscillation_amplitude", "regime_classification"]
    return [{key: row.get(key, "") for key in keys} for row in filtered]


def build_dt_convergence_table(rows: list[dict]) -> list[dict]:
    filtered = [row for row in rows if row["stage_id"] == "R3_dt_convergence_probe"]
    keys = ["candidate_id", "run_id", "dt", "epsilon_floor_estimate", "near_floor_bandwidth", "near_floor_oscillation_amplitude", "epsilon_last_window_std", "regime_classification"]
    return [{key: row.get(key, "") for key in keys} for row in filtered]


def build_ic_resolution_table(rows: list[dict]) -> list[dict]:
    filtered = [row for row in rows if row["stage_id"] == "R4_micro_ic_resolution_probe"]
    keys = ["candidate_id", "run_id", "epsilon0_micro_scan", "epsilon_floor_estimate", "epsilon_min_observed", "near_floor_bandwidth", "delta_epsilon_min_resolved", "regime_classification"]
    return [{key: row.get(key, "") for key in keys} for row in filtered]


def build_top_refined_floor_candidates(rows: list[dict], top_n: int = 10) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda row: (row.get("epsilon_floor_estimate", float("inf")), row.get("near_floor_bandwidth", float("inf"))))
    return [
        {
            "rank": index + 1,
            "candidate_id": row.get("candidate_id", ""),
            "run_id": row["run_id"],
            "stage_id": row["stage_id"],
            "epsilon_floor_estimate": row["epsilon_floor_estimate"],
            "near_floor_bandwidth": row["near_floor_bandwidth"],
            "near_floor_oscillation_amplitude": row["near_floor_oscillation_amplitude"],
            "dt": row.get("dt", ""),
            "t_final": row.get("t_final", ""),
            "regime_classification": row["regime_classification"],
        }
        for index, row in enumerate(sorted_rows[:top_n])
    ]


def build_epsilon_floor_summary(rows: list[dict]) -> list[dict]:
    keys = [
        "run_id", "stage_id", "initial_condition_family", "regime_classification", "epsilon_min_observed",
        "epsilon_argmin_time", "epsilon_floor_estimate", "near_floor_bandwidth", "near_floor_oscillation_amplitude",
        "delta_epsilon_min_resolved", "rho_negative_flag", "k", "beta", "c", "kappa", "lambda", "v",
    ]
    return [{key: row.get(key, "") for key in keys} for row in rows]


def build_near_floor_comparison_table(rows: list[dict]) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda row: row.get("epsilon_floor_estimate", float("inf")))
    keys = [
        "run_id", "stage_id", "initial_condition_family", "regime_classification", "epsilon_floor_estimate",
        "epsilon_min_observed", "near_floor_bandwidth", "near_floor_oscillation_amplitude", "delta_epsilon_min_resolved",
    ]
    return [{key: row.get(key, "") for key in keys} for row in sorted_rows[:25]]


def build_top_floor_candidate_runs(rows: list[dict], top_n: int = 10) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda row: row.get("epsilon_floor_estimate", float("inf")))
    return [
        {
            "rank": index + 1,
            "run_id": row["run_id"],
            "stage_id": row["stage_id"],
            "initial_condition_family": row["initial_condition_family"],
            "regime_classification": row["regime_classification"],
            "epsilon_floor_estimate": row["epsilon_floor_estimate"],
            "epsilon_min_observed": row["epsilon_min_observed"],
            "near_floor_bandwidth": row["near_floor_bandwidth"],
            "near_floor_oscillation_amplitude": row["near_floor_oscillation_amplitude"],
            "k": row["k"],
            "beta": row["beta"],
            "c": row["c"],
            "kappa": row["kappa"],
            "lambda": row["lambda"],
            "v": row["v"],
        }
        for index, row in enumerate(sorted_rows[:top_n])
    ]


def write_batch_diagnostic(batch_run_dir: Path, batch_name: str, rows: list[dict]) -> None:
    regimes = {row["regime_classification"] for row in rows}
    lines = [f"# Batch Diagnostic: {batch_name}", ""]
    if "near_floor_oscillatory" in regimes:
        lines.extend(
            [
                "Near-floor oscillatory regimes were identified in this refinement scan.",
                "",
                "This supports the oscillatory-band hypothesis for at least one refined candidate.",
            ]
        )
    elif "near_floor_convergent" in regimes or "near_floor_persistent" in regimes:
        lines.extend(
            [
                "Near-floor regimes were identified in this scan.",
                "",
                "Recommended next step: refine around the lowest `epsilon_floor_estimate` candidates and compare final-window bandwidth under smaller `dt` and longer `t_final`.",
            ]
        )
    elif "collapse_to_pressure" not in regimes:
        lines.extend(
            [
                "No `collapse_to_pressure` cases were found in this ODE scan.",
                "",
                "No floor-near regime was reached in the scanned region under the current operational measurements.",
                "Recommended next step: expand the floor-seeking range or refine around the lowest `epsilon_min_observed` candidates.",
            ]
        )
    else:
        lines.extend(["`collapse_to_pressure` cases were found in this scan.", "", "Recommended next step: refine the neighborhood around the first classification transitions."])
    (batch_run_dir / "diagnostic_note.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def flatten_summary(summary: dict, run_config: dict) -> dict:
    flat = dict(summary)
    flat.update(run_config["parameters"])
    flat["stage_id"] = run_config.get("stage_id", "")
    flat["initial_condition_family"] = run_config.get("initial_condition_family", "")
    flat["candidate_id"] = run_config.get("candidate_id", "")
    flat["seed"] = run_config["seed"]
    flat["epsilon0"] = run_config["initial_conditions"]["epsilon0"]
    flat["rho0"] = run_config["initial_conditions"]["rho0"]
    flat["R0"] = run_config["initial_conditions"]["R0"]
    flat["dt"] = run_config["time_settings"]["dt"]
    flat["t_final"] = run_config["time_settings"]["t_final"]
    flat["epsilon0_micro_scan"] = run_config.get("epsilon0_micro_scan", "")
    return flat


def run_batch(batch_path: Path) -> Path:
    raw_batch_config = load_batch_config(batch_path)
    batch_config = normalize_batch_config(raw_batch_config)
    base_config_path = (REPO_ROOT / batch_config.get("base_config", "sim/configs/ode_smoke_baseline.json")).resolve()
    base_config, _ = load_config(base_config_path)
    validate_config(base_config)

    batch_id = batch_config.get("batch_id", batch_config.get("name"))
    batch_run_dir = RUNS_ROOT / batch_id
    batch_run_dir.mkdir(parents=True, exist_ok=False)
    (batch_run_dir / "batch_config_snapshot.json").write_text(json.dumps(raw_batch_config, indent=2) + "\n", encoding="utf-8")

    if "runs" in batch_config:
        run_specs = [build_run_config(base_config, run_spec, run_spec["run_suffix"]) for run_spec in batch_config["runs"]]
    elif batch_config["governance"]["experiment_family"] == "epsilon_floor_refinement":
        run_specs = build_refinement_runs(batch_config, base_config)
    else:
        run_specs = expand_stage_runs(batch_config, base_config)

    summaries = []
    for run_config in run_specs:
        validate_config(run_config)
        timeseries, summary = simulate_ode(run_config)
        write_outputs(base_config_path, run_config, json.dumps(run_config, indent=2), timeseries, summary)
        summaries.append(flatten_summary(summary, run_config))

    write_csv(batch_run_dir / "batch_summary.csv", summaries, list(summaries[0].keys()) if summaries else ["run_id"])
    write_csv(
        batch_run_dir / "classification_summary.csv",
        summarize_classifications(summaries),
        ["stage_id", "candidate_id", "initial_condition_family", "regime_classification", "run_count"],
    )

    required_outputs = batch_config.get("batch_aggregation", {}).get("required_outputs", [])
    if "parameter_regime_table.csv" in required_outputs:
        write_csv(batch_run_dir / "parameter_regime_table.csv", build_parameter_regime_table(summaries), list(build_parameter_regime_table(summaries)[0].keys()))
    if "top_runs_by_regime.csv" in required_outputs:
        top_rows = build_top_runs_by_regime(summaries)
        write_csv(batch_run_dir / "top_runs_by_regime.csv", top_rows, list(top_rows[0].keys()) if top_rows else ["regime_classification"])
    if "epsilon_floor_summary.csv" in required_outputs:
        floor_rows = build_epsilon_floor_summary(summaries)
        write_csv(batch_run_dir / "epsilon_floor_summary.csv", floor_rows, list(floor_rows[0].keys()))
    if "near_floor_comparison_table.csv" in required_outputs:
        near_rows = build_near_floor_comparison_table(summaries)
        write_csv(batch_run_dir / "near_floor_comparison_table.csv", near_rows, list(near_rows[0].keys()))
    if "top_floor_candidate_runs.csv" in required_outputs:
        top_floor_rows = build_top_floor_candidate_runs(summaries)
        write_csv(batch_run_dir / "top_floor_candidate_runs.csv", top_floor_rows, list(top_floor_rows[0].keys()))
    if "epsilon_floor_refinement_summary.csv" in required_outputs:
        refinement_rows = build_epsilon_floor_refinement_summary(summaries)
        write_csv(batch_run_dir / "epsilon_floor_refinement_summary.csv", refinement_rows, list(refinement_rows[0].keys()))
    if "near_floor_band_stability_table.csv" in required_outputs:
        band_rows = build_near_floor_band_stability_table(summaries)
        write_csv(batch_run_dir / "near_floor_band_stability_table.csv", band_rows, list(band_rows[0].keys()) if band_rows else ["candidate_id"])
    if "dt_convergence_table.csv" in required_outputs:
        dt_rows = build_dt_convergence_table(summaries)
        write_csv(batch_run_dir / "dt_convergence_table.csv", dt_rows, list(dt_rows[0].keys()) if dt_rows else ["candidate_id"])
    if "ic_resolution_table.csv" in required_outputs:
        ic_rows = build_ic_resolution_table(summaries)
        write_csv(batch_run_dir / "ic_resolution_table.csv", ic_rows, list(ic_rows[0].keys()) if ic_rows else ["candidate_id"])
    if "top_refined_floor_candidates.csv" in required_outputs:
        top_refined_rows = build_top_refined_floor_candidates(summaries)
        write_csv(batch_run_dir / "top_refined_floor_candidates.csv", top_refined_rows, list(top_refined_rows[0].keys()))

    write_batch_diagnostic(batch_run_dir, batch_id, summaries)
    return batch_run_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a governed ODE batch from a batch config.")
    parser.add_argument("batch_config", type=Path, help="Path to the batch JSON config.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch_path = args.batch_config.resolve()
    batch_run_dir = run_batch(batch_path)
    print(batch_run_dir)


if __name__ == "__main__":
    main()
