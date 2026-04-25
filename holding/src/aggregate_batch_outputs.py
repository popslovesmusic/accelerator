from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List


BASE_FILES = [
    "run_manifest.csv",
    "timeseries_global.csv",
    "domain_metrics.csv",
    "front_metrics.csv",
    "final_summary.csv",
]


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[Dict[str, str]], fieldnames: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_derived_outputs(output_root: Path, batch_id: str) -> None:
    run_manifest = read_csv_rows(output_root / "run_manifest.csv")
    final_summary = {row["run_id"]: row for row in read_csv_rows(output_root / "final_summary.csv")}

    domain_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(output_root / "domain_metrics.csv"):
        domain_rows[row["run_id"]].append(row)

    series_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in read_csv_rows(output_root / "timeseries_global.csv"):
        series_rows[row["run_id"]].append(row)

    classification_rows: List[Dict[str, str]] = []
    collapse_rows: List[Dict[str, str]] = []

    for manifest in run_manifest:
        run_id = manifest["run_id"]
        summary = final_summary[run_id]
        domains = domain_rows[run_id]
        series = series_rows[run_id]
        last_domain = domains[-1]
        final_interface_count = int(float(summary["final_interface_count"]))
        final_exclusion_fraction = float(summary["final_exclusion_fraction"])
        classification = summary["classification"]

        if classification == "runaway_or_unphysical" and final_interface_count == 0 and final_exclusion_fraction >= 0.95:
            regime_class = "R2_global_exclusion_takeover"
            termination_reason = "collapse_to_pressure"
        elif classification == "runaway_or_unphysical" and final_interface_count > 0:
            regime_class = "R3_delayed_front_collapse"
            termination_reason = "late_failure_without_persistent_interface"
        else:
            regime_class = "unmapped"
            termination_reason = classification

        classification_rows.append(
            {
                "run_id": run_id,
                "IC_type": manifest["ic_type"],
                "seed": manifest["seed"],
                "gamma": manifest["gamma"],
                "lam": manifest["lam"],
                "kappa": manifest["kappa"],
                "D_eps": manifest["D_eps"],
                "D_rho": manifest["D_rho"],
                "regime_class": regime_class,
                "classification_confidence": "provisional",
                "termination_reason": termination_reason,
                "late_active_fraction": last_domain["active_fraction"],
                "late_excluded_active_fraction": last_domain["excluded_active_fraction"],
                "late_front_width": summary["late_time_mean_front_width"],
                "late_front_velocity": summary["late_time_mean_front_speed"],
            }
        )

        interface_loss_time = None
        for row in series:
            if int(float(row["interface_count"])) == 0:
                interface_loss_time = float(row["time"])
                break
        if interface_loss_time is None and series:
            interface_loss_time = float(series[-1]["time"])

        collapse_rows.append(
            {
                "run_id": run_id,
                "batch_id": batch_id,
                "IC_type": manifest["ic_type"],
                "seed": manifest["seed"],
                "gamma": manifest["gamma"],
                "lam": manifest["lam"],
                "kappa": manifest["kappa"],
                "D_eps": manifest["D_eps"],
                "D_rho": manifest["D_rho"],
                "collapse_time": series[-1]["time"] if series else "",
                "interface_loss_time": f"{interface_loss_time:.6f}" if interface_loss_time is not None else "",
                "final_active_fraction": last_domain["active_fraction"],
                "final_excluded_active_fraction": last_domain["excluded_active_fraction"],
                "final_interface_count": summary["final_interface_count"],
            }
        )

    write_csv(
        output_root / "classification_summary.csv",
        classification_rows,
        [
            "run_id",
            "IC_type",
            "seed",
            "gamma",
            "lam",
            "kappa",
            "D_eps",
            "D_rho",
            "regime_class",
            "classification_confidence",
            "termination_reason",
            "late_active_fraction",
            "late_excluded_active_fraction",
            "late_front_width",
            "late_front_velocity",
        ],
    )

    write_csv(
        output_root / "collapse_time_scan.csv",
        collapse_rows,
        [
            "run_id",
            "batch_id",
            "IC_type",
            "seed",
            "gamma",
            "lam",
            "kappa",
            "D_eps",
            "D_rho",
            "collapse_time",
            "interface_loss_time",
            "final_active_fraction",
            "final_excluded_active_fraction",
            "final_interface_count",
        ],
    )

    regime_groups: Dict[tuple[str, str, str, str, str], List[str]] = defaultdict(list)
    for row in classification_rows:
        key = (row["gamma"], row["lam"], row["kappa"], row["D_eps"], row["D_rho"])
        regime_groups[key].append(row["regime_class"])

    regime_rows: List[Dict[str, str]] = []
    for key in sorted(regime_groups, key=lambda item: tuple(float(value) for value in item)):
        counts = Counter(regime_groups[key])
        gamma, lam, kappa, d_eps, d_rho = key
        regime_rows.append(
            {
                "gamma": gamma,
                "lam": lam,
                "kappa": kappa,
                "D_eps": d_eps,
                "D_rho": d_rho,
                "dominant_regime_class": counts.most_common(1)[0][0],
                "run_count": str(sum(counts.values())),
            }
        )

    write_csv(
        output_root / "regime_map.csv",
        regime_rows,
        ["gamma", "lam", "kappa", "D_eps", "D_rho", "dominant_regime_class", "run_count"],
    )


def aggregate_batches(output_root: Path, batch_dirs: List[Path]) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["profiles", "figures"]:
        (output_root / subdir).mkdir(exist_ok=True)

    for filename in BASE_FILES:
        combined_rows: List[Dict[str, str]] = []
        fieldnames: List[str] | None = None
        for batch_dir in batch_dirs:
            path = batch_dir / filename
            rows = read_csv_rows(path)
            if fieldnames is None:
                fieldnames = list(rows[0].keys()) if rows else []
            combined_rows.extend(rows)
        write_csv(output_root / filename, combined_rows, fieldnames or [])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate split batch outputs into one combined result set.")
    parser.add_argument("--output-root", required=True, help="Directory for the combined batch outputs.")
    parser.add_argument("--batch-id", required=True, help="Batch id to stamp into derived summary files.")
    parser.add_argument("--inputs", nargs="+", required=True, help="Input batch directories to aggregate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    batch_dirs = [Path(entry).resolve() for entry in args.inputs]
    aggregate_batches(output_root, batch_dirs)
    build_derived_outputs(output_root, args.batch_id)


if __name__ == "__main__":
    main()
