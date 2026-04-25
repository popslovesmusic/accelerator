from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

try:
    from software.src.dsr_local_classifier import classify_dsr_metrics, compute_dsr_metrics, summarize_dsr_late_tail
except ModuleNotFoundError:
    from dsr_local_classifier import classify_dsr_metrics, compute_dsr_metrics, summarize_dsr_late_tail


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


PROFILE_TIME_PATTERN = re.compile(r"_t_([0-9]+p[0-9]+)\.csv$")


def profile_time_value(path: Path) -> float:
    match = PROFILE_TIME_PATTERN.search(path.name)
    if match is None:
        return -1.0
    return float(match.group(1).replace("p", "."))


def relational_profiles(output_root: Path, run_id: str) -> List[Path]:
    profile_dir = output_root / "profiles_relational"
    return sorted(profile_dir.glob(f"profile_relational_{run_id}_t_*.csv"), key=profile_time_value)


def summarize_runs(rows: Sequence[Dict[str, object]]) -> Dict[str, float]:
    if not rows:
        return {}
    numeric_fields = (
        "delta_floor_ratio",
        "excess_floor_ratio",
        "delta_floor_correlation",
        "sigma_floor_ratio",
        "rho_floor_ratio",
        "late_window",
        "tail_floor_locked_fraction",
        "tail_bounded_support_fraction",
        "tail_max_excess_floor_ratio",
        "tail_min_delta_floor_correlation",
        "sigma_l2",
        "rho_l2",
        "depth_l2",
        "floor_active_fraction",
        "sign_match_fraction",
        "ratchet_event_steps",
        "seed_update_steps",
    )
    summary: Dict[str, float] = {"run_count": float(len(rows))}
    for field in numeric_fields:
        values = [float(row[field]) for row in rows]
        summary[f"mean_{field}"] = float(np.mean(values))
        summary[f"min_{field}"] = float(np.min(values))
        summary[f"max_{field}"] = float(np.max(values))
    return summary


def render_markdown(output_root: Path, rows: Sequence[Dict[str, object]], summary: Dict[str, float]) -> str:
    lines = [
        "# DSR Local Diagnostics",
        "",
        f"Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        f"Output root: `{output_root}`",
        "",
        "This note reads the final relational profiles directly and reports DSR-local metrics without relying on the legacy `(epsilon, rho, R)` classifier.",
        "",
    ]
    if summary:
        lines.extend(
            [
                "## Summary",
                "",
                f"- `run_count = {int(summary['run_count'])}`",
                f"- `mean_delta_floor_ratio = {summary['mean_delta_floor_ratio']:.6f}`",
                f"- `mean_excess_floor_ratio = {summary['mean_excess_floor_ratio']:.6f}`",
                f"- `mean_delta_floor_correlation = {summary['mean_delta_floor_correlation']:.6f}`",
                f"- `mean_sigma_floor_ratio = {summary['mean_sigma_floor_ratio']:.6f}`",
                f"- `mean_rho_floor_ratio = {summary['mean_rho_floor_ratio']:.6f}`",
                f"- `mean_late_window = {summary['mean_late_window']:.6f}`",
                f"- `mean_tail_floor_locked_fraction = {summary['mean_tail_floor_locked_fraction']:.6f}`",
                f"- `mean_tail_bounded_support_fraction = {summary['mean_tail_bounded_support_fraction']:.6f}`",
                f"- `mean_sign_match_fraction = {summary['mean_sign_match_fraction']:.6f}`",
                f"- `mean_ratchet_event_steps = {summary['mean_ratchet_event_steps']:.6f}`",
                f"- `mean_seed_update_steps = {summary['mean_seed_update_steps']:.6f}`",
                "",
            ]
        )
    lines.extend(["## Runs", ""])
    for row in rows:
        lines.append(
            f"- `{row['run_id']}` (`{row['ic_type']}`): "
            f"classifier=`{row['classification']}`, dsr_label=`{row['dsr_local_label']}`, profile_time=`{float(row['profile_time']):.1f}`, delta/floor=`{float(row['delta_floor_ratio']):.6f}`, "
            f"excess/floor=`{float(row['excess_floor_ratio']):.6f}`, corr=`{float(row['delta_floor_correlation']):.6f}`, "
            f"sign_match=`{float(row['sign_match_fraction']):.6f}`, sigma/floor=`{float(row['sigma_floor_ratio']):.6f}`, "
            f"rho/floor=`{float(row['rho_floor_ratio']):.6f}`, late_window=`{float(row['late_window']):.1f}`, "
            f"tail_locked=`{float(row['tail_floor_locked_fraction']):.3f}`, tail_bounded=`{float(row['tail_bounded_support_fraction']):.3f}`, "
            f"events=`{int(row['ratchet_event_steps'])}`, seed_updates=`{int(row['seed_update_steps'])}`"
        )
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "A DSR run should be judged first by floor adherence, relational-shape agreement, and event-gated stability. Legacy classification remains useful as a compatibility warning, but not as the governing local interpretation signal for this branch.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report DSR-local metrics from relational profile outputs.")
    parser.add_argument("--output-root", required=True, help="Batch output root containing run_manifest.csv and profiles_relational/.")
    parser.add_argument("--csv-output", required=True, help="Destination CSV path for per-run DSR-local metrics.")
    parser.add_argument("--json-output", required=True, help="Destination JSON path for the DSR-local payload.")
    parser.add_argument("--md-output", required=True, help="Destination Markdown note path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    manifest_rows = read_csv(output_root / "run_manifest.csv")
    summary_rows = {row["run_id"]: row for row in read_csv(output_root / "final_summary.csv")}

    report_rows: List[Dict[str, object]] = []
    for manifest_row in manifest_rows:
        run_id = str(manifest_row["run_id"])
        profile_paths = relational_profiles(output_root, run_id)
        if not profile_paths:
            continue
        profile_path = profile_paths[-1]
        profile_rows = read_csv(profile_path)
        summary_row = summary_rows.get(run_id, {})
        metrics_history: List[Dict[str, float]] = []
        profile_times: List[float] = []
        for candidate_path in profile_paths:
            candidate_rows = read_csv(candidate_path)
            metrics_history.append(
                compute_dsr_metrics(
                    delta=[float(row["delta"]) for row in candidate_rows],
                    sigma=[float(row["sigma"]) for row in candidate_rows],
                    rho=[float(row["rho"]) for row in candidate_rows],
                    depth=[float(row["depth"]) for row in candidate_rows],
                    delta_floor=[float(row["delta_floor"]) for row in candidate_rows],
                )
            )
            profile_times.append(profile_time_value(candidate_path))
        metrics = compute_dsr_metrics(
            delta=[float(row["delta"]) for row in profile_rows],
            sigma=[float(row["sigma"]) for row in profile_rows],
            rho=[float(row["rho"]) for row in profile_rows],
            depth=[float(row["depth"]) for row in profile_rows],
            delta_floor=[float(row["delta_floor"]) for row in profile_rows],
        )
        late_tail_summary = summarize_dsr_late_tail(
            profile_times,
            metrics_history,
            min_tail_count=5,
        )
        dsr_classification = classify_dsr_metrics(
            metrics,
            ratchet_event_steps=int(manifest_row.get("ratchet_event_steps", 0) or 0),
            seed_update_steps=int(manifest_row.get("seed_update_steps", 0) or 0),
            late_tail_summary=late_tail_summary,
        )
        report_rows.append(
            {
                "run_id": run_id,
                "sim_id": manifest_row.get("sim_id", ""),
                "batch_id": manifest_row.get("batch_id", ""),
                "ic_type": manifest_row.get("IC_type", manifest_row.get("ic_type", "")),
                "phase_expression": manifest_row.get("phase_expression", ""),
                "delta_family": manifest_row.get("delta_family", ""),
                "classification": summary_row.get("classification", manifest_row.get("classification", "")),
                "dsr_local_label": dsr_classification["label"],
                "dsr_branch_converged": str(dsr_classification["converged"]).lower(),
                "ratchet_event_steps": int(manifest_row.get("ratchet_event_steps", 0) or 0),
                "seed_update_steps": int(manifest_row.get("seed_update_steps", 0) or 0),
                "profile_time": profile_time_value(profile_path),
                "late_window": late_tail_summary["late_window"],
                "tail_floor_locked_fraction": late_tail_summary["floor_locked_fraction"],
                "tail_bounded_support_fraction": late_tail_summary["bounded_support_fraction"],
                "tail_max_excess_floor_ratio": late_tail_summary["max_excess_floor_ratio"],
                "tail_min_delta_floor_correlation": late_tail_summary["min_delta_floor_correlation"],
                "profile_path": str(profile_path),
                **metrics,
            }
        )

    report_rows.sort(key=lambda row: str(row["run_id"]))
    summary = summarize_runs(report_rows)
    write_csv(
        Path(args.csv_output).resolve(),
        report_rows,
        [
            "run_id",
            "sim_id",
            "batch_id",
            "ic_type",
            "phase_expression",
            "delta_family",
            "classification",
            "dsr_local_label",
            "dsr_branch_converged",
            "ratchet_event_steps",
            "seed_update_steps",
            "profile_time",
            "late_window",
            "tail_floor_locked_fraction",
            "tail_bounded_support_fraction",
            "tail_max_excess_floor_ratio",
            "tail_min_delta_floor_correlation",
            "point_count",
            "delta_l2",
            "sigma_l2",
            "rho_l2",
            "depth_l2",
            "delta_floor_l2",
            "excess_floor_l2",
            "delta_floor_ratio",
            "excess_floor_ratio",
            "delta_floor_correlation",
            "sigma_floor_ratio",
            "rho_floor_ratio",
            "sigma_rho_ratio",
            "depth_span",
            "floor_active_fraction",
            "sign_match_fraction",
            "mean_delta",
            "mean_sigma",
            "mean_rho",
            "mean_depth",
            "profile_path",
        ],
    )
    write_json(
        Path(args.json_output).resolve(),
        {"date": "2026-04-04", "output_root": str(output_root), "summary": summary, "runs": report_rows},
    )
    Path(args.md_output).resolve().write_text(render_markdown(output_root, report_rows, summary), encoding="utf-8")


if __name__ == "__main__":
    main()
