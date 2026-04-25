from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


PAIR_COLUMNS = [
    "seed",
    "IC_type",
    "kappa",
    "lam",
    "standard_run_id",
    "inverted_run_id",
    "standard_classification",
    "inverted_classification",
    "basin_identity_match",
    "regime_break",
    "onset_threshold_shift",
    "shelf_width_comparison",
    "pattern_morphology_similarity",
    "late_time_magnitude_ratio",
    "stability_time_shift",
    "delta_final_mean_eps",
    "delta_final_mean_rho",
    "delta_final_mean_R",
    "delta_final_exclusion_fraction",
    "delta_final_interface_count",
    "delta_late_time_mean_front_width",
    "delta_late_time_mean_sharpness",
    "delta_late_time_residue_asymmetry",
]


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve_outputs_root(path: Path) -> Path:
    candidate = path.resolve()
    if (candidate / "final_summary.csv").is_file() and (candidate / "timeseries_global.csv").is_file():
        return candidate
    outputs_candidate = candidate / "outputs"
    if (outputs_candidate / "final_summary.csv").is_file() and (outputs_candidate / "timeseries_global.csv").is_file():
        return outputs_candidate
    raise FileNotFoundError(f"Could not find both final_summary.csv and timeseries_global.csv under {candidate}")


def write_csv(path: Path, rows: Iterable[Dict[str, object]], columns: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def as_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def onset_time_for_run(timeseries_rows: List[Dict[str, str]], *, exclusion_threshold: float = 0.05) -> str:
    for row in timeseries_rows:
        exclusion_fraction = as_float(row.get("exclusion_fraction"))
        if exclusion_fraction >= exclusion_threshold:
            return f"{as_float(row.get('time')):.6f}"
    return ""


def pair_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        str(row.get("seed", "")),
        str(row.get("IC_type", row.get("ic_type", ""))),
        str(row.get("kappa", "")),
        str(row.get("lam", row.get("lambda", ""))),
    )


def morphology_similarity(standard_row: Dict[str, str], inverted_row: Dict[str, str]) -> float:
    comparison_fields = [
        "final_exclusion_fraction",
        "final_interface_count",
        "late_time_mean_front_width",
        "late_time_mean_sharpness",
        "late_time_residue_asymmetry",
    ]
    normalized_deltas: List[float] = []
    for field in comparison_fields:
        standard_value = as_float(standard_row.get(field))
        inverted_value = as_float(inverted_row.get(field))
        scale = max(1.0e-6, abs(standard_value), abs(inverted_value), 1.0)
        normalized_deltas.append(abs(inverted_value - standard_value) / scale)
    return 1.0 / (1.0 + (sum(normalized_deltas) / max(1, len(normalized_deltas))))


def late_time_magnitude_ratio(standard_row: Dict[str, str], inverted_row: Dict[str, str]) -> float:
    standard_norm = math.sqrt(
        as_float(standard_row.get("final_mean_eps")) ** 2
        + as_float(standard_row.get("final_mean_rho")) ** 2
        + as_float(standard_row.get("final_mean_R")) ** 2
    )
    inverted_norm = math.sqrt(
        as_float(inverted_row.get("final_mean_eps")) ** 2
        + as_float(inverted_row.get("final_mean_rho")) ** 2
        + as_float(inverted_row.get("final_mean_R")) ** 2
    )
    if standard_norm <= 1.0e-12:
        return 0.0 if inverted_norm <= 1.0e-12 else float("inf")
    return inverted_norm / standard_norm


def build_pair_rows(
    standard_summary_rows: List[Dict[str, str]],
    standard_timeseries_rows: List[Dict[str, str]],
    inverted_summary_rows: List[Dict[str, str]],
    inverted_timeseries_rows: List[Dict[str, str]],
) -> List[Dict[str, object]]:
    standard_summary_by_key = {pair_key(row): row for row in standard_summary_rows}
    inverted_summary_by_key = {pair_key(row): row for row in inverted_summary_rows}

    standard_timeseries_by_run: Dict[str, List[Dict[str, str]]] = {}
    for row in standard_timeseries_rows:
        standard_timeseries_by_run.setdefault(str(row.get("run_id", "")), []).append(row)

    inverted_timeseries_by_run: Dict[str, List[Dict[str, str]]] = {}
    for row in inverted_timeseries_rows:
        inverted_timeseries_by_run.setdefault(str(row.get("run_id", "")), []).append(row)

    pair_rows: List[Dict[str, object]] = []
    for key in sorted(set(standard_summary_by_key) & set(inverted_summary_by_key)):
        standard_row = standard_summary_by_key[key]
        inverted_row = inverted_summary_by_key[key]
        standard_run_id = str(standard_row.get("run_id", ""))
        inverted_run_id = str(inverted_row.get("run_id", ""))
        standard_classification = str(standard_row.get("regime_classification", standard_row.get("classification", "")))
        inverted_classification = str(inverted_row.get("regime_classification", inverted_row.get("classification", "")))
        basin_identity_match = standard_classification == inverted_classification
        regime_break = (
            not basin_identity_match
            or int(round(as_float(standard_row.get("final_interface_count"))))
            != int(round(as_float(inverted_row.get("final_interface_count"))))
        )

        standard_onset = onset_time_for_run(standard_timeseries_by_run.get(standard_run_id, []))
        inverted_onset = onset_time_for_run(inverted_timeseries_by_run.get(inverted_run_id, []))
        onset_shift = ""
        if standard_onset and inverted_onset:
            onset_shift = f"{as_float(inverted_onset) - as_float(standard_onset):.6f}"

        standard_stability_time = standard_row.get("stability_time", "")
        inverted_stability_time = inverted_row.get("stability_time", "")
        stability_time_shift = ""
        if standard_stability_time and inverted_stability_time:
            stability_time_shift = f"{as_float(inverted_stability_time) - as_float(standard_stability_time):.6f}"

        pair_rows.append(
            {
                "seed": key[0],
                "IC_type": key[1],
                "kappa": key[2],
                "lam": key[3],
                "standard_run_id": standard_run_id,
                "inverted_run_id": inverted_run_id,
                "standard_classification": standard_classification,
                "inverted_classification": inverted_classification,
                "basin_identity_match": str(basin_identity_match).lower(),
                "regime_break": str(regime_break).lower(),
                "onset_threshold_shift": onset_shift,
                "shelf_width_comparison": "",
                "pattern_morphology_similarity": f"{morphology_similarity(standard_row, inverted_row):.6f}",
                "late_time_magnitude_ratio": f"{late_time_magnitude_ratio(standard_row, inverted_row):.6f}",
                "stability_time_shift": stability_time_shift,
                "delta_final_mean_eps": f"{as_float(inverted_row.get('final_mean_eps')) - as_float(standard_row.get('final_mean_eps')):.6f}",
                "delta_final_mean_rho": f"{as_float(inverted_row.get('final_mean_rho')) - as_float(standard_row.get('final_mean_rho')):.6f}",
                "delta_final_mean_R": f"{as_float(inverted_row.get('final_mean_R')) - as_float(standard_row.get('final_mean_R')):.6f}",
                "delta_final_exclusion_fraction": f"{as_float(inverted_row.get('final_exclusion_fraction')) - as_float(standard_row.get('final_exclusion_fraction')):.6f}",
                "delta_final_interface_count": int(round(as_float(inverted_row.get("final_interface_count")) - as_float(standard_row.get("final_interface_count")))),
                "delta_late_time_mean_front_width": f"{as_float(inverted_row.get('late_time_mean_front_width')) - as_float(standard_row.get('late_time_mean_front_width')):.6f}",
                "delta_late_time_mean_sharpness": f"{as_float(inverted_row.get('late_time_mean_sharpness')) - as_float(standard_row.get('late_time_mean_sharpness')):.6f}",
                "delta_late_time_residue_asymmetry": f"{as_float(inverted_row.get('late_time_residue_asymmetry')) - as_float(standard_row.get('late_time_residue_asymmetry')):.6f}",
            }
        )
    return pair_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare standard and I_phi_inverted batch outputs and emit a paired delta report.")
    parser.add_argument("--standard-batch", required=True, help="Batch directory for the standard phase expression.")
    parser.add_argument("--inverted-batch", required=True, help="Batch directory for the I_phi_inverted phase expression.")
    parser.add_argument("--output", required=True, help="Destination CSV path for the paired delta report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    standard_batch = resolve_outputs_root(Path(args.standard_batch))
    inverted_batch = resolve_outputs_root(Path(args.inverted_batch))
    output_path = Path(args.output).resolve()

    standard_summary_rows = load_csv_rows(standard_batch / "final_summary.csv")
    standard_timeseries_rows = load_csv_rows(standard_batch / "timeseries_global.csv")
    inverted_summary_rows = load_csv_rows(inverted_batch / "final_summary.csv")
    inverted_timeseries_rows = load_csv_rows(inverted_batch / "timeseries_global.csv")

    pair_rows = build_pair_rows(
        standard_summary_rows,
        standard_timeseries_rows,
        inverted_summary_rows,
        inverted_timeseries_rows,
    )
    write_csv(output_path, pair_rows, PAIR_COLUMNS)
    print(f"Wrote {len(pair_rows)} paired rows to {output_path}")


if __name__ == "__main__":
    main()
