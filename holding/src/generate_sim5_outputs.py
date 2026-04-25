from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev

from .native_backend import native_backend_max_threads
from . import native_backend_name


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sim5 summary outputs from a completed batch_runner output root.")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--phase-name", required=True)
    parser.add_argument("--kappa-values", nargs="+", required=True)
    parser.add_argument("--lambda-values", nargs="+", required=True)
    parser.add_argument("--grid-size", type=int, required=True)
    parser.add_argument("--t-max", type=float, required=True)
    parser.add_argument("--seed-list", nargs="+", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--recommended-next-action", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.output_root).resolve()

    run_manifest = load_csv_rows(root / "run_manifest.csv")
    final_summary = {row["run_id"]: row for row in load_csv_rows(root / "final_summary.csv")}
    timeseries_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in load_csv_rows(root / "timeseries_global.csv"):
        timeseries_by_run[row["run_id"]].append(row)

    run_results: list[dict[str, str]] = []
    point_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)

    for manifest in run_manifest:
        run_id = manifest["run_id"]
        summary = final_summary[run_id]
        series = timeseries_by_run[run_id]
        t_max = float(manifest["t_final"])

        exclusion_time = None
        max_interface_count = 0
        interface_loss_time = None
        for row in series:
            time_value = float(row["time"])
            exclusion_fraction = float(row["exclusion_fraction"])
            interface_count = int(float(row["interface_count"]))
            max_interface_count = max(max_interface_count, interface_count)
            if exclusion_time is None and exclusion_fraction >= 1.0:
                exclusion_time = time_value
            if interface_loss_time is None and interface_count == 0:
                interface_loss_time = time_value

        collapsed = exclusion_time is not None
        time_to_exclusion = exclusion_time if exclusion_time is not None else t_max
        interface_lifetime = interface_loss_time if interface_loss_time is not None else t_max
        final_mean_rho = float(summary["final_mean_rho"])
        rho_plateau_duration = t_max if final_mean_rho > 0.0 else 0.0
        ic_family = manifest["run_id"].rsplit("_ic", 1)[1]

        row = {
            "run_id": run_id,
            "kappa": manifest["kappa"],
            "lambda": manifest["lam"],
            "D_eps": manifest["D_eps"],
            "D_rho": manifest["D_rho"],
            "IC_family": ic_family,
            "replicate_id": manifest["seed"],
            "seed": manifest["seed"],
            "T_max": manifest["t_final"],
            "collapsed_bool": str(collapsed),
            "time_to_full_exclusion": f"{time_to_exclusion:.6f}",
            "final_exclusion_fraction": summary["final_exclusion_fraction"],
            "final_mean_rho": summary["final_mean_rho"],
            "final_mean_R": summary["final_mean_R"],
            "final_mean_eps": summary["final_mean_eps"],
            "max_interface_count": str(max_interface_count),
            "late_time_front_speed": summary["late_time_mean_front_speed"],
            "interface_lifetime": f"{interface_lifetime:.6f}",
            "rho_plateau_duration": f"{rho_plateau_duration:.6f}",
            "resolution_check_pass": str(summary.get("resolution_check_pass", "")),
            "stability_check_pass": str(summary.get("stability_check_pass", "")),
            "source_classification": manifest["classification"],
        }
        run_results.append(row)
        point_groups[(manifest["D_eps"], manifest["D_rho"], manifest["kappa"], manifest["lam"])].append(row)

    run_fields = [
        "run_id", "kappa", "lambda", "D_eps", "D_rho", "IC_family", "replicate_id", "seed", "T_max",
        "collapsed_bool", "time_to_full_exclusion", "final_exclusion_fraction", "final_mean_rho",
        "final_mean_R", "final_mean_eps", "max_interface_count", "late_time_front_speed",
        "interface_lifetime", "rho_plateau_duration", "resolution_check_pass", "stability_check_pass",
        "source_classification",
    ]
    write_csv(root / "run_results.csv", run_results, run_fields)

    parameter_rows: list[dict[str, str]] = []
    by_kappa: dict[str, list[dict[str, str]]] = defaultdict(list)
    sorted_groups = sorted(point_groups.items(), key=lambda item: tuple(float(x) for x in item[0]))

    previous_by_kappa: dict[str, dict[str, str] | None] = {}
    for (d_eps, d_rho, kappa, lam), rows in sorted_groups:
        collapse_times = [float(r["time_to_full_exclusion"]) for r in rows]
        collapse_fraction = sum(r["collapsed_bool"] == "True" for r in rows) / len(rows)
        mean_time = mean(collapse_times)
        std_time = pstdev(collapse_times) if len(collapse_times) > 1 else 0.0
        max_time = max(collapse_times)
        mean_final_excl = mean(float(r["final_exclusion_fraction"]) for r in rows)
        mean_final_rho = mean(float(r["final_mean_rho"]) for r in rows)
        mean_final_r = mean(float(r["final_mean_R"]) for r in rows)
        mean_final_eps = mean(float(r["final_mean_eps"]) for r in rows)
        mean_speed = mean(float(r["late_time_front_speed"]) for r in rows)
        mean_interface_lifetime = mean(float(r["interface_lifetime"]) for r in rows)

        ic_intervals: dict[str, list[float]] = defaultdict(lambda: [float("inf"), float("-inf")])
        for row in rows:
            time_value = float(row["time_to_full_exclusion"])
            interval = ic_intervals[row["IC_family"]]
            interval[0] = min(interval[0], time_value)
            interval[1] = max(interval[1], time_value)
        intervals = list(ic_intervals.values())
        if intervals:
            union_min = min(interval[0] for interval in intervals)
            union_max = max(interval[1] for interval in intervals)
            union_length = max(0.0, union_max - union_min)
            overlap_sum = 0.0
            for i in range(len(intervals)):
                for j in range(i + 1, len(intervals)):
                    overlap_sum += max(0.0, min(intervals[i][1], intervals[j][1]) - max(intervals[i][0], intervals[j][0]))
            ic_overlap_index = 0.0 if union_length == 0.0 else min(1.0, overlap_sum / union_length)
        else:
            ic_overlap_index = 0.0

        any_survive = any(row["collapsed_bool"] == "False" for row in rows)
        any_non_exclusion = any(float(row["final_exclusion_fraction"]) < 1.0 for row in rows)
        any_positive_rho = any(float(row["final_mean_rho"]) > 0.0 for row in rows)
        all_full_exclusion = all(row["collapsed_bool"] == "True" for row in rows)
        all_zero_rho = all(abs(float(row["final_mean_rho"])) < 1.0e-12 for row in rows)

        if any_survive and any_non_exclusion and any_positive_rho:
            behavior_class = "R1_bounded_persistence"
        elif any(row["collapsed_bool"] == "True" for row in rows) and any(row["collapsed_bool"] == "False" for row in rows):
            behavior_class = "R1m_mixed_regime"
        elif all_full_exclusion and all_zero_rho:
            behavior_class = "R2_global_exclusion_runaway"
        else:
            behavior_class = "unmapped"

        soft_subclass = ""
        if behavior_class == "R2_global_exclusion_runaway":
            previous = previous_by_kappa.get(kappa)
            mean_speed_drop = False
            mean_time_jump = False
            variance_jump = False
            if previous is not None:
                prev_mean_time = float(previous["mean_time_to_exclusion"])
                prev_std_time = float(previous["std_time_to_exclusion"])
                prev_speed = float(previous["mean_late_time_front_speed"])
                mean_time_jump = mean_time >= 1.5 * prev_mean_time if prev_mean_time > 0.0 else False
                variance_jump = std_time >= 2.0 * prev_std_time if prev_std_time > 0.0 else std_time > 0.0
                mean_speed_drop = mean_speed <= 0.5 * prev_speed if prev_speed > 0.0 else False
            if mean_time_jump or variance_jump or ic_overlap_index > 0.25 or mean_speed_drop or mean_interface_lifetime >= 0.75 * args.t_max:
                soft_subclass = "R2d_precritical_delay_band"
            elif std_time < 0.5 and ic_overlap_index == 0.0:
                soft_subclass = "R2r_rigid_runaway"
            else:
                soft_subclass = "R2s_structured_runaway"

        previous = previous_by_kappa.get(kappa)
        candidate_boundary = behavior_class != "R2_global_exclusion_runaway"
        if previous is not None and behavior_class == "R2_global_exclusion_runaway":
            prev_std = float(previous["std_time_to_exclusion"])
            prev_speed = float(previous["mean_late_time_front_speed"])
            candidate_boundary = (
                std_time >= 2.0 * prev_std if prev_std > 0.0 else False
            ) or (
                ic_overlap_index > 0.25
            ) or (
                mean_speed <= 0.5 * prev_speed if prev_speed > 0.0 else False
            )

        parameter_row = {
            "D_eps": d_eps,
            "D_rho": d_rho,
            "kappa": kappa,
            "lambda": lam,
            "n_runs": str(len(rows)),
            "collapse_fraction": f"{collapse_fraction:.6f}",
            "mean_time_to_exclusion": f"{mean_time:.6f}",
            "std_time_to_exclusion": f"{std_time:.6f}",
            "max_time_to_exclusion": f"{max_time:.6f}",
            "mean_final_exclusion_fraction": f"{mean_final_excl:.6f}",
            "mean_final_mean_rho": f"{mean_final_rho:.6f}",
            "mean_final_mean_R": f"{mean_final_r:.6f}",
            "mean_final_mean_eps": f"{mean_final_eps:.6f}",
            "mean_late_time_front_speed": f"{mean_speed:.6f}",
            "mean_interface_lifetime": f"{mean_interface_lifetime:.6f}",
            "IC_overlap_index": f"{ic_overlap_index:.6f}",
            "behavior_class": behavior_class,
            "soft_subclass": soft_subclass,
            "candidate_boundary_bool": str(candidate_boundary),
        }
        parameter_rows.append(parameter_row)
        by_kappa[kappa].append(parameter_row)
        previous_by_kappa[kappa] = parameter_row

    parameter_fields = [
        "D_eps", "D_rho", "kappa", "lambda", "n_runs", "collapse_fraction", "mean_time_to_exclusion",
        "std_time_to_exclusion", "max_time_to_exclusion", "mean_final_exclusion_fraction", "mean_final_mean_rho",
        "mean_final_mean_R", "mean_final_mean_eps", "mean_late_time_front_speed", "mean_interface_lifetime",
        "IC_overlap_index", "behavior_class", "soft_subclass", "candidate_boundary_bool",
    ]
    write_csv(root / "parameter_summary.csv", parameter_rows, parameter_fields)

    boundary_rows: list[dict[str, str]] = []
    for kappa, rows in sorted(by_kappa.items(), key=lambda item: float(item[0])):
        runaway = [float(row["lambda"]) for row in rows if row["behavior_class"] == "R2_global_exclusion_runaway"]
        persistent = [float(row["lambda"]) for row in rows if row["behavior_class"] in {"R1_bounded_persistence", "R1m_mixed_regime"}]
        candidate_rows = [row for row in rows if row["candidate_boundary_bool"] == "True"]

        lambda_runaway_upper = max(runaway) if runaway else None
        lambda_persistent_lower = min(persistent) if persistent else None
        bracket_width = None if lambda_runaway_upper is None or lambda_persistent_lower is None else max(0.0, lambda_runaway_upper - lambda_persistent_lower)
        best_estimate = None if bracket_width is None else 0.5 * (lambda_runaway_upper + lambda_persistent_lower)
        variance_peak = max(float(row["std_time_to_exclusion"]) for row in rows) if rows else 0.0
        overlap_candidates = [float(row["lambda"]) for row in rows if float(row["IC_overlap_index"]) > 0.25]

        boundary_rows.append(
            {
                "D_eps": rows[0]["D_eps"],
                "D_rho": rows[0]["D_rho"],
                "kappa": kappa,
                "lambda_runaway_upper": "" if lambda_runaway_upper is None else f"{lambda_runaway_upper:.6f}",
                "lambda_persistent_lower": "" if lambda_persistent_lower is None else f"{lambda_persistent_lower:.6f}",
                "critical_bracket_width": "" if bracket_width is None else f"{bracket_width:.6f}",
                "best_estimate_lambda_c": "" if best_estimate is None else f"{best_estimate:.6f}",
                "behavior_below_boundary": "R2_global_exclusion_runaway" if lambda_runaway_upper is not None else "",
                "behavior_above_boundary": "" if lambda_persistent_lower is None else "R1/R1m_candidate",
                "collapse_time_gradient_peak": "",
                "collapse_time_variance_peak": f"{variance_peak:.6f}",
                "IC_overlap_onset_lambda": "" if not overlap_candidates else f"{min(overlap_candidates):.6f}",
                "tier2_validated": "False",
                "notes": "No hard crossing detected in this coarse slice." if lambda_persistent_lower is None else "Hard crossing candidate detected.",
            }
        )

    boundary_fields = [
        "D_eps", "D_rho", "kappa", "lambda_runaway_upper", "lambda_persistent_lower", "critical_bracket_width",
        "best_estimate_lambda_c", "behavior_below_boundary", "behavior_above_boundary",
        "collapse_time_gradient_peak", "collapse_time_variance_peak", "IC_overlap_onset_lambda",
        "tier2_validated", "notes",
    ]
    write_csv(root / "boundary_table.csv", boundary_rows, boundary_fields)

    manifest = {
        "simulation_spec_version": "surface_map_v1",
        "batch_id": args.batch_id,
        "phase": args.phase,
        "name": args.phase_name,
        "engine_name": native_backend_name(),
        "metric_version": "current_level2_metrics",
        "grid_size": args.grid_size,
        "T_max": args.t_max,
        "kappa_values": [float(value) for value in args.kappa_values],
        "lambda_values": [float(value) for value in args.lambda_values],
        "replicates_per_ic": 3,
        "initial_condition_families": ["IC0", "IC1", "IC2"],
        "seed_mode": "explicit_seeds",
        "seeds": [int(value) for value in args.seed_list],
        "code_version": None,
        "git_hash": None,
        "compile_flags_if_available": {"native_max_threads": native_backend_max_threads()},
        "notes": args.notes,
    }
    (root / "surface_map_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    phase_report = {
        "phase": args.phase,
        "status": "completed",
        "n_parameter_points": len(parameter_rows),
        "n_runs": len(run_results),
        "all_runaway": all(row["behavior_class"] == "R2_global_exclusion_runaway" for row in parameter_rows),
        "candidate_boundary_points": [
            {"kappa": row["kappa"], "lambda": row["lambda"], "soft_subclass": row["soft_subclass"]}
            for row in parameter_rows
            if row["candidate_boundary_bool"] == "True"
        ],
        "next_phase_ready": True,
        "recommended_next_action": args.recommended_next_action,
    }
    (root / "phase_report.json").write_text(json.dumps(phase_report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
