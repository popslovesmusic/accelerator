from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sim6 bridge-scan summary outputs from a completed batch.")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--kappa-values", nargs="+", required=True)
    parser.add_argument("--lambda-values", nargs="+", required=True)
    parser.add_argument("--grid-size", type=int, required=True)
    parser.add_argument("--t-max", type=float, required=True)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def classify_run(summary: dict[str, str], domain_tail: dict[str, str]) -> tuple[str, bool]:
    final_exclusion = float(summary["final_exclusion_fraction"])
    final_rho = float(summary["final_mean_rho"])
    final_interfaces = int(float(summary["final_interface_count"]))
    late_active = float(domain_tail["active_fraction"])
    late_excluded_active = float(domain_tail["excluded_active_fraction"])

    is_candidate_ss3 = (
        0.0 < final_exclusion < 1.0
        and final_rho > 0.0
        and final_interfaces > 0
    )
    if is_candidate_ss3:
        return "candidate_SS3", True

    if final_exclusion <= 0.05 and final_rho > 0.0 and final_interfaces == 0:
        return "SS2", False

    if late_active > 0.0 and late_excluded_active < 1.0 and final_rho > 0.0 and final_interfaces > 0:
        return "candidate_SS3", True

    return "runaway", False


def first_time(series: list[dict[str, str]], predicate) -> float | None:
    for row in series:
        if predicate(row):
            return float(row["time"])
    return None


def main() -> None:
    args = parse_args()
    root = Path(args.output_root).resolve()

    run_manifest = read_csv_rows(root / "run_manifest.csv")
    final_summary = {row["run_id"]: row for row in read_csv_rows(root / "final_summary.csv")}
    timeseries_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    domain_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(root / "timeseries_global.csv"):
        timeseries_by_run[row["run_id"]].append(row)
    for row in read_csv_rows(root / "domain_metrics.csv"):
        domain_by_run[row["run_id"]].append(row)

    run_rows: list[dict[str, str]] = []
    point_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)

    for manifest in run_manifest:
        run_id = manifest["run_id"]
        summary = final_summary[run_id]
        series = timeseries_by_run[run_id]
        domains = domain_by_run[run_id]
        last_domain = domains[-1]
        run_class, candidate_flag = classify_run(summary, last_domain)

        exclusion_time = first_time(series, lambda row: float(row["exclusion_fraction"]) >= 1.0)
        interface_loss_time = first_time(series, lambda row: int(float(row["interface_count"])) == 0)
        mean_rho_tail = mean(float(row["mean_rho"]) for row in series[-max(1, len(series) // 5):])

        row = {
            "run_id": run_id,
            "D_eps": manifest["D_eps"],
            "D_rho": manifest["D_rho"],
            "kappa": manifest["kappa"],
            "lambda": manifest["lam"],
            "IC_family": manifest["ic_type"],
            "seed": manifest["seed"],
            "T_max": manifest["t_final"],
            "run_class": run_class,
            "candidate_SS3_bool": str(candidate_flag),
            "time_to_full_exclusion": "" if exclusion_time is None else f"{exclusion_time:.6f}",
            "interface_loss_time": "" if interface_loss_time is None else f"{interface_loss_time:.6f}",
            "final_exclusion_fraction": summary["final_exclusion_fraction"],
            "final_mean_rho": summary["final_mean_rho"],
            "final_mean_R": summary["final_mean_R"],
            "final_mean_eps": summary["final_mean_eps"],
            "final_interface_count": summary["final_interface_count"],
            "late_time_front_speed": summary["late_time_mean_front_speed"],
            "late_time_front_width": summary["late_time_mean_front_width"],
            "late_active_fraction": last_domain["active_fraction"],
            "late_excluded_active_fraction": last_domain["excluded_active_fraction"],
            "mean_rho_tail": f"{mean_rho_tail:.6f}",
            "source_classification": summary["classification"],
        }
        run_rows.append(row)
        point_groups[(manifest["D_eps"], manifest["D_rho"], manifest["kappa"], manifest["lam"])].append(row)

    run_fields = [
        "run_id", "D_eps", "D_rho", "kappa", "lambda", "IC_family", "seed", "T_max",
        "run_class", "candidate_SS3_bool", "time_to_full_exclusion", "interface_loss_time",
        "final_exclusion_fraction", "final_mean_rho", "final_mean_R", "final_mean_eps",
        "final_interface_count", "late_time_front_speed", "late_time_front_width",
        "late_active_fraction", "late_excluded_active_fraction", "mean_rho_tail",
        "source_classification",
    ]
    write_csv(root / "sim6_run_results.csv", run_rows, run_fields)

    parameter_rows: list[dict[str, str]] = []
    transition_rows: list[dict[str, str]] = []
    by_kappa: dict[str, list[dict[str, str]]] = defaultdict(list)

    for key in sorted(point_groups, key=lambda item: tuple(float(value) for value in item)):
        d_eps, d_rho, kappa, lam = key
        rows = point_groups[key]
        counts = Counter(row["run_class"] for row in rows)
        collapse_times = [
            float(row["time_to_full_exclusion"])
            for row in rows
            if row["time_to_full_exclusion"] != ""
        ]
        interface_times = [
            float(row["interface_loss_time"])
            for row in rows
            if row["interface_loss_time"] != ""
        ]

        any_candidate_ss3 = any(row["candidate_SS3_bool"] == "True" for row in rows)
        any_ss2 = any(row["run_class"] == "SS2" for row in rows)
        all_runaway = all(row["run_class"] == "runaway" for row in rows)

        if any_candidate_ss3:
            point_class = "candidate_SS3"
        elif any_ss2 and not all_runaway:
            point_class = "SS2"
        else:
            point_class = "runaway"

        parameter_row = {
            "D_eps": d_eps,
            "D_rho": d_rho,
            "kappa": kappa,
            "lambda": lam,
            "n_runs": str(len(rows)),
            "runaway_count": str(counts.get("runaway", 0)),
            "SS2_count": str(counts.get("SS2", 0)),
            "candidate_SS3_count": str(counts.get("candidate_SS3", 0)),
            "point_class": point_class,
            "mean_time_to_full_exclusion": "" if not collapse_times else f"{mean(collapse_times):.6f}",
            "std_time_to_full_exclusion": "" if len(collapse_times) <= 1 else f"{pstdev(collapse_times):.6f}",
            "mean_interface_loss_time": "" if not interface_times else f"{mean(interface_times):.6f}",
            "mean_final_exclusion_fraction": f"{mean(float(row['final_exclusion_fraction']) for row in rows):.6f}",
            "mean_final_mean_rho": f"{mean(float(row['final_mean_rho']) for row in rows):.6f}",
            "mean_final_interface_count": f"{mean(float(row['final_interface_count']) for row in rows):.6f}",
            "mean_late_time_front_speed": f"{mean(float(row['late_time_front_speed']) for row in rows):.6f}",
            "mean_late_time_front_width": f"{mean(float(row['late_time_front_width']) for row in rows):.6f}",
            "mean_late_active_fraction": f"{mean(float(row['late_active_fraction']) for row in rows):.6f}",
            "mean_late_excluded_active_fraction": f"{mean(float(row['late_excluded_active_fraction']) for row in rows):.6f}",
        }
        parameter_rows.append(parameter_row)
        by_kappa[kappa].append(parameter_row)
        if point_class != "runaway":
            transition_rows.append(parameter_row)

    parameter_fields = [
        "D_eps", "D_rho", "kappa", "lambda", "n_runs", "runaway_count", "SS2_count",
        "candidate_SS3_count", "point_class", "mean_time_to_full_exclusion",
        "std_time_to_full_exclusion", "mean_interface_loss_time",
        "mean_final_exclusion_fraction", "mean_final_mean_rho", "mean_final_interface_count",
        "mean_late_time_front_speed", "mean_late_time_front_width",
        "mean_late_active_fraction", "mean_late_excluded_active_fraction",
    ]
    write_csv(root / "sim6_parameter_summary.csv", parameter_rows, parameter_fields)

    bridge_rows: list[dict[str, str]] = []
    for kappa, rows in sorted(by_kappa.items(), key=lambda item: float(item[0])):
        ss3_lams = [float(row["lambda"]) for row in rows if row["point_class"] == "candidate_SS3"]
        ss2_lams = [float(row["lambda"]) for row in rows if row["point_class"] == "SS2"]
        runaway_lams = [float(row["lambda"]) for row in rows if row["point_class"] == "runaway"]
        bridge_rows.append(
            {
                "D_eps": rows[0]["D_eps"],
                "D_rho": rows[0]["D_rho"],
                "kappa": kappa,
                "runaway_lambda_max": "" if not runaway_lams else f"{max(runaway_lams):.6f}",
                "SS2_lambda_min": "" if not ss2_lams else f"{min(ss2_lams):.6f}",
                "candidate_SS3_lambda_min": "" if not ss3_lams else f"{min(ss3_lams):.6f}",
                "candidate_SS3_lambda_max": "" if not ss3_lams else f"{max(ss3_lams):.6f}",
                "transition_detected": str(bool(ss2_lams or ss3_lams)),
            }
        )

    bridge_fields = [
        "D_eps", "D_rho", "kappa", "runaway_lambda_max", "SS2_lambda_min",
        "candidate_SS3_lambda_min", "candidate_SS3_lambda_max", "transition_detected",
    ]
    write_csv(root / "sim6_bridge_table.csv", bridge_rows, bridge_fields)

    report = {
        "batch_id": args.batch_id,
        "strategy": "bridge_scan",
        "grid_size": args.grid_size,
        "T_max": args.t_max,
        "kappa_values": [float(value) for value in args.kappa_values],
        "lambda_values": [float(value) for value in args.lambda_values],
        "n_parameter_points": len(parameter_rows),
        "n_runs": len(run_rows),
        "transition_points": [
            {"kappa": row["kappa"], "lambda": row["lambda"], "point_class": row["point_class"]}
            for row in transition_rows
        ],
        "notes": args.notes,
    }
    (root / "sim6_phase_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
