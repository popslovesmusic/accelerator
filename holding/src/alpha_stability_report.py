from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


PROFILE_PATTERN = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p\-]+)\.csv$")


def resolve_outputs_root(path: Path) -> Path:
    candidate = path.resolve()
    if (candidate / "final_summary.csv").is_file():
        return candidate
    outputs_candidate = candidate / "outputs"
    if (outputs_candidate / "final_summary.csv").is_file():
        return outputs_candidate
    raise FileNotFoundError(f"Could not find final_summary.csv under {candidate}")


def as_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def mean(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    return sum(values) / float(len(values))


def stddev(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / float(len(values)))


def cv(values: Sequence[float]) -> float:
    mu = mean(values)
    sigma = stddev(values)
    if not math.isfinite(mu) or abs(mu) <= 1.0e-12:
        return float("nan")
    return sigma / abs(mu)


def write_csv(path: Path, rows: Iterable[Dict[str, object]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def parse_profile_time(token: str) -> float:
    return float(token.replace("p", "."))


def fit_alpha_from_profile(path: Path) -> Tuple[float, float]:
    numerator = 0.0
    denominator = 0.0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            eps_value = as_float(row.get("eps"))
            residue_value = as_float(row.get("R"))
            numerator += eps_value * residue_value
            denominator += residue_value * residue_value
    if denominator <= 1.0e-12:
        return float("nan"), denominator
    return numerator / denominator, denominator


def collect_profiles_by_run(outputs_root: Path) -> Tuple[Dict[str, Dict[float, Path]], Dict[float, List[Path]]]:
    profiles_dir = outputs_root / "profiles"
    by_run: Dict[str, Dict[float, Path]] = defaultdict(dict)
    by_time: Dict[float, List[Path]] = defaultdict(list)
    for path in profiles_dir.glob("profile_run_*.csv"):
        match = PROFILE_PATTERN.match(path.name)
        if not match:
            continue
        run_id = match.group("run_id")
        time = parse_profile_time(match.group("time"))
        by_run[run_id][time] = path
        by_time[time].append(path)
    return by_run, by_time


def sample_times(times: Sequence[float], target_count: int = 21) -> List[float]:
    if not times:
        return []
    if len(times) <= target_count:
        return list(times)
    indices = sorted({round(index * (len(times) - 1) / (target_count - 1)) for index in range(target_count)})
    return [times[index] for index in indices]


def load_final_summary_meta(outputs_root: Path) -> Dict[str, Dict[str, str]]:
    meta: Dict[str, Dict[str, str]] = {}
    with (outputs_root / "final_summary.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            meta[str(row.get("run_id", ""))] = row
    return meta


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure alpha stability for baseline standard batches.")
    parser.add_argument(
        "--batch",
        action="append",
        required=True,
        help="Baseline batch directory. Can be provided multiple times.",
    )
    parser.add_argument("--summary-output", required=True, help="Destination CSV path for per-batch alpha summaries.")
    parser.add_argument("--ic-output", required=True, help="Destination CSV path for per-IC final alpha summaries.")
    parser.add_argument("--trace-output", required=True, help="Destination CSV path for sampled alpha time traces.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary_rows: List[Dict[str, object]] = []
    ic_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []

    for batch_arg in args.batch:
        outputs_root = resolve_outputs_root(Path(batch_arg))
        batch_name = outputs_root.parent.name
        by_run, by_time = collect_profiles_by_run(outputs_root)
        meta = load_final_summary_meta(outputs_root)

        final_alpha_values: List[float] = []
        final_denominators: List[float] = []
        alpha_by_ic: Dict[str, List[float]] = defaultdict(list)
        denominator_by_ic: Dict[str, List[float]] = defaultdict(list)

        for run_id, profiles in by_run.items():
            final_time = max(profiles)
            alpha_value, denominator = fit_alpha_from_profile(profiles[final_time])
            final_denominators.append(denominator)
            if math.isfinite(alpha_value):
                final_alpha_values.append(alpha_value)
                ic_type = str(meta.get(run_id, {}).get("IC_type", ""))
                alpha_by_ic[ic_type].append(alpha_value)
                denominator_by_ic[ic_type].append(denominator)

        sampled_trace_values: List[Tuple[float, float, float, int]] = []
        all_times = sorted(by_time)
        sampled_times = sample_times(all_times)
        for time in sampled_times:
            numerator = 0.0
            denominator = 0.0
            for path in by_time[time]:
                alpha_value, profile_denominator = fit_alpha_from_profile(path)
                if math.isfinite(alpha_value):
                    denominator += profile_denominator
                    numerator += alpha_value * profile_denominator
            weighted_alpha = float("nan")
            if denominator > 1.0e-12:
                weighted_alpha = numerator / denominator
            sampled_trace_values.append((time, weighted_alpha, denominator, len(by_time[time])))
            trace_rows.append(
                {
                    "batch_name": batch_name,
                    "time": f"{time:.6f}",
                    "alpha_weighted_mean": f"{weighted_alpha:.12f}" if math.isfinite(weighted_alpha) else "",
                    "residue_support_denom": f"{denominator:.12e}",
                    "profile_count": len(by_time[time]),
                    "alpha_identifiable": str(denominator > 1.0e-12).lower(),
                }
            )

        late_trace_values = [
            alpha_value
            for time, alpha_value, denominator, _ in sampled_trace_values
            if math.isfinite(alpha_value) and time >= 0.8 * all_times[-1]
        ]
        late_mean = mean(late_trace_values)
        late_std = stddev(late_trace_values)
        late_cv = cv(late_trace_values)
        final_mean = mean(final_alpha_values)
        final_std = stddev(final_alpha_values)
        final_cv = cv(final_alpha_values)
        ic_means = {ic_type: mean(values) for ic_type, values in alpha_by_ic.items()}
        ic_mean_values = list(ic_means.values())
        ic_spread = (max(ic_mean_values) - min(ic_mean_values)) if ic_mean_values else float("nan")

        summary_rows.append(
            {
                "batch_name": batch_name,
                "final_identifiable_run_count": len(final_alpha_values),
                "final_skipped_run_count": len(by_run) - len(final_alpha_values),
                "final_alpha_mean": f"{final_mean:.12f}" if math.isfinite(final_mean) else "",
                "final_alpha_std": f"{final_std:.12f}" if math.isfinite(final_std) else "",
                "final_alpha_cv": f"{final_cv:.12f}" if math.isfinite(final_cv) else "",
                "late_trace_alpha_mean": f"{late_mean:.12f}" if math.isfinite(late_mean) else "",
                "late_trace_alpha_std": f"{late_std:.12f}" if math.isfinite(late_std) else "",
                "late_trace_alpha_cv": f"{late_cv:.12f}" if math.isfinite(late_cv) else "",
                "late_trace_point_count": len(late_trace_values),
                "ic_group_count": len(alpha_by_ic),
                "ic_mean_spread": f"{ic_spread:.12f}" if math.isfinite(ic_spread) else "",
                "alpha_identifiable_at_final": str(len(final_alpha_values) > 0).lower(),
            }
        )

        for ic_type, values in sorted(alpha_by_ic.items()):
            ic_rows.append(
                {
                    "batch_name": batch_name,
                    "IC_type": ic_type,
                    "final_alpha_mean": f"{mean(values):.12f}",
                    "final_alpha_std": f"{stddev(values):.12f}",
                    "final_alpha_cv": f"{cv(values):.12f}",
                    "run_count": len(values),
                    "mean_residue_support_denom": f"{mean(denominator_by_ic[ic_type]):.12e}",
                }
            )

    write_csv(
        Path(args.summary_output).resolve(),
        summary_rows,
        [
            "batch_name",
            "final_identifiable_run_count",
            "final_skipped_run_count",
            "final_alpha_mean",
            "final_alpha_std",
            "final_alpha_cv",
            "late_trace_alpha_mean",
            "late_trace_alpha_std",
            "late_trace_alpha_cv",
            "late_trace_point_count",
            "ic_group_count",
            "ic_mean_spread",
            "alpha_identifiable_at_final",
        ],
    )
    write_csv(
        Path(args.ic_output).resolve(),
        ic_rows,
        [
            "batch_name",
            "IC_type",
            "final_alpha_mean",
            "final_alpha_std",
            "final_alpha_cv",
            "run_count",
            "mean_residue_support_denom",
        ],
    )
    write_csv(
        Path(args.trace_output).resolve(),
        trace_rows,
        [
            "batch_name",
            "time",
            "alpha_weighted_mean",
            "residue_support_denom",
            "profile_count",
            "alpha_identifiable",
        ],
    )


if __name__ == "__main__":
    main()
