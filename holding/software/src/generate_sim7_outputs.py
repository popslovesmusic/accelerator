from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev


IC_MAP = {
    "front_seeded": "IC0",
    "near_uniform_noise": "IC1",
    "localized_seed": "IC2",
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate sim7 summary outputs from a completed P0/P1/P2/P3 batch.")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--kappa-values", nargs="+", required=True)
    parser.add_argument("--lambda-values", nargs="+", required=True)
    parser.add_argument("--grid-size", type=int, required=True)
    parser.add_argument("--t-max", type=float, required=True)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def first_time(series: list[dict[str, str]], predicate) -> float | None:
    for row in series:
        if predicate(row):
            return float(row["time"])
    return None


def plateau_mean(series: list[dict[str, str]], key: str) -> float:
    tail = series[-max(1, len(series) // 5):]
    return mean(float(row[key]) for row in tail)


def classify_run(summary: dict[str, str]) -> tuple[str, str]:
    final_exclusion = float(summary["final_exclusion_fraction"])
    final_rho = float(summary["final_mean_rho"])
    final_interfaces = int(float(summary["final_interface_count"]))
    if final_exclusion >= 0.95 and final_rho <= 0.05 and final_interfaces == 0:
        return "runaway", "rejected_as_runaway_side"
    if final_exclusion <= 0.05 and abs(final_rho - 2.3333333333) <= 0.15 and final_interfaces == 0:
        return "SS2", "rejected_as_transient_to_SS2"
    if 0.05 < final_exclusion < 0.95 and final_rho > 0.25 and final_interfaces >= 1:
        return "candidate_SS3", "promote_to_SS3_candidate"
    return "intermediate", "needs_followup"


def main() -> None:
    args = parse_args()
    root = Path(args.output_root).resolve()

    run_manifest = read_csv_rows(root / "run_manifest.csv")
    final_summary = {row["run_id"]: row for row in read_csv_rows(root / "final_summary.csv")}
    timeseries_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    domain_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    front_by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(root / "timeseries_global.csv"):
        timeseries_by_run[row["run_id"]].append(row)
    for row in read_csv_rows(root / "domain_metrics.csv"):
        domain_by_run[row["run_id"]].append(row)
    for row in read_csv_rows(root / "front_metrics.csv"):
        front_by_run[row["run_id"]].append(row)

    run_rows: list[dict[str, str]] = []
    class_rows: list[dict[str, str]] = []
    point_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)

    for manifest in run_manifest:
        run_id = manifest["run_id"]
        summary = final_summary[run_id]
        series = timeseries_by_run[run_id]
        domains = domain_by_run[run_id]
        fronts = front_by_run[run_id]
        run_class, decision = classify_run(summary)
        interface_loss_time = first_time(series, lambda row: int(float(row["interface_count"])) == 0)
        full_exclusion_time = first_time(series, lambda row: float(row["exclusion_fraction"]) >= 0.95)
        mixed_state_duration = sum(
            1 for row in series
            if 0.05 < float(row["exclusion_fraction"]) < 0.95
            and float(row["mean_rho"]) > 0.25
            and int(float(row["interface_count"])) >= 1
        )
        mixed_state_fraction = mixed_state_duration / max(1, len(series))
        late_fronts = fronts[-max(1, len(fronts) // 3):]
        front_position_stability = pstdev([float(row["front_position"]) for row in late_fronts]) if len(late_fronts) > 1 else 0.0
        front_width_stability = pstdev([float(row["front_width"]) for row in late_fronts]) if len(late_fronts) > 1 else 0.0

        run_row = {
            "run_id": run_id,
            "D_eps": manifest["D_eps"],
            "D_rho": manifest["D_rho"],
            "kappa": manifest["kappa"],
            "lambda": manifest["lam"],
            "IC_family": IC_MAP.get(manifest["ic_type"], manifest["ic_type"]),
            "seed": manifest["seed"],
            "T_max": manifest["t_final"],
            "run_class": run_class,
            "decision_tag": decision,
            "final_exclusion_fraction": summary["final_exclusion_fraction"],
            "final_mean_eps": summary["final_mean_eps"],
            "final_mean_rho": summary["final_mean_rho"],
            "final_mean_R": summary["final_mean_R"],
            "final_interface_count": summary["final_interface_count"],
            "interface_lifetime": "" if interface_loss_time is None else f"{interface_loss_time:.6f}",
            "time_to_interface_loss": "" if interface_loss_time is None else f"{interface_loss_time:.6f}",
            "time_to_full_exclusion": "" if full_exclusion_time is None else f"{full_exclusion_time:.6f}",
            "max_interface_count": str(max(int(float(row["interface_count"])) for row in series)),
            "rho_plateau_value": f"{plateau_mean(series, 'mean_rho'):.6f}",
            "eps_plateau_value": f"{plateau_mean(series, 'mean_eps'):.6f}",
            "R_plateau_value": f"{plateau_mean(series, 'mean_R'):.6f}",
            "mixed_state_duration_fraction": f"{mixed_state_fraction:.6f}",
            "front_position_stability": f"{front_position_stability:.6f}",
            "front_width_stability": f"{front_width_stability:.6f}",
            "rho_exclusion_coexistence_duration": f"{mixed_state_fraction * float(manifest['t_final']):.6f}",
            "drift_to_SS2_time_if_present": "" if run_class != "SS2" else ("" if interface_loss_time is None else f"{interface_loss_time:.6f}"),
            "source_classification": summary["classification"],
        }
        run_rows.append(run_row)
        point_groups[(manifest["D_eps"], manifest["D_rho"], manifest["kappa"], manifest["lam"])].append(run_row)
        class_rows.append(
            {
                "run_id": run_id,
                "IC_family": run_row["IC_family"],
                "seed": run_row["seed"],
                "kappa": run_row["kappa"],
                "lambda": run_row["lambda"],
                "run_class": run_class,
                "decision_tag": decision,
                "final_exclusion_fraction": run_row["final_exclusion_fraction"],
                "final_mean_rho": run_row["final_mean_rho"],
                "final_interface_count": run_row["final_interface_count"],
            }
        )

    write_csv(root / "sim7_run_results.csv", run_rows, list(run_rows[0].keys()) if run_rows else [])
    write_csv(root / "sim7_classification_summary.csv", class_rows, list(class_rows[0].keys()) if class_rows else [])
    write_csv(root / "sim7_timeseries_global.csv", read_csv_rows(root / "timeseries_global.csv"), list(read_csv_rows(root / "timeseries_global.csv")[0].keys()) if read_csv_rows(root / "timeseries_global.csv") else [])
    write_csv(root / "sim7_front_metrics.csv", read_csv_rows(root / "front_metrics.csv"), list(read_csv_rows(root / "front_metrics.csv")[0].keys()) if read_csv_rows(root / "front_metrics.csv") else [])
    write_csv(root / "sim7_domain_metrics.csv", read_csv_rows(root / "domain_metrics.csv"), list(read_csv_rows(root / "domain_metrics.csv")[0].keys()) if read_csv_rows(root / "domain_metrics.csv") else [])

    parameter_rows: list[dict[str, str]] = []
    regime_rows: list[dict[str, str]] = []
    candidate_rows: list[dict[str, str]] = []
    for key in sorted(point_groups, key=lambda item: tuple(float(value) for value in item)):
        d_eps, d_rho, kappa, lam = key
        rows = point_groups[key]
        counts = Counter(row["run_class"] for row in rows)
        collapse_times = [float(row["time_to_full_exclusion"]) for row in rows if row["time_to_full_exclusion"]]
        ic_overlap_index = 1.0 if counts.get("candidate_SS3", 0) > 0 and len({row["IC_family"] for row in rows if row["run_class"] == "candidate_SS3"}) > 1 else 0.0
        point_class = "candidate_SS3" if counts.get("candidate_SS3", 0) > 0 else ("SS2" if counts.get("SS2", 0) == len(rows) else "runaway")
        row = {
            "D_eps": d_eps,
            "D_rho": d_rho,
            "kappa": kappa,
            "lambda": lam,
            "n_runs": str(len(rows)),
            "runaway_count": str(counts.get("runaway", 0)),
            "SS2_count": str(counts.get("SS2", 0)),
            "candidate_SS3_count": str(counts.get("candidate_SS3", 0)),
            "intermediate_count": str(counts.get("intermediate", 0)),
            "point_class": point_class,
            "mean_final_exclusion_fraction": f"{mean(float(r['final_exclusion_fraction']) for r in rows):.6f}",
            "mean_final_mean_rho": f"{mean(float(r['final_mean_rho']) for r in rows):.6f}",
            "mean_final_interface_count": f"{mean(float(r['final_interface_count']) for r in rows):.6f}",
            "mean_interface_lifetime": f"{mean(float(r['interface_lifetime']) for r in rows if r['interface_lifetime']) if any(r['interface_lifetime'] for r in rows) else 0.0:.6f}",
            "variance_of_collapse_time_by_parameter": f"{pstdev(collapse_times) if len(collapse_times) > 1 else 0.0:.6f}",
            "IC_overlap_index": f"{ic_overlap_index:.6f}",
            "mixed_state_duration_fraction": f"{mean(float(r['mixed_state_duration_fraction']) for r in rows):.6f}",
        }
        parameter_rows.append(row)
        regime_rows.append(
            {
                "kappa": kappa,
                "lambda": lam,
                "dominant_regime_class": counts.most_common(1)[0][0],
                "run_count": str(len(rows)),
            }
        )
        if counts.get("candidate_SS3", 0) > 0:
            candidate_rows.append(row)

    write_csv(root / "sim7_parameter_summary.csv", parameter_rows, list(parameter_rows[0].keys()) if parameter_rows else [])
    write_csv(root / "sim7_regime_map.csv", regime_rows, list(regime_rows[0].keys()) if regime_rows else [])

    bridge_rows = []
    grouped_by_kappa: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in parameter_rows:
        grouped_by_kappa[row["kappa"]].append(row)
    for kappa, rows in sorted(grouped_by_kappa.items(), key=lambda item: float(item[0])):
        runaway_lams = [float(r["lambda"]) for r in rows if r["point_class"] == "runaway"]
        ss2_lams = [float(r["lambda"]) for r in rows if r["point_class"] == "SS2"]
        ss3_lams = [float(r["lambda"]) for r in rows if r["point_class"] == "candidate_SS3"]
        bridge_rows.append(
            {
                "kappa": kappa,
                "runaway_lambda_max": "" if not runaway_lams else f"{max(runaway_lams):.6f}",
                "candidate_SS3_lambda_min": "" if not ss3_lams else f"{min(ss3_lams):.6f}",
                "candidate_SS3_lambda_max": "" if not ss3_lams else f"{max(ss3_lams):.6f}",
                "SS2_lambda_min": "" if not ss2_lams else f"{min(ss2_lams):.6f}",
                "transition_detected": str(bool(ss3_lams or ss2_lams)),
            }
        )
    write_csv(root / "sim7_bridge_table.csv", bridge_rows, list(bridge_rows[0].keys()) if bridge_rows else [])

    report = {
        "batch_id": args.batch_id,
        "phase": args.phase,
        "grid_size": args.grid_size,
        "T_max": args.t_max,
        "kappa_values": [float(v) for v in args.kappa_values],
        "lambda_values": [float(v) for v in args.lambda_values],
        "n_parameter_points": len(parameter_rows),
        "n_runs": len(run_rows),
        "candidate_points": [
            {"kappa": row["kappa"], "lambda": row["lambda"], "candidate_SS3_count": row["candidate_SS3_count"]}
            for row in candidate_rows
        ],
        "notes": args.notes,
    }
    (root / "sim7_phase_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    candidate_lines = [
        "# sim7 Candidate Report",
        "",
        f"Batch: {args.batch_id}",
        f"Phase: {args.phase}",
        "",
        f"Candidate points: {len(candidate_rows)}",
        "",
    ]
    for row in candidate_rows:
        candidate_lines.append(
            f"- kappa={row['kappa']} lambda={row['lambda']} candidate_SS3_count={row['candidate_SS3_count']} mean_final_exclusion_fraction={row['mean_final_exclusion_fraction']} mean_final_mean_rho={row['mean_final_mean_rho']} mean_final_interface_count={row['mean_final_interface_count']}"
        )
    (root / "sim7_candidate_report.md").write_text("\n".join(candidate_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
