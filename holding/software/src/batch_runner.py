from __future__ import annotations

import argparse
import concurrent.futures
import itertools
import json
import multiprocessing
import os
import shutil
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np

from .classify import classify_run, final_summary_row
from .delta_sigma_calibration import resolve_delta_sigma_calibration
from .diagnostics import compute_snapshot_metrics, track_fronts
from .dsr_local_classifier import classify_dsr_metrics, compute_dsr_metrics, summarize_dsr_late_tail
from .dsr_geometry import DEFAULT_DSR_COMMITMENTS_PATH
from .initial_conditions import build_initial_condition
from .native_backend import compute_snapshot_metrics_native, is_native_backend_available, set_native_backend_threads
from .pde_solver import GridConfig, Parameters, gradient_neumann, simulate
from .plots import plot_front_position, plot_front_velocity_vs_parameter, plot_kymograph, plot_phase_map


ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
OUTPUT_DIR = ROOT / "outputs"
PROFILE_DIR = OUTPUT_DIR / "profiles"
RELATIONAL_PROFILE_DIR = OUTPUT_DIR / "profiles_relational"
FIGURE_DIR = OUTPUT_DIR / "figures"


RUN_MANIFEST_COLUMNS = [
    "run_id", "sim_id", "batch_id", "run_date", "seed", "ic_type", "IC_type", "phase_expression",
    "L", "Nx", "dx", "dt", "t_final",
    "a", "alpha", "b", "beta", "c", "gamma", "kappa", "lam", "lambda", "u", "v", "s", "h", "D_eps", "D_rho", "D_R", "eta_kappa", "eta_u", "mu", "nu", "delta_alpha", "delta_beta",
    "dsr_lambda_D", "dsr_theta", "dsr_event_gain", "dsr_sigma_decay", "dsr_sigma_load", "dsr_rho_gain", "dsr_rho_relax", "dsr_bootstrap_gain",
    "ont_M0", "ont_aC", "ont_aD", "ont_lambda", "ont_chi", "ont_kappa_D", "ont_alpha_C", "ont_mu_C", "ont_nu_C", "ont_beta_D", "ont_eta_D", "ont_theta0", "ont_theta1", "ont_epsilon_gate", "ont_gamma_flat", "ont_c_flat", "ont_p_flat", "ont_ell_min", "ont_eps_speed",
    "exclusion_rate_k", "topology_writing_rate_kappa", "topology_persistence_lambda", "inscription_dominance_Pi",
    "dsr_commitments_source", "ratchet_event_steps", "seed_update_steps",
    "delta_family", "delta_alpha_identifiable", "delta_calibration_scope", "delta_calibration_source", "delta_calibration_status",
    "classification", "branch_classification", "classification_source", "seed_unanimity", "converged", "branch_converged", "notes",
]

TIMESERIES_COLUMNS = [
    "run_id", "time", "mean_eps", "mean_rho", "mean_R", "var_eps", "var_rho", "var_R",
    "total_eps", "total_rho", "total_R", "exclusion_fraction", "interface_count", "max_sharpness",
]

FRONT_COLUMNS = [
    "run_id", "time", "front_id", "front_position", "front_velocity", "front_width",
    "front_sharpness", "left_mean_R", "right_mean_R", "residue_asymmetry",
    "front_status", "source_front_id", "predecessor_count", "successor_count",
]

DOMAIN_COLUMNS = [
    "run_id", "time", "n_exclusion_domains", "largest_exclusion_domain", "largest_pressure_domain",
    "mean_node_ratio", "median_node_ratio", "max_node_ratio", "mean_sharpness",
    "inactive_fraction", "active_fraction", "excluded_active_fraction", "undefined_ratio_fraction",
]

FINAL_SUMMARY_COLUMNS = [
    "run_id", "sim_id", "batch_id", "run_date", "seed", "IC_type", "phase_expression",
    "kappa", "lam", "lambda", "exclusion_rate_k", "continuation_attempts", "exclusion_events",
    "alignment_success_rate", "topology_writing_rate_kappa", "topology_persistence_lambda",
    "inscription_dominance_Pi", "residue_field_R_mean", "epsilon_mean", "rho_mean",
    "final_interface_count", "exclusion_fraction", "collapse_time", "regime_classification",
    "seed_unanimity", "classification", "branch_classification", "classification_source", "branch_converged", "final_mean_eps", "final_mean_rho", "final_mean_R",
    "final_exclusion_fraction", "late_time_mean_front_speed", "late_time_mean_front_width",
    "late_time_mean_sharpness", "late_time_residue_asymmetry", "stability_time", "resolution_check_pass",
    "stability_check_pass", "D_eps", "D_rho", "eta_kappa", "eta_u", "mu", "nu", "delta_alpha", "delta_beta",
    "dsr_lambda_D", "dsr_theta", "dsr_event_gain", "dsr_sigma_decay", "dsr_sigma_load", "dsr_rho_gain", "dsr_rho_relax", "dsr_bootstrap_gain",
    "ont_M0", "ont_aC", "ont_aD", "ont_lambda", "ont_chi", "ont_kappa_D", "ont_alpha_C", "ont_mu_C", "ont_nu_C", "ont_beta_D", "ont_eta_D", "ont_theta0", "ont_theta1", "ont_epsilon_gate", "ont_gamma_flat", "ont_c_flat", "ont_p_flat", "ont_ell_min", "ont_eps_speed",
    "dsr_commitments_source", "ratchet_event_steps", "seed_update_steps",
    "delta_family", "delta_alpha_identifiable", "delta_calibration_scope", "delta_calibration_source", "delta_calibration_status",
    "final_mean_Delta", "final_mean_Sigma", "ontology_delta_phi_min", "ontology_kappa_proxy", "ontology_gate_integral", "ontology_ratchet_active_steps",
    "dsr_local_label", "dsr_branch_converged", "dsr_delta_floor_ratio", "dsr_excess_floor_ratio", "dsr_delta_floor_correlation", "dsr_sigma_floor_ratio", "dsr_rho_floor_ratio", "dsr_sign_match_fraction",
    "dsr_tail_count", "dsr_late_window", "dsr_tail_floor_locked_fraction", "dsr_tail_bounded_support_fraction", "dsr_tail_delta_floor_ratio_spread", "dsr_tail_max_excess_floor_ratio", "dsr_tail_min_delta_floor_correlation", "dsr_tail_min_sign_match_fraction", "dsr_tail_max_sigma_floor_ratio", "dsr_tail_max_rho_floor_ratio",
    "ontology_residue_written", "ontology_persistence_window", "ontology_late_time_slope", "ontology_local_label", "broad_summary_label",
    "D_sr_proxy", "K_proxy", "L_proxy",
]


def set_output_root(output_root: Path) -> None:
    global OUTPUT_DIR, PROFILE_DIR, RELATIONAL_PROFILE_DIR, FIGURE_DIR
    OUTPUT_DIR = output_root
    PROFILE_DIR = OUTPUT_DIR / "profiles"
    RELATIONAL_PROFILE_DIR = OUTPUT_DIR / "profiles_relational"
    FIGURE_DIR = OUTPUT_DIR / "figures"


def ensure_layout() -> None:
    for path in [OUTPUT_DIR, PROFILE_DIR, RELATIONAL_PROFILE_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def clean_outputs() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    ensure_layout()


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def deep_copy_json(data: Dict) -> Dict:
    return json.loads(json.dumps(data))


def resolve_config_path(config_name: str) -> Path:
    candidate = Path(config_name)
    if candidate.is_file():
        return candidate.resolve()

    rooted = (Path.cwd() / candidate).resolve()
    if rooted.is_file():
        return rooted

    config_path = CONFIG_DIR / config_name
    if config_path.is_file():
        return config_path.resolve()

    raise FileNotFoundError(f"Could not resolve config path: {config_name}")


def expand_run_specs(config_name: str) -> List[Dict]:
    config_path = resolve_config_path(config_name)
    config = load_json(config_path)
    if "base_config" not in config and "parameter_grid" not in config and "parameters" in config:
        return [config]

    if "base_config" in config:
        base_ref = Path(config["base_config"])
        if not base_ref.is_absolute():
            config_relative = (config_path.parent / base_ref)
            if config_relative.is_file():
                base_ref = config_relative
            else:
                base_ref = CONFIG_DIR / config["base_config"]
        base = load_json(base_ref)
    else:
        base = {
            key: deep_copy_json(value)
            for key, value in config.items()
            if key not in {"label", "parameter_grid", "overrides"}
        }
    run_specs: List[Dict] = []

    for override in config.get("overrides", []):
        for value in override["values"]:
            spec = deep_copy_json(base)
            spec["label"] = f'{override["label"]}_{override["parameter"]}_{value}'
            spec["parameters"][override["parameter"]] = value
            run_specs.append(spec)

    if "parameter_grid" in config:
        keys = list(config["parameter_grid"].keys())
        for values in itertools.product(*(config["parameter_grid"][key] for key in keys)):
            spec = deep_copy_json(base)
            if "grid" in config:
                spec.setdefault("grid", {}).update(deep_copy_json(config["grid"]))
            if "parameters" in config:
                spec.setdefault("parameters", {}).update(deep_copy_json(config["parameters"]))
            if "seeds" in config:
                spec["seeds"] = deep_copy_json(config["seeds"])
            if "initial_conditions" in config:
                spec["initial_conditions"] = deep_copy_json(config["initial_conditions"])
            label_bits = []
            for key, value in zip(keys, values):
                spec["parameters"][key] = value
                label_bits.append(f"{key}_{value}")
            spec["label"] = "grid_" + "_".join(label_bits)
            run_specs.append(spec)

    return run_specs


def write_csv(path: Path, rows: Iterable[Dict], fieldnames: List[str]) -> None:
    def encode(value: object) -> str:
        text = "" if value is None else str(value)
        if any(char in text for char in [",", "\"", "\n"]):
            text = "\"" + text.replace("\"", "\"\"") + "\""
        return text

    with path.open("w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(fieldnames) + "\n")
        for row in rows:
            handle.write(",".join(encode(row.get(name, "")) for name in fieldnames) + "\n")


def profile_filename(run_id: str, time_value: float) -> Path:
    safe_time = f"{time_value:.4f}".replace(".", "p")
    return PROFILE_DIR / f"profile_run_{run_id}_t_{safe_time}.csv"


def relational_profile_filename(run_id: str, time_value: float) -> Path:
    safe_time = f"{time_value:.4f}".replace(".", "p")
    return RELATIONAL_PROFILE_DIR / f"profile_relational_{run_id}_t_{safe_time}.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Level 2 1D NOT-axiom PDE batches.")
    parser.add_argument("--config", default="base_transition.json", help="Config or sweep file under level2/config.")
    parser.add_argument("--max-runs", type=int, default=None, help="Optional cap for smoke tests.")
    parser.add_argument("--t-final", type=float, default=None, help="Override t_final for quicker validation.")
    parser.add_argument("--save-every", type=int, default=None, help="Override save cadence.")
    parser.add_argument("--with-convergence-checks", action="store_true", help="Run Nx/dt convergence checks for each run.")
    parser.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 1) - 1), help="Number of worker processes for independent runs.")
    parser.add_argument("--fast", action="store_true", help="Skip per-run profiles and figures to reduce I/O overhead.")
    parser.add_argument("--write-profiles", action="store_true", help="Write profile CSVs even when --fast is enabled.")
    parser.add_argument("--skip-figures", action="store_true", help="Skip all figure generation while retaining CSV outputs.")
    parser.add_argument("--profile-tail-count", type=int, default=None, help="If set, only retain the last N profile snapshots per run.")
    parser.add_argument("--clean", action="store_true", help="Delete existing level2/outputs before running the batch.")
    parser.add_argument("--backend", choices=["auto", "python", "native"], default="auto", help="Simulation backend to use. 'auto' prefers the native C++ PDE engine and falls back to Python only if needed.")
    parser.add_argument("--native-threads", type=int, default=None, help="OpenMP thread count for the native backend.")
    parser.add_argument("--output-root", default=None, help="Optional output directory. Defaults to level2/outputs.")
    return parser.parse_args()


def run_date_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def derive_batch_id(output_root: Path) -> str:
    output_root = output_root.resolve()
    if output_root.name == "outputs" and output_root.parent != output_root:
        return output_root.parent.name
    return output_root.name


def safe_pi_value(kappa: float, lam: float) -> float:
    if abs(lam) <= 1.0e-12:
        return 0.0 if abs(kappa) <= 1.0e-12 else float("inf")
    return kappa / lam


def late_tail_rows(rows: List[Dict[str, float]], late_fraction: float = 0.2) -> List[Dict[str, float]]:
    if not rows:
        return []
    n_tail = max(1, int(len(rows) * late_fraction))
    return rows[-n_tail:]


def compute_continuation_attempts(front_rows: List[Dict[str, float]]) -> int:
    return len({int(row["front_id"]) for row in front_rows})


def compute_exclusion_events(timeseries_rows: List[Dict[str, float]]) -> int:
    previous_active = False
    events = 0
    for row in timeseries_rows:
        active = float(row.get("n_exclusion_domains", 0.0)) > 0.0 or float(row.get("exclusion_fraction", 0.0)) > 0.0
        if active and not previous_active:
            events += 1
        previous_active = active
    return events


def compute_alignment_success_rate(timeseries_rows: List[Dict[str, float]]) -> float:
    tail = late_tail_rows(timeseries_rows)
    if not tail:
        return 0.0
    values = []
    for row in tail:
        excluded_fraction = float(row.get("excluded_active_fraction", row.get("exclusion_fraction", 0.0)))
        values.append(max(0.0, min(1.0, 1.0 - excluded_fraction)))
    return float(np.mean(values)) if values else 0.0


def compute_collapse_time(timeseries_rows: List[Dict[str, float]], threshold: float = 0.95) -> str:
    for row in timeseries_rows:
        if float(row.get("exclusion_fraction", 0.0)) >= threshold:
            return f"{float(row['time']):.6f}"
    return ""


def compute_l_proxy(timeseries_rows: List[Dict[str, float]]) -> float:
    if not timeseries_rows:
        return 0.0
    final_time = float(timeseries_rows[-1]["time"])
    if final_time <= 0.0:
        return 0.0
    interface_loss_time = final_time
    for row in timeseries_rows:
        if float(row.get("interface_count", 0.0)) <= 0.0:
            interface_loss_time = float(row["time"])
            break
    return max(0.0, min(1.0, interface_loss_time / final_time))


def compute_stability_time(timeseries_rows: List[Dict[str, float]]) -> str:
    if not timeseries_rows:
        return ""

    final_row = timeseries_rows[-1]
    final_mean_eps = float(final_row.get("mean_eps", 0.0))
    final_mean_rho = float(final_row.get("mean_rho", 0.0))
    final_mean_residue = float(final_row.get("mean_R", 0.0))
    final_exclusion_fraction = float(final_row.get("exclusion_fraction", 0.0))
    final_interface_count = int(round(float(final_row.get("interface_count", 0.0))))

    eps_tolerance = max(1.0e-3, 0.02 * max(abs(final_mean_eps), 1.0))
    rho_tolerance = max(1.0e-3, 0.02 * max(abs(final_mean_rho), 1.0))
    residue_tolerance = max(1.0e-3, 0.02 * max(abs(final_mean_residue), 1.0))
    exclusion_tolerance = 0.02

    for start_index, candidate_row in enumerate(timeseries_rows):
        tail = timeseries_rows[start_index:]
        if all(
            abs(float(row.get("mean_eps", 0.0)) - final_mean_eps) <= eps_tolerance
            and abs(float(row.get("mean_rho", 0.0)) - final_mean_rho) <= rho_tolerance
            and abs(float(row.get("mean_R", 0.0)) - final_mean_residue) <= residue_tolerance
            and abs(float(row.get("exclusion_fraction", 0.0)) - final_exclusion_fraction) <= exclusion_tolerance
            and int(round(float(row.get("interface_count", 0.0)))) == final_interface_count
            for row in tail
        ):
            return f"{float(candidate_row['time']):.6f}"

    return f"{float(final_row['time']):.6f}"


def compute_d_sr_proxy(summary_row: Dict[str, object]) -> float:
    epsilon_mean = float(summary_row["final_mean_eps"])
    rho_mean = float(summary_row["final_mean_rho"])
    residue_mean = float(summary_row["final_mean_R"])
    return residue_mean / max(epsilon_mean + rho_mean, 1.0e-12)


def fit_tail_slope(times: List[float], values: List[float], tail_fraction: float = 0.2) -> float:
    time_array = np.asarray(times, dtype=float)
    value_array = np.asarray(values, dtype=float)
    if time_array.size < 2 or value_array.size != time_array.size:
        return 0.0
    tail_count = max(2, int(np.ceil(time_array.size * tail_fraction)))
    tail_times = time_array[-tail_count:]
    tail_values = value_array[-tail_count:]
    if np.allclose(tail_times, tail_times[0]):
        return 0.0
    slope, _intercept = np.polyfit(tail_times, tail_values, 1)
    return float(slope)


def classify_ontology_branch(
    peak_max_delta: float,
    final_max_delta: float,
    delta_phi_min: float,
    final_mean_constraint: float,
    final_mean_depth: float,
    residue_written: bool,
    persistence_window: float,
    late_time_slope: float,
) -> str:
    if peak_max_delta < delta_phi_min:
        return "inert"
    sustained_support = (
        residue_written
        and persistence_window >= 5.0
        and final_max_delta >= delta_phi_min
        and final_mean_constraint >= 1.0e-4
        and final_mean_depth >= 1.0e-4
        and late_time_slope >= -1.0e-5
    )
    if sustained_support:
        return "persistent"
    return "metastable"


def summarise_run(
    run_id: str,
    params: Parameters,
    results: Dict,
    write_profiles: bool,
    profile_tail_count: int | None = None,
) -> Dict[str, object]:
    run_timeseries: List[Dict] = []
    run_front_frames: List[List[Dict]] = []
    node_ratio_stack: List[np.ndarray] = []
    residue_stack: List[np.ndarray] = []
    x_values = np.asarray(results["x"], dtype=float)
    dx = float(x_values[1] - x_values[0]) if len(x_values) > 1 else 1.0
    use_native_metrics = str(results.get("engine_name", "")).startswith("level2_pde_cpp") and is_native_backend_available()

    times = list(results["times"])
    snapshots = list(results["snapshots"])
    profile_start_index = 0
    if write_profiles and profile_tail_count is not None:
        profile_start_index = max(0, len(times) - max(0, int(profile_tail_count)))
    final_delta_snapshot: np.ndarray | None = None
    final_sigma_snapshot: np.ndarray | None = None
    final_rho_snapshot: np.ndarray | None = None
    final_depth_snapshot: np.ndarray | None = None
    final_delta_floor_snapshot: np.ndarray | None = None
    dsr_branch_detected = False
    dsr_profile_times: List[float] = []
    dsr_metrics_history: List[Dict[str, float]] = []
    ontology_delta_snapshot: np.ndarray | None = None
    ontology_constraint_snapshot: np.ndarray | None = None
    ontology_depth_snapshot: np.ndarray | None = None
    ontology_delta_phi_min = 0.0
    ontology_peak_max_delta = 0.0
    ontology_peak_speed_ratio = 0.0
    ontology_profile_times: List[float] = []
    ontology_profile_peak_deltas: List[float] = []
    ontology_persistence_start: float | None = None
    ontology_persistence_end: float | None = None
    ontology_final_kappa_proxy = 0.0
    previous_ontology_delta: np.ndarray | None = None
    previous_ontology_time: float | None = None

    for snapshot_index, (time_value, snapshot) in enumerate(zip(times, snapshots)):
        if use_native_metrics:
            metrics_row, fronts, profile = compute_snapshot_metrics_native(
                x=np.asarray(results["x"], dtype=float),
                time=float(time_value),
                epsilon=np.asarray(snapshot["epsilon"], dtype=float),
                rho=np.asarray(snapshot["rho"], dtype=float),
                residue=np.asarray(snapshot["residue"], dtype=float),
            )
            metrics = metrics_row
        else:
            metrics_obj, fronts, profile = compute_snapshot_metrics(
                x=results["x"],
                time=time_value,
                epsilon=snapshot["epsilon"],
                rho=snapshot["rho"],
                residue=snapshot["residue"],
            )
            metrics = {
                "time": metrics_obj.time,
                "mean_eps": metrics_obj.mean_eps,
                "mean_rho": metrics_obj.mean_rho,
                "mean_R": metrics_obj.mean_R,
                "var_eps": metrics_obj.var_eps,
                "var_rho": metrics_obj.var_rho,
                "var_R": metrics_obj.var_R,
                "total_eps": metrics_obj.total_eps,
                "total_rho": metrics_obj.total_rho,
                "total_R": metrics_obj.total_R,
                "exclusion_fraction": metrics_obj.exclusion_fraction,
                "interface_count": metrics_obj.interface_count,
                "max_sharpness": metrics_obj.max_sharpness,
                "n_exclusion_domains": metrics_obj.n_exclusion_domains,
                "largest_exclusion_domain": metrics_obj.largest_exclusion_domain,
                "largest_pressure_domain": metrics_obj.largest_pressure_domain,
                "mean_node_ratio": metrics_obj.mean_node_ratio,
                "median_node_ratio": metrics_obj.median_node_ratio,
                "max_node_ratio": metrics_obj.max_node_ratio,
                "mean_sharpness": metrics_obj.mean_sharpness,
                "inactive_fraction": metrics_obj.inactive_fraction,
                "active_fraction": metrics_obj.active_fraction,
                "excluded_active_fraction": metrics_obj.excluded_active_fraction,
                "undefined_ratio_fraction": metrics_obj.undefined_ratio_fraction,
            }
        combined_row = {
            "run_id": run_id,
            "time": metrics["time"],
            "mean_eps": metrics["mean_eps"],
            "mean_rho": metrics["mean_rho"],
            "mean_R": metrics["mean_R"],
            "var_eps": metrics["var_eps"],
            "var_rho": metrics["var_rho"],
            "var_R": metrics["var_R"],
            "total_eps": metrics["total_eps"],
            "total_rho": metrics["total_rho"],
            "total_R": metrics["total_R"],
            "exclusion_fraction": metrics["exclusion_fraction"],
            "interface_count": metrics["interface_count"],
            "max_sharpness": metrics["max_sharpness"],
            "n_exclusion_domains": metrics["n_exclusion_domains"],
            "largest_exclusion_domain": metrics["largest_exclusion_domain"],
            "largest_pressure_domain": metrics["largest_pressure_domain"],
            "mean_node_ratio": metrics["mean_node_ratio"],
            "median_node_ratio": metrics["median_node_ratio"],
            "max_node_ratio": metrics["max_node_ratio"],
            "mean_sharpness": metrics["mean_sharpness"],
            "inactive_fraction": metrics["inactive_fraction"],
            "active_fraction": metrics["active_fraction"],
            "excluded_active_fraction": metrics["excluded_active_fraction"],
            "undefined_ratio_fraction": metrics["undefined_ratio_fraction"],
        }
        run_timeseries.append(combined_row)

        run_front_frames.append([{"run_id": run_id, **front} for front in fronts])

        if write_profiles and snapshot_index >= profile_start_index:
            write_csv(
                profile_filename(run_id, time_value),
                [
                    {
                        "x": float(x_value),
                        "eps": float(eps_value),
                        "rho": float(rho_value),
                        "R": float(residue_value),
                        "node_ratio": float(ratio_value),
                        "sharpness": float(sharpness_value),
                    }
                    for x_value, eps_value, rho_value, residue_value, ratio_value, sharpness_value in zip(
                        profile["x"],
                        profile["eps"],
                        profile["rho"],
                        profile["R"],
                        profile["node_ratio"],
                        profile["sharpness"],
                    )
                ],
                ["x", "eps", "rho", "R", "node_ratio", "sharpness"],
            )
            if "delta" in snapshot and "sigma" in snapshot:
                relational_rows = [
                    {
                        "x": float(x_value),
                        "delta": float(delta_value),
                        "sigma": float(sigma_value),
                        "rho": float(rho_value),
                        **(
                            {"depth": float(depth_value)}
                            if "depth" in snapshot
                            else {}
                        ),
                        **(
                            {"delta_floor": float(delta_floor_value)}
                            if "delta_floor" in snapshot
                            else {}
                        ),
                    }
                    for x_value, delta_value, sigma_value, rho_value, depth_value, delta_floor_value in zip(
                        profile["x"],
                        np.asarray(snapshot["delta"], dtype=float),
                        np.asarray(snapshot["sigma"], dtype=float),
                        np.asarray(snapshot["rho"], dtype=float),
                        np.asarray(snapshot.get("depth", np.full_like(np.asarray(snapshot["rho"], dtype=float), np.nan)), dtype=float),
                        np.asarray(snapshot.get("delta_floor", np.full_like(np.asarray(snapshot["rho"], dtype=float), np.nan)), dtype=float),
                    )
                ]
                relational_columns = ["x", "delta", "sigma", "rho"]
                if "depth" in snapshot:
                    relational_columns.append("depth")
                if "delta_floor" in snapshot:
                    relational_columns.append("delta_floor")
                write_csv(
                    relational_profile_filename(run_id, time_value),
                    relational_rows,
                    relational_columns,
                )
            elif "delta" in snapshot and "C" in snapshot and "D" in snapshot:
                relational_rows = [
                    {
                        "x": float(x_value),
                        "delta": float(delta_value),
                        "C": float(constraint_value),
                        "D": float(depth_value),
                        **(
                            {"ratchet_gate": float(gate_value)}
                            if "ratchet_gate" in snapshot
                            else {}
                        ),
                        **(
                            {"delta_phi_min": float(delta_phi_min_value)}
                            if "delta_phi_min" in snapshot
                            else {}
                        ),
                        **(
                            {"kappa_proxy": float(kappa_proxy_value)}
                            if "kappa_proxy" in snapshot
                            else {}
                        ),
                    }
                    for x_value, delta_value, constraint_value, depth_value, gate_value, delta_phi_min_value, kappa_proxy_value in zip(
                        profile["x"],
                        np.asarray(snapshot["delta"], dtype=float),
                        np.asarray(snapshot["C"], dtype=float),
                        np.asarray(snapshot["D"], dtype=float),
                        np.asarray(snapshot.get("ratchet_gate", np.full_like(np.asarray(snapshot["C"], dtype=float), np.nan)), dtype=float),
                        np.asarray(snapshot.get("delta_phi_min", np.full_like(np.asarray(snapshot["C"], dtype=float), np.nan)), dtype=float),
                        np.asarray(snapshot.get("kappa_proxy", np.full_like(np.asarray(snapshot["C"], dtype=float), np.nan)), dtype=float),
                    )
                ]
                relational_columns = ["x", "delta", "C", "D"]
                if "ratchet_gate" in snapshot:
                    relational_columns.append("ratchet_gate")
                if "delta_phi_min" in snapshot:
                    relational_columns.append("delta_phi_min")
                if "kappa_proxy" in snapshot:
                    relational_columns.append("kappa_proxy")
                write_csv(
                    relational_profile_filename(run_id, time_value),
                    relational_rows,
                    relational_columns,
                )

        node_ratio_stack.append(profile["node_ratio"])
        residue_stack.append(profile["R"])
        if "delta" in snapshot and "sigma" in snapshot:
            final_delta_snapshot = np.asarray(snapshot["delta"], dtype=float)
            final_sigma_snapshot = np.asarray(snapshot["sigma"], dtype=float)
            final_rho_snapshot = np.asarray(snapshot["rho"], dtype=float)
            final_depth_snapshot = np.asarray(snapshot.get("depth", np.zeros_like(final_delta_snapshot)), dtype=float)
            final_delta_floor_snapshot = np.asarray(snapshot.get("delta_floor", np.zeros_like(final_delta_snapshot)), dtype=float)
            dsr_branch_detected = dsr_branch_detected or ("delta_floor" in snapshot)
            if "delta_floor" in snapshot:
                dsr_profile_times.append(float(time_value))
                dsr_metrics_history.append(
                    compute_dsr_metrics(
                        delta=final_delta_snapshot,
                        sigma=final_sigma_snapshot,
                        rho=final_rho_snapshot,
                        depth=final_depth_snapshot,
                        delta_floor=final_delta_floor_snapshot,
                    )
                )
        elif "delta" in snapshot and "C" in snapshot:
            ontology_delta_snapshot = np.asarray(snapshot["delta"], dtype=float)
            ontology_constraint_snapshot = np.asarray(snapshot["C"], dtype=float)
            ontology_depth_snapshot = np.asarray(snapshot.get("D", np.zeros_like(ontology_delta_snapshot)), dtype=float)
            current_delta_phi_min = float(
                np.nanmax(np.asarray(snapshot.get("delta_phi_min", np.array([results.get("ontology_delta_phi_min", 0.0)])), dtype=float))
            )
            current_peak_delta = float(np.max(ontology_delta_snapshot))
            ontology_delta_phi_min = current_delta_phi_min
            ontology_peak_max_delta = max(ontology_peak_max_delta, current_peak_delta)
            ontology_profile_times.append(float(time_value))
            ontology_profile_peak_deltas.append(current_peak_delta)
            if current_peak_delta >= current_delta_phi_min:
                if ontology_persistence_start is None:
                    ontology_persistence_start = float(time_value)
                ontology_persistence_end = float(time_value)
            ontology_final_kappa_proxy = float(
                np.nanmax(np.asarray(snapshot.get("kappa_proxy", np.array([results.get("ontology_kappa_proxy", 0.0)])), dtype=float))
            )
            if previous_ontology_delta is not None and previous_ontology_time is not None and len(ontology_delta_snapshot) > 1:
                dt = max(float(time_value) - previous_ontology_time, 1.0e-12)
                speed_proxy = np.abs((ontology_delta_snapshot - previous_ontology_delta) / dt) / (
                    np.abs(gradient_neumann(ontology_delta_snapshot, dx)) + max(float(params.ont_eps_speed), 1.0e-12)
                )
                ontology_peak_speed_ratio = max(
                    ontology_peak_speed_ratio,
                    float(np.max(speed_proxy)) / max(float(params.ont_c_flat), 1.0e-12),
                )
            previous_ontology_delta = ontology_delta_snapshot.copy()
            previous_ontology_time = float(time_value)

    run_fronts = track_fronts(run_front_frames, max_match_distance=4.0 * dx)
    classification = classify_run(
        run_timeseries,
        run_fronts,
        bool(results["blew_up"]),
        int(results.get("negative_undershoot_events", results["nonnegativity_violations"])),
    )
    summary = final_summary_row(run_id, classification, run_timeseries, run_fronts)
    summary.update(
        {
            "lam": params.lam,
            "D_eps": params.D_eps,
            "D_rho": params.D_rho,
            "kappa": params.kappa,
        }
    )
    if final_delta_snapshot is not None and final_sigma_snapshot is not None:
        summary["final_mean_Delta"] = float(np.mean(final_delta_snapshot))
        summary["final_mean_Sigma"] = float(np.mean(final_sigma_snapshot))
    elif ontology_delta_snapshot is not None and ontology_constraint_snapshot is not None:
        summary["final_mean_Delta"] = float(np.mean(ontology_delta_snapshot))
        summary["final_mean_Sigma"] = float(np.mean(ontology_constraint_snapshot))
    else:
        summary["final_mean_Delta"] = ""
        summary["final_mean_Sigma"] = ""
    summary["dsr_local_label"] = ""
    summary["dsr_branch_converged"] = ""
    summary["dsr_delta_floor_ratio"] = ""
    summary["dsr_excess_floor_ratio"] = ""
    summary["dsr_delta_floor_correlation"] = ""
    summary["dsr_sigma_floor_ratio"] = ""
    summary["dsr_rho_floor_ratio"] = ""
    summary["dsr_sign_match_fraction"] = ""
    summary["dsr_tail_count"] = ""
    summary["dsr_late_window"] = ""
    summary["dsr_tail_floor_locked_fraction"] = ""
    summary["dsr_tail_bounded_support_fraction"] = ""
    summary["dsr_tail_delta_floor_ratio_spread"] = ""
    summary["dsr_tail_max_excess_floor_ratio"] = ""
    summary["dsr_tail_min_delta_floor_correlation"] = ""
    summary["dsr_tail_min_sign_match_fraction"] = ""
    summary["dsr_tail_max_sigma_floor_ratio"] = ""
    summary["dsr_tail_max_rho_floor_ratio"] = ""
    branch_classification = classification
    classification_source = "legacy_mapped_back"
    branch_converged: bool | str = classification not in {"runaway_or_unphysical", "undetermined"}
    if dsr_branch_detected:
        late_tail_summary = summarize_dsr_late_tail(
            dsr_profile_times,
            dsr_metrics_history,
            min_tail_count=5,
        )
        dsr_metrics = compute_dsr_metrics(
            delta=final_delta_snapshot if final_delta_snapshot is not None else np.asarray([], dtype=float),
            sigma=final_sigma_snapshot if final_sigma_snapshot is not None else np.asarray([], dtype=float),
            rho=final_rho_snapshot if final_rho_snapshot is not None else np.asarray([], dtype=float),
            depth=final_depth_snapshot if final_depth_snapshot is not None else np.asarray([], dtype=float),
            delta_floor=final_delta_floor_snapshot if final_delta_floor_snapshot is not None else np.asarray([], dtype=float),
        )
        dsr_classification = classify_dsr_metrics(
            dsr_metrics,
            ratchet_event_steps=int(results.get("ratchet_event_steps", 0)),
            seed_update_steps=int(results.get("seed_update_steps", 0)),
            late_tail_summary=late_tail_summary,
        )
        branch_classification = str(dsr_classification["label"])
        classification_source = "dsr_local"
        branch_converged = bool(dsr_classification["converged"])
        summary["dsr_local_label"] = branch_classification
        summary["dsr_branch_converged"] = str(branch_converged).lower()
        summary["dsr_delta_floor_ratio"] = dsr_metrics["delta_floor_ratio"]
        summary["dsr_excess_floor_ratio"] = dsr_metrics["excess_floor_ratio"]
        summary["dsr_delta_floor_correlation"] = dsr_metrics["delta_floor_correlation"]
        summary["dsr_sigma_floor_ratio"] = dsr_metrics["sigma_floor_ratio"]
        summary["dsr_rho_floor_ratio"] = dsr_metrics["rho_floor_ratio"]
        summary["dsr_sign_match_fraction"] = dsr_metrics["sign_match_fraction"]
        summary["dsr_tail_count"] = int(late_tail_summary["tail_count"])
        summary["dsr_late_window"] = late_tail_summary["late_window"]
        summary["dsr_tail_floor_locked_fraction"] = late_tail_summary["floor_locked_fraction"]
        summary["dsr_tail_bounded_support_fraction"] = late_tail_summary["bounded_support_fraction"]
        summary["dsr_tail_delta_floor_ratio_spread"] = late_tail_summary["delta_floor_ratio_spread"]
        summary["dsr_tail_max_excess_floor_ratio"] = late_tail_summary["max_excess_floor_ratio"]
        summary["dsr_tail_min_delta_floor_correlation"] = late_tail_summary["min_delta_floor_correlation"]
        summary["dsr_tail_min_sign_match_fraction"] = late_tail_summary["min_sign_match_fraction"]
        summary["dsr_tail_max_sigma_floor_ratio"] = late_tail_summary["max_sigma_floor_ratio"]
        summary["dsr_tail_max_rho_floor_ratio"] = late_tail_summary["max_rho_floor_ratio"]
    elif ontology_delta_snapshot is not None and ontology_constraint_snapshot is not None and ontology_depth_snapshot is not None:
        ontology_persistence_window = 0.0
        if ontology_persistence_start is not None and ontology_persistence_end is not None:
            ontology_persistence_window = max(0.0, ontology_persistence_end - ontology_persistence_start)
        ontology_late_time_slope = fit_tail_slope(ontology_profile_times, ontology_profile_peak_deltas)
        ontology_residue_written = (ontology_final_kappa_proxy >= 1.0) or (float(np.mean(ontology_depth_snapshot)) > 1.0e-5)
        branch_classification = classify_ontology_branch(
            peak_max_delta=ontology_peak_max_delta,
            final_max_delta=float(np.max(ontology_delta_snapshot)),
            delta_phi_min=ontology_delta_phi_min,
            final_mean_constraint=float(np.mean(ontology_constraint_snapshot)),
            final_mean_depth=float(np.mean(ontology_depth_snapshot)),
            residue_written=ontology_residue_written,
            persistence_window=ontology_persistence_window,
            late_time_slope=ontology_late_time_slope,
        )
        classification_source = "ontology_local"
        branch_converged = branch_classification in {"metastable", "persistent"}
        summary["ontology_residue_written"] = str(ontology_residue_written).lower()
        summary["ontology_persistence_window"] = ontology_persistence_window
        summary["ontology_late_time_slope"] = ontology_late_time_slope
        summary["ontology_local_label"] = branch_classification
        summary["broad_summary_label"] = classification
    else:
        summary["ontology_residue_written"] = ""
        summary["ontology_persistence_window"] = ""
        summary["ontology_late_time_slope"] = ""
        summary["ontology_local_label"] = ""
        summary["broad_summary_label"] = classification
    return {
        "timeseries": run_timeseries,
        "fronts": run_fronts,
        "classification": classification,
        "branch_classification": branch_classification,
        "classification_source": classification_source,
        "branch_converged": branch_converged,
        "summary": summary,
        "node_ratio_stack": np.asarray(node_ratio_stack),
        "residue_stack": np.asarray(residue_stack),
    }


def evaluate_convergence(reference: Dict[str, object], trials: List[Dict[str, object]], rules: Dict) -> bool:
    if not trials:
        return False

    ref_summary = reference["summary"]
    ref_source = str(reference.get("classification_source", "legacy_mapped_back"))
    ref_class = str(reference.get("branch_classification", reference["classification"])) if ref_source != "legacy_mapped_back" else str(reference["classification"])

    for trial in trials:
        trial_summary = trial["summary"]
        trial_source = str(trial.get("classification_source", "legacy_mapped_back"))
        trial_class = str(trial.get("branch_classification", trial["classification"])) if trial_source != "legacy_mapped_back" else str(trial["classification"])
        if rules.get("classification_must_match", True) and trial_class != ref_class:
            return False
        if ref_source != "legacy_mapped_back" and rules.get("classification_source_must_match", True) and trial_source != ref_source:
            return False
        if abs(float(trial_summary["final_exclusion_fraction"]) - float(ref_summary["final_exclusion_fraction"])) > float(rules.get("exclusion_fraction_tolerance", 0.08)):
            return False
        if abs(float(trial_summary["late_time_mean_front_speed"]) - float(ref_summary["late_time_mean_front_speed"])) > float(rules.get("front_speed_tolerance", 0.15)):
            return False
        if abs(int(trial_summary["final_interface_count"]) - int(ref_summary["final_interface_count"])) > int(rules.get("interface_count_tolerance", 0)):
            return False
    return True


def run_convergence_checks(
    spec: Dict,
    params: Parameters,
    grid_spec: Dict,
    ic_spec: Dict,
    seed: int,
    phase_expression: str,
    reference_result: Dict[str, object],
) -> tuple[bool, bool]:
    rules = spec.get("convergence_checks")
    if not rules:
        return False, False

    resolution_trials: List[Dict[str, object]] = []
    for nx in rules.get("Nx_values", []):
        if int(nx) == int(grid_spec["Nx"]):
            continue
        check_grid_spec = deep_copy_json(grid_spec)
        check_grid_spec["Nx"] = int(nx)
        check_grid = GridConfig(**check_grid_spec)
        initial_state = build_initial_condition(check_grid, ic_spec, seed)
        results = simulate(params, check_grid, initial_state, phase_expression=phase_expression)
        resolution_trials.append(
            summarise_run("convergence_resolution", params, results, write_profiles=False)
        )

    dt_trials: List[Dict[str, object]] = []
    for dt_value in rules.get("dt_values", []):
        if abs(float(dt_value) - float(grid_spec["dt"])) < 1.0e-12:
            continue
        check_grid_spec = deep_copy_json(grid_spec)
        check_grid_spec["dt"] = float(dt_value)
        check_grid = GridConfig(**check_grid_spec)
        initial_state = build_initial_condition(check_grid, ic_spec, seed)
        results = simulate(params, check_grid, initial_state, phase_expression=phase_expression)
        dt_trials.append(
            summarise_run("convergence_dt", params, results, write_profiles=False)
        )

    resolution_pass = evaluate_convergence(reference_result, resolution_trials, rules)
    stability_pass = evaluate_convergence(reference_result, dt_trials, rules)
    return resolution_pass, stability_pass


def execute_single_run(task: Dict[str, object]) -> Dict[str, object]:
    output_root = Path(str(task["output_root"])).resolve()
    set_output_root(output_root)
    ensure_layout()
    spec = deep_copy_json(task["spec"])
    grid_spec = deep_copy_json(task["grid_spec"])
    params = Parameters(**task["parameters"])
    seed = int(task["seed"])
    ic_index = int(task["ic_index"])
    ic_spec = deep_copy_json(task["ic_spec"])
    run_id = str(task["run_id"])
    with_convergence_checks = bool(task["with_convergence_checks"])
    write_profiles = bool(task["write_profiles"])
    write_figures = bool(task["write_figures"])
    profile_tail_count = task["profile_tail_count"]
    backend = str(task["backend"])
    native_threads = task["native_threads"]
    sim_id = str(task["sim_id"])
    batch_id = str(task["batch_id"])
    run_date = str(task["run_date"])
    phase_expression = str(task["phase_expression"])

    if backend in {"auto", "native"} and native_threads is not None and is_native_backend_available():
        set_native_backend_threads(int(native_threads))

    grid = GridConfig(**grid_spec)
    delta_calibration_family = ""
    delta_alpha_identifiable = ""
    delta_calibration_scope = ""
    delta_calibration_source = ""
    delta_calibration_status = ""
    dsr_commitments_source = ""
    if phase_expression in {"I_phi_v3_delta_sigma_rho", "I_phi_v4_dsr"}:
        calibration = resolve_delta_sigma_calibration(spec, str(ic_spec["type"]))
        params.delta_alpha = calibration.alpha
        params.delta_beta = calibration.beta
        delta_calibration_family = calibration.family
        delta_alpha_identifiable = str(calibration.identifiable).lower()
        delta_calibration_scope = calibration.scope
        delta_calibration_source = calibration.source
        delta_calibration_status = calibration.status
    if phase_expression == "I_phi_v4_dsr":
        dsr_commitments_source = str(DEFAULT_DSR_COMMITMENTS_PATH)

    initial_state = build_initial_condition(grid, ic_spec, seed)
    results = simulate(params, grid, initial_state, backend=backend, phase_expression=phase_expression)
    run_result = summarise_run(
        run_id,
        params,
        results,
        write_profiles=write_profiles,
        profile_tail_count=profile_tail_count,
    )

    resolution_check_pass = False
    stability_check_pass = False
    if with_convergence_checks:
        resolution_check_pass, stability_check_pass = run_convergence_checks(
            spec=spec,
            params=params,
            grid_spec=grid_spec,
            ic_spec=ic_spec,
            seed=seed,
            phase_expression=phase_expression,
            reference_result=run_result,
        )

    classification = str(run_result["classification"])
    branch_classification = str(run_result["branch_classification"])
    classification_source = str(run_result["classification_source"])
    converged = classification not in {"runaway_or_unphysical", "undetermined"}
    branch_converged = run_result["branch_converged"]
    pi_value = safe_pi_value(params.kappa, params.lam)
    manifest_row = {
        "run_id": run_id,
        "sim_id": sim_id,
        "batch_id": batch_id,
        "run_date": run_date,
        "seed": seed,
        "ic_type": ic_spec["type"],
        "IC_type": ic_spec["type"],
        "phase_expression": phase_expression,
        "L": grid.L,
        "Nx": grid.Nx,
        "dx": grid.dx,
        "dt": grid.dt,
        "t_final": grid.t_final,
        **asdict(params),
        "lambda": params.lam,
        "exclusion_rate_k": params.lam,
        "topology_writing_rate_kappa": params.kappa,
        "topology_persistence_lambda": params.lam,
        "inscription_dominance_Pi": pi_value,
        "dsr_commitments_source": dsr_commitments_source,
        "ratchet_event_steps": int(results.get("ratchet_event_steps", 0)),
        "seed_update_steps": int(results.get("seed_update_steps", 0)),
        "delta_family": delta_calibration_family,
        "delta_alpha_identifiable": delta_alpha_identifiable,
        "delta_calibration_scope": delta_calibration_scope,
        "delta_calibration_source": delta_calibration_source,
        "delta_calibration_status": delta_calibration_status,
        "ontology_delta_phi_min": results.get("ontology_delta_phi_min", ""),
        "ontology_kappa_proxy": results.get("ontology_kappa_proxy", ""),
        "ontology_gate_integral": results.get("ontology_gate_integral", ""),
        "ontology_ratchet_active_steps": results.get("ontology_ratchet_active_steps", ""),
        "classification": classification,
        "branch_classification": branch_classification,
        "classification_source": classification_source,
        "converged": converged,
        "branch_converged": branch_converged,
        "notes": spec.get("label", ""),
    }
    summary = dict(run_result["summary"])
    continuation_attempts = compute_continuation_attempts(run_result["fronts"])
    exclusion_events = compute_exclusion_events(run_result["timeseries"])
    alignment_success_rate = compute_alignment_success_rate(run_result["timeseries"])
    collapse_time = compute_collapse_time(run_result["timeseries"])
    l_proxy = compute_l_proxy(run_result["timeseries"])
    k_proxy = float(max((row["interface_count"] for row in run_result["timeseries"]), default=0.0))
    d_sr_proxy = compute_d_sr_proxy(summary)
    stability_time = compute_stability_time(run_result["timeseries"])
    summary.update(
        {
            "sim_id": sim_id,
            "batch_id": batch_id,
            "run_date": run_date,
            "seed": seed,
            "IC_type": ic_spec["type"],
            "phase_expression": phase_expression,
            "lambda": params.lam,
            "exclusion_rate_k": params.lam,
            "continuation_attempts": continuation_attempts,
            "exclusion_events": exclusion_events,
            "alignment_success_rate": alignment_success_rate,
            "topology_writing_rate_kappa": params.kappa,
            "topology_persistence_lambda": params.lam,
            "inscription_dominance_Pi": pi_value,
            "residue_field_R_mean": summary["final_mean_R"],
            "epsilon_mean": summary["final_mean_eps"],
            "rho_mean": summary["final_mean_rho"],
            "exclusion_fraction": summary["final_exclusion_fraction"],
            "collapse_time": collapse_time,
            "regime_classification": classification,
            "seed_unanimity": "",
            "branch_classification": branch_classification,
            "classification_source": classification_source,
            "branch_converged": branch_converged,
            "stability_time": stability_time,
            "eta_kappa": params.eta_kappa,
            "eta_u": params.eta_u,
            "mu": params.mu,
            "nu": params.nu,
            "delta_alpha": params.delta_alpha,
            "delta_beta": params.delta_beta,
            "dsr_lambda_D": params.dsr_lambda_D,
            "dsr_theta": params.dsr_theta,
            "dsr_event_gain": params.dsr_event_gain,
            "dsr_sigma_decay": params.dsr_sigma_decay,
            "dsr_sigma_load": params.dsr_sigma_load,
            "dsr_rho_gain": params.dsr_rho_gain,
            "dsr_rho_relax": params.dsr_rho_relax,
            "dsr_bootstrap_gain": params.dsr_bootstrap_gain,
            "ont_M0": params.ont_M0,
            "ont_aC": params.ont_aC,
            "ont_aD": params.ont_aD,
            "ont_lambda": params.ont_lambda,
            "ont_chi": params.ont_chi,
            "ont_kappa_D": params.ont_kappa_D,
            "ont_alpha_C": params.ont_alpha_C,
            "ont_mu_C": params.ont_mu_C,
            "ont_nu_C": params.ont_nu_C,
            "ont_beta_D": params.ont_beta_D,
            "ont_eta_D": params.ont_eta_D,
            "ont_theta0": params.ont_theta0,
            "ont_theta1": params.ont_theta1,
            "ont_epsilon_gate": params.ont_epsilon_gate,
            "ont_gamma_flat": params.ont_gamma_flat,
            "ont_c_flat": params.ont_c_flat,
            "ont_p_flat": params.ont_p_flat,
            "ont_ell_min": params.ont_ell_min,
            "ont_eps_speed": params.ont_eps_speed,
            "dsr_commitments_source": dsr_commitments_source,
            "ratchet_event_steps": int(results.get("ratchet_event_steps", 0)),
            "seed_update_steps": int(results.get("seed_update_steps", 0)),
            "delta_family": delta_calibration_family,
            "delta_alpha_identifiable": delta_alpha_identifiable,
            "delta_calibration_scope": delta_calibration_scope,
            "delta_calibration_source": delta_calibration_source,
            "delta_calibration_status": delta_calibration_status,
            "ontology_delta_phi_min": results.get("ontology_delta_phi_min", ""),
            "ontology_kappa_proxy": results.get("ontology_kappa_proxy", ""),
            "ontology_gate_integral": results.get("ontology_gate_integral", ""),
            "ontology_ratchet_active_steps": results.get("ontology_ratchet_active_steps", ""),
            "D_sr_proxy": d_sr_proxy,
            "K_proxy": k_proxy,
            "L_proxy": l_proxy,
        }
    )
    summary["resolution_check_pass"] = resolution_check_pass
    summary["stability_check_pass"] = stability_check_pass
    summary["lam"] = params.lam
    summary["kappa"] = params.kappa
    summary["D_eps"] = params.D_eps
    summary["D_rho"] = params.D_rho

    figure_paths = {
        "front_position": str(FIGURE_DIR / f"{run_id}_front_position.png"),
        "node_ratio_kymograph": str(FIGURE_DIR / f"{run_id}_node_ratio_kymograph.png"),
        "residue_kymograph": str(FIGURE_DIR / f"{run_id}_residue_kymograph.png"),
    }

    return {
        "run_id": run_id,
        "write_figures": write_figures,
        "manifest_row": manifest_row,
        "timeseries_rows": [{key: row[key] for key in TIMESERIES_COLUMNS} for row in run_result["timeseries"]],
        "domain_rows": [{key: row[key] for key in DOMAIN_COLUMNS} for row in run_result["timeseries"]],
        "front_rows": [{key: row[key] for key in FRONT_COLUMNS} for row in run_result["fronts"]],
        "summary_row": summary,
        "x": np.asarray(results["x"]),
        "times": list(results["times"]),
        "node_ratio_stack": np.asarray(run_result["node_ratio_stack"]),
        "residue_stack": np.asarray(run_result["residue_stack"]),
        "fronts": run_result["fronts"],
        "figure_paths": figure_paths,
    }


def format_seconds(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def print_progress(completed_count: int, total_count: int, run_id: str, start_time: float) -> None:
    percent = 100.0 if total_count == 0 else (100.0 * completed_count / total_count)
    elapsed = max(0.0, time.perf_counter() - start_time)
    rate = 0.0 if completed_count == 0 else elapsed / completed_count
    remaining = max(0, total_count - completed_count)
    eta_seconds = rate * remaining
    elapsed_text = format_seconds(elapsed)
    eta_text = format_seconds(eta_seconds)
    print(
        f"[{completed_count}/{total_count}] {percent:5.1f}% complete - elapsed {elapsed_text} - ETA {eta_text} - {run_id}",
        flush=True,
    )


def main() -> None:
    args = parse_args()
    if args.output_root is not None:
        set_output_root(Path(args.output_root).resolve())
    if args.clean:
        clean_outputs()
    else:
        ensure_layout()
    run_specs = expand_run_specs(args.config)
    if args.max_runs is not None:
        run_specs = run_specs[:args.max_runs]

    write_profiles = (not args.fast) or args.write_profiles
    write_figures = (not args.fast) and (not args.skip_figures)
    batch_id = derive_batch_id(OUTPUT_DIR)
    run_date = run_date_utc()

    tasks: List[Dict[str, object]] = []
    for run_index, spec in enumerate(run_specs):
        grid_spec = deep_copy_json(spec["grid"])
        if args.t_final is not None:
            grid_spec["t_final"] = args.t_final
        if args.save_every is not None:
            grid_spec["save_every"] = args.save_every

        grid = GridConfig(**grid_spec)
        params = Parameters(**spec["parameters"])
        seeds = spec.get("seeds", [0])
        ic_specs = spec.get("initial_conditions", [])
        sim_id = str(spec.get("sim_id", spec.get("label", "sim")))
        phase_expression = str(spec.get("phase_expression", "standard"))

        for seed in seeds:
            for ic_index, ic_spec in enumerate(ic_specs):
                run_id = f"{spec.get('label', 'run')}_{run_index:03d}_s{seed}_ic{ic_index}"
                tasks.append(
                    {
                        "spec": spec,
                        "grid_spec": grid_spec,
                        "parameters": asdict(params),
                        "seed": seed,
                        "ic_index": ic_index,
                        "ic_spec": ic_spec,
                        "run_id": run_id,
                        "with_convergence_checks": args.with_convergence_checks,
                        "write_profiles": write_profiles,
                        "write_figures": write_figures,
                        "profile_tail_count": args.profile_tail_count,
                        "backend": args.backend,
                        "native_threads": args.native_threads,
                        "output_root": str(OUTPUT_DIR.resolve()),
                        "sim_id": sim_id,
                        "batch_id": batch_id,
                        "run_date": run_date,
                        "phase_expression": phase_expression,
                    }
                )

    completed_runs: List[Dict[str, object]] = []
    total_tasks = len(tasks)
    start_time = time.perf_counter()
    effective_jobs = args.jobs
    if effective_jobs > 1:
        worker_count = min(effective_jobs, total_tasks)
        mp_context = multiprocessing.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count, mp_context=mp_context) as executor:
            future_to_task = {executor.submit(execute_single_run, task): task for task in tasks}
            completed_count = 0
            for future in concurrent.futures.as_completed(future_to_task):
                result = future.result()
                completed_runs.append(result)
                completed_count += 1
                print_progress(completed_count, total_tasks, str(result["run_id"]), start_time)
    else:
        for index, task in enumerate(tasks, start=1):
            result = execute_single_run(task)
            completed_runs.append(result)
            print_progress(index, total_tasks, str(result["run_id"]), start_time)

    manifest_rows: List[Dict] = []
    timeseries_rows: List[Dict] = []
    front_rows: List[Dict] = []
    domain_rows: List[Dict] = []
    summary_rows: List[Dict] = []

    for completed in completed_runs:
        manifest_rows.append(completed["manifest_row"])
        timeseries_rows.extend(completed["timeseries_rows"])
        domain_rows.extend(completed["domain_rows"])
        front_rows.extend(completed["front_rows"])
        summary_rows.append(completed["summary_row"])

        if completed["write_figures"]:
            plot_kymograph(
                completed["x"],
                completed["times"],
                completed["node_ratio_stack"],
                completed["figure_paths"]["node_ratio_kymograph"],
                "Node Ratio Kymograph",
            )
            plot_kymograph(
                completed["x"],
                completed["times"],
                completed["residue_stack"],
                completed["figure_paths"]["residue_kymograph"],
                "Residue Kymograph",
                cmap="magma",
            )
            plot_front_position(completed["fronts"], completed["figure_paths"]["front_position"])

    summary_groups: Dict[tuple[str, str, float, float], List[Dict]] = {}
    for row in summary_rows:
        key = (
            str(row.get("sim_id", "")),
            str(row.get("phase_expression", "")),
            float(row.get("kappa", 0.0)),
            float(row.get("lambda", row.get("lam", 0.0))),
        )
        summary_groups.setdefault(key, []).append(row)

    seed_unanimity_by_key: Dict[tuple[str, str, float, float], str] = {}
    for key, rows in summary_groups.items():
        classifications = {
            str(row.get("regime_classification", row.get("classification", "")))
            for row in rows
        }
        seed_unanimity_by_key[key] = str(len(classifications) == 1).lower()
        for row in rows:
            row["seed_unanimity"] = seed_unanimity_by_key[key]

    for row in manifest_rows:
        key = (
            str(row.get("sim_id", "")),
            str(row.get("phase_expression", "")),
            float(row.get("kappa", 0.0)),
            float(row.get("lambda", row.get("lam", 0.0))),
        )
        row["seed_unanimity"] = seed_unanimity_by_key.get(key, "")

    write_csv(OUTPUT_DIR / "run_manifest.csv", manifest_rows, RUN_MANIFEST_COLUMNS)
    write_csv(OUTPUT_DIR / "timeseries_global.csv", timeseries_rows, TIMESERIES_COLUMNS)
    write_csv(OUTPUT_DIR / "front_metrics.csv", front_rows, FRONT_COLUMNS)
    write_csv(OUTPUT_DIR / "domain_metrics.csv", domain_rows, DOMAIN_COLUMNS)
    write_csv(OUTPUT_DIR / "final_summary.csv", summary_rows, FINAL_SUMMARY_COLUMNS)
    if write_figures:
        plot_front_velocity_vs_parameter(summary_rows, "lam", str(FIGURE_DIR / "front_velocity_vs_lambda.png"))
        plot_phase_map(summary_rows, "lam", "D_eps", str(FIGURE_DIR / "phase_map_lambda_D_eps.png"))
        plot_phase_map(summary_rows, "lam", "kappa", str(FIGURE_DIR / "phase_map_lambda_kappa.png"))


if __name__ == "__main__":
    main()
