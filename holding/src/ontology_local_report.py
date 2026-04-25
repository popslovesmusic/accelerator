from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np


PROFILE_TIME_PATTERN = re.compile(r"_t_([0-9]+p[0-9]+)\.csv$")
RUN_IC_PATTERN = re.compile(r"_ic(\d+)$")


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[Dict[str, object]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def profile_time_value(path: Path) -> float:
    match = PROFILE_TIME_PATTERN.search(path.name)
    if match is None:
        return -1.0
    return float(match.group(1).replace("p", "."))


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_ic_index(run_id: str) -> int | None:
    match = RUN_IC_PATTERN.search(run_id)
    if match is None:
        return None
    return int(match.group(1))


def sorted_relational_profiles(output_root: Path, run_id: str) -> List[Path]:
    profile_dir = output_root / "profiles_relational"
    matches = list(profile_dir.glob(f"profile_relational_{run_id}_t_*.csv"))
    return sorted(matches, key=profile_time_value)


def gradient_neumann(field: np.ndarray, dx: float) -> np.ndarray:
    if field.size < 2:
        return np.zeros_like(field)
    gradient = (np.roll(field, -1) - np.roll(field, 1)) / (2.0 * dx)
    gradient[0] = (field[1] - field[0]) / dx
    gradient[-1] = (field[-1] - field[-2]) / dx
    return gradient


def l2_norm(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(array))))


def fit_tail_slope(times: Sequence[float], values: Sequence[float], tail_fraction: float = 0.2) -> float:
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


def classify_regime(
    peak_max_delta: float,
    final_max_delta: float,
    delta_phi_min: float,
    final_mean_C: float,
    final_mean_D: float,
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
        and final_mean_C >= 1.0e-4
        and final_mean_D >= 1.0e-4
        and late_time_slope >= -1.0e-5
    )
    if sustained_support:
        return "persistent"
    return "metastable"


def render_markdown(output_root: Path, rows: Sequence[Dict[str, object]]) -> str:
    lines = [
        "# Ontology Local Report",
        "",
        "Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        f"Output root: `{output_root}`",
        "",
        "This note evaluates the local `delta-C-D` ontology runtime with ontology-native regime logic rather than the legacy mapped-back classifier.",
        "",
        "## Runs",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['run_id']}`: A0=`{float(row['A0']):.2f}`, seed=`{row['seed']}`, regime=`{row['ontology_regime']}`, legacy=`{row['legacy_classification']}`, "
            f"profile_time=`{float(row['profile_time']):.1f}`, peak_delta=`{float(row['peak_max_delta']):.6f}`, "
            f"final_delta=`{float(row['final_max_delta']):.6f}`, delta_phi_min=`{float(row['delta_phi_min']):.6f}`, "
            f"peak_speed_ratio=`{float(row['peak_speed_ratio']):.6f}`, mean_C=`{float(row['final_mean_C']):.6f}`, "
            f"mean_D=`{float(row['final_mean_D']):.6f}`, kappa_proxy=`{float(row['kappa_proxy']):.0f}`, persistence_window=`{float(row['persistence_window']):.1f}`, late_time_slope=`{float(row['late_time_slope']):.6e}`"
        )
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "This report is the ontology-local interpretation layer for the new branch. It should be used to judge whether the `delta-C-D` runtime is behaving coherently before any comparison back to the legacy classifier or any governed staging decision.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize local ontology delta-C-D runs.")
    parser.add_argument("--output-root", required=True, help="Batch output root containing ontology-local run outputs.")
    parser.add_argument("--config", default=None, help="Optional config path used to recover IC metadata such as A0, width, and noise.")
    parser.add_argument("--csv-output", required=True, help="Destination CSV path.")
    parser.add_argument("--json-output", required=True, help="Destination JSON path.")
    parser.add_argument("--md-output", required=True, help="Destination Markdown path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    config_payload = load_json(Path(args.config).resolve()) if args.config else None
    manifest_rows = read_csv(output_root / "run_manifest.csv")
    summary_rows = {row["run_id"]: row for row in read_csv(output_root / "final_summary.csv")}

    report_rows: List[Dict[str, object]] = []
    for manifest_row in manifest_rows:
        run_id = str(manifest_row["run_id"])
        profile_paths = sorted_relational_profiles(output_root, run_id)
        if not profile_paths:
            continue

        peak_max_delta = 0.0
        peak_speed_ratio = 0.0
        persistence_start: float | None = None
        persistence_end: float | None = None
        previous_delta: np.ndarray | None = None
        previous_time: float | None = None
        profile_times: List[float] = []
        profile_peak_deltas: List[float] = []
        final_profile_rows: List[Dict[str, str]] = []
        final_profile_time = 0.0
        for profile_path in profile_paths:
            profile_rows = read_csv(profile_path)
            delta = np.asarray([float(row["delta"]) for row in profile_rows], dtype=float)
            constraint = np.asarray([float(row["C"]) for row in profile_rows], dtype=float)
            depth = np.asarray([float(row["D"]) for row in profile_rows], dtype=float)
            current_time = profile_time_value(profile_path)
            current_peak_delta = float(np.max(delta))
            peak_max_delta = max(peak_max_delta, float(np.max(delta)))
            profile_times.append(current_time)
            profile_peak_deltas.append(current_peak_delta)
            delta_phi_min_current = float(profile_rows[0].get("delta_phi_min", summary_rows.get(run_id, {}).get("ontology_delta_phi_min", 0.0)) or 0.0)
            if current_peak_delta >= delta_phi_min_current:
                if persistence_start is None:
                    persistence_start = current_time
                persistence_end = current_time
            if previous_delta is not None and previous_time is not None and delta.size > 1:
                dt = max(current_time - previous_time, 1.0e-12)
                dx = 200.0 / max(delta.size, 1)
                speed_proxy = np.abs((delta - previous_delta) / dt) / (np.abs(gradient_neumann(delta, dx)) + max(float(manifest_row.get("ont_eps_speed", 1.0e-6) or 1.0e-6), 1.0e-12))
                peak_speed_ratio = max(
                    peak_speed_ratio,
                    float(np.max(speed_proxy)) / max(float(manifest_row.get("ont_c_flat", 1.0) or 1.0), 1.0e-12),
                )
            previous_delta = delta
            previous_time = current_time
            final_profile_rows = profile_rows
            final_profile_time = current_time

        final_delta = np.asarray([float(row["delta"]) for row in final_profile_rows], dtype=float)
        final_constraint = np.asarray([float(row["C"]) for row in final_profile_rows], dtype=float)
        final_depth = np.asarray([float(row["D"]) for row in final_profile_rows], dtype=float)
        delta_phi_min = float(final_profile_rows[0].get("delta_phi_min", summary_rows.get(run_id, {}).get("ontology_delta_phi_min", 0.0)) or 0.0)
        kappa_proxy = float(final_profile_rows[0].get("kappa_proxy", summary_rows.get(run_id, {}).get("ontology_kappa_proxy", 0.0)) or 0.0)
        final_max_delta = float(np.max(final_delta)) if final_delta.size else 0.0
        final_mean_C = float(np.mean(final_constraint)) if final_constraint.size else 0.0
        final_mean_D = float(np.mean(final_depth)) if final_depth.size else 0.0
        persistence_window = 0.0
        if persistence_start is not None and persistence_end is not None:
            persistence_window = max(0.0, persistence_end - persistence_start)
        late_time_slope = fit_tail_slope(profile_times, profile_peak_deltas)
        residue_written = (kappa_proxy >= 1.0) or (final_mean_D > 1.0e-5)
        regime = classify_regime(
            peak_max_delta=peak_max_delta,
            final_max_delta=final_max_delta,
            delta_phi_min=delta_phi_min,
            final_mean_C=final_mean_C,
            final_mean_D=final_mean_D,
            residue_written=residue_written,
            persistence_window=persistence_window,
            late_time_slope=late_time_slope,
        )
        ic_metadata: Dict[str, object] = {}
        ic_index = run_ic_index(run_id)
        if config_payload is not None and ic_index is not None:
            initial_conditions = list(config_payload.get("initial_conditions", []))
            if 0 <= ic_index < len(initial_conditions):
                ic_spec = initial_conditions[ic_index]
                ic_metadata = {
                    "A0": float(ic_spec.get("A0", np.nan)),
                    "width": float(ic_spec.get("sigma0", np.nan)),
                    "noise": float(ic_spec.get("noise", np.nan)),
                }
        report_rows.append(
            {
                "run_id": run_id,
                "sim_id": manifest_row.get("sim_id", ""),
                "batch_id": manifest_row.get("batch_id", ""),
                "seed": int(manifest_row.get("seed", 0) or 0),
                "phase_expression": manifest_row.get("phase_expression", ""),
                "legacy_classification": summary_rows.get(run_id, {}).get("classification", manifest_row.get("classification", "")),
                "profile_time": final_profile_time,
                "peak_max_delta": peak_max_delta,
                "final_max_delta": final_max_delta,
                "delta_phi_min": delta_phi_min,
                "final_mean_C": final_mean_C,
                "final_mean_D": final_mean_D,
                "peak_speed_ratio": peak_speed_ratio,
                "kappa_proxy": kappa_proxy,
                "residue_written": str(residue_written).lower(),
                "persistence_window": persistence_window,
                "late_time_slope": late_time_slope,
                "final_C_l2": l2_norm(final_constraint),
                "final_D_l2": l2_norm(final_depth),
                "ontology_local_label": regime,
                "broad_summary_label": summary_rows.get(run_id, {}).get("classification", manifest_row.get("classification", "")),
                "ontology_regime": regime,
                "notes": f"{regime}_via_ontology_local_report",
                **ic_metadata,
            }
        )

    report_rows.sort(key=lambda row: str(row["run_id"]))
    write_csv(
        Path(args.csv_output).resolve(),
        report_rows,
        [
            "run_id",
            "sim_id",
            "batch_id",
            "seed",
            "A0",
            "width",
            "noise",
            "phase_expression",
            "ontology_local_label",
            "broad_summary_label",
            "ontology_regime",
            "legacy_classification",
            "profile_time",
            "peak_max_delta",
            "final_max_delta",
            "delta_phi_min",
            "final_mean_C",
            "final_mean_D",
            "residue_written",
            "persistence_window",
            "late_time_slope",
            "peak_speed_ratio",
            "kappa_proxy",
            "final_C_l2",
            "final_D_l2",
            "notes",
        ],
    )
    write_json(Path(args.json_output).resolve(), {"date": "2026-04-04", "output_root": str(output_root), "runs": report_rows})
    Path(args.md_output).resolve().write_text(render_markdown(output_root, report_rows), encoding="utf-8")


if __name__ == "__main__":
    main()
