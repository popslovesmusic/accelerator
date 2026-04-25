from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


PROFILE_PATTERN = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p\-]+)\.csv$")

PAIR_COLUMNS = [
    "label",
    "baseline_batch",
    "comparison_batch",
    "baseline_run_id",
    "comparison_run_id",
    "seed",
    "IC_type",
    "kappa",
    "lam",
    "phase_expression",
    "mu",
    "nu",
    "alpha_fit",
    "beta_fit",
    "baseline_classification",
    "comparison_classification",
    "basin_identity_match",
    "baseline_profile_time",
    "comparison_profile_time",
    "baseline_delta_mean",
    "comparison_delta_mean",
    "delta_mean_shift",
    "baseline_delta_l2",
    "comparison_delta_l2",
    "delta_l2_ratio",
    "baseline_delta_curvature_l2",
    "comparison_delta_curvature_l2",
    "delta_curvature_l2_ratio",
    "baseline_delta_zero_crossings",
    "comparison_delta_zero_crossings",
    "delta_zero_crossing_shift",
    "baseline_sigma_mean",
    "comparison_sigma_mean",
    "sigma_mean_shift",
    "baseline_sigma_l2",
    "comparison_sigma_l2",
    "sigma_l2_ratio",
    "delta_profile_correlation",
    "delta_curvature_correlation",
    "delta_signature_similarity",
]

SUMMARY_COLUMNS = [
    "label",
    "baseline_batch",
    "comparison_batch",
    "phase_expression",
    "mu",
    "nu",
    "alpha_fit",
    "beta_fit",
    "pair_count",
    "basin_match_count",
    "basin_match_rate",
    "mean_delta_signature_similarity",
    "mean_delta_profile_correlation",
    "mean_delta_curvature_correlation",
    "mean_delta_l2_ratio",
    "mean_sigma_l2_ratio",
]


@dataclass
class ProfileData:
    time: float
    x: List[float]
    eps: List[float]
    rho: List[float]
    residue: List[float]


def resolve_outputs_root(path: Path) -> Path:
    candidate = path.resolve()
    if (candidate / "final_summary.csv").is_file():
        return candidate
    outputs_candidate = candidate / "outputs"
    if (outputs_candidate / "final_summary.csv").is_file():
        return outputs_candidate
    raise FileNotFoundError(f"Could not find final_summary.csv under {candidate}")


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[Dict[str, object]], columns: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def as_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def safe_ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1.0e-12:
        return 0.0 if abs(numerator) <= 1.0e-12 else float("inf")
    return numerator / denominator


def parse_profile_time(token: str) -> float:
    return float(token.replace("p", "."))


def pair_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        str(row.get("seed", "")),
        str(row.get("IC_type", row.get("ic_type", ""))),
        str(row.get("kappa", "")),
        str(row.get("lam", row.get("lambda", ""))),
    )


def load_final_profiles(outputs_root: Path) -> Dict[str, ProfileData]:
    profiles_dir = outputs_root / "profiles"
    latest_paths: Dict[str, Tuple[float, Path]] = {}
    for path in profiles_dir.glob("profile_run_*.csv"):
        match = PROFILE_PATTERN.match(path.name)
        if not match:
            continue
        run_id = match.group("run_id")
        time = parse_profile_time(match.group("time"))
        current = latest_paths.get(run_id)
        if current is None or time > current[0]:
            latest_paths[run_id] = (time, path)

    loaded: Dict[str, ProfileData] = {}
    for run_id, (time, path) in latest_paths.items():
        x: List[float] = []
        eps: List[float] = []
        rho: List[float] = []
        residue: List[float] = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                x.append(as_float(row.get("x")))
                eps.append(as_float(row.get("eps")))
                rho.append(as_float(row.get("rho")))
                residue.append(as_float(row.get("R")))
        loaded[run_id] = ProfileData(time=time, x=x, eps=eps, rho=rho, residue=residue)
    return loaded


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def l2_norm(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / float(len(values)))


def second_differences(values: Sequence[float], x: Sequence[float]) -> List[float]:
    if len(values) < 3:
        return []
    if len(x) >= 2:
        dx = x[1] - x[0]
    else:
        dx = 1.0
    if abs(dx) <= 1.0e-12:
        dx = 1.0
    scale = dx * dx
    return [
        (values[index + 1] - 2.0 * values[index] + values[index - 1]) / scale
        for index in range(1, len(values) - 1)
    ]


def zero_crossings(values: Sequence[float]) -> int:
    crossings = 0
    previous_sign = 0
    for value in values:
        sign = 0
        if value > 0.0:
            sign = 1
        elif value < 0.0:
            sign = -1
        if sign == 0:
            continue
        if previous_sign != 0 and sign != previous_sign:
            crossings += 1
        previous_sign = sign
    return crossings


def pearson_correlation(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_mean = mean(left)
    right_mean = mean(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    numerator = sum(a * b for a, b in zip(left_centered, right_centered))
    left_scale = math.sqrt(sum(a * a for a in left_centered))
    right_scale = math.sqrt(sum(b * b for b in right_centered))
    if left_scale <= 1.0e-12 and right_scale <= 1.0e-12:
        return 1.0
    if left_scale <= 1.0e-12 or right_scale <= 1.0e-12:
        return 0.0
    return numerator / (left_scale * right_scale)


def ratio_similarity(ratio: float) -> float:
    if not math.isfinite(ratio) or ratio <= 0.0:
        return 0.0
    return 1.0 / (1.0 + abs(math.log(ratio)))


def bounded_correlation_similarity(correlation: float) -> float:
    return max(0.0, min(1.0, 0.5 * (correlation + 1.0)))


def fit_alpha_from_profiles(profiles: Dict[str, ProfileData]) -> float:
    numerator = 0.0
    denominator = 0.0
    for profile in profiles.values():
        for eps_value, residue_value in zip(profile.eps, profile.residue):
            numerator += eps_value * residue_value
            denominator += residue_value * residue_value
    if denominator <= 1.0e-12:
        return 1.0
    return numerator / denominator


def profile_metrics(profile: ProfileData, *, alpha: float, beta: float) -> Dict[str, object]:
    delta = [eps_value - alpha * residue_value for eps_value, residue_value in zip(profile.eps, profile.residue)]
    sigma = [eps_value + beta * residue_value for eps_value, residue_value in zip(profile.eps, profile.residue)]
    delta_curvature = second_differences(delta, profile.x)
    return {
        "delta_values": delta,
        "sigma_values": sigma,
        "delta_curvature_values": delta_curvature,
        "delta_mean": mean(delta),
        "delta_l2": l2_norm(delta),
        "delta_curvature_l2": l2_norm(delta_curvature),
        "delta_zero_crossings": zero_crossings(delta),
        "sigma_mean": mean(sigma),
        "sigma_l2": l2_norm(sigma),
    }


def build_pair_rows(
    *,
    label: str,
    baseline_batch: Path,
    comparison_batch: Path,
    baseline_summary_rows: List[Dict[str, str]],
    comparison_summary_rows: List[Dict[str, str]],
    baseline_profiles: Dict[str, ProfileData],
    comparison_profiles: Dict[str, ProfileData],
    alpha: float,
    beta: float,
) -> List[Dict[str, object]]:
    baseline_by_key = {pair_key(row): row for row in baseline_summary_rows}
    pair_rows: List[Dict[str, object]] = []
    for comparison_row in comparison_summary_rows:
        key = pair_key(comparison_row)
        baseline_row = baseline_by_key.get(key)
        if baseline_row is None:
            continue

        baseline_run_id = str(baseline_row.get("run_id", ""))
        comparison_run_id = str(comparison_row.get("run_id", ""))
        baseline_profile = baseline_profiles.get(baseline_run_id)
        comparison_profile = comparison_profiles.get(comparison_run_id)
        if baseline_profile is None or comparison_profile is None:
            continue

        baseline_metrics = profile_metrics(baseline_profile, alpha=alpha, beta=beta)
        comparison_metrics = profile_metrics(comparison_profile, alpha=alpha, beta=beta)
        delta_l2_ratio = safe_ratio(float(comparison_metrics["delta_l2"]), float(baseline_metrics["delta_l2"]))
        sigma_l2_ratio = safe_ratio(float(comparison_metrics["sigma_l2"]), float(baseline_metrics["sigma_l2"]))
        delta_curvature_l2_ratio = safe_ratio(
            float(comparison_metrics["delta_curvature_l2"]),
            float(baseline_metrics["delta_curvature_l2"]),
        )
        delta_profile_correlation = pearson_correlation(
            baseline_metrics["delta_values"],
            comparison_metrics["delta_values"],
        )
        delta_curvature_correlation = pearson_correlation(
            baseline_metrics["delta_curvature_values"],
            comparison_metrics["delta_curvature_values"],
        )
        delta_signature_similarity = mean(
            [
                ratio_similarity(delta_l2_ratio),
                ratio_similarity(delta_curvature_l2_ratio),
                bounded_correlation_similarity(delta_profile_correlation),
                bounded_correlation_similarity(delta_curvature_correlation),
            ]
        )

        baseline_classification = str(
            baseline_row.get("regime_classification", baseline_row.get("classification", ""))
        )
        comparison_classification = str(
            comparison_row.get("regime_classification", comparison_row.get("classification", ""))
        )
        pair_rows.append(
            {
                "label": label,
                "baseline_batch": baseline_batch.parent.name,
                "comparison_batch": comparison_batch.parent.name,
                "baseline_run_id": baseline_run_id,
                "comparison_run_id": comparison_run_id,
                "seed": key[0],
                "IC_type": key[1],
                "kappa": key[2],
                "lam": key[3],
                "phase_expression": comparison_row.get("phase_expression", ""),
                "mu": comparison_row.get("mu", ""),
                "nu": comparison_row.get("nu", ""),
                "alpha_fit": f"{alpha:.12f}",
                "beta_fit": f"{beta:.12f}",
                "baseline_classification": baseline_classification,
                "comparison_classification": comparison_classification,
                "basin_identity_match": str(baseline_classification == comparison_classification).lower(),
                "baseline_profile_time": f"{baseline_profile.time:.6f}",
                "comparison_profile_time": f"{comparison_profile.time:.6f}",
                "baseline_delta_mean": f"{float(baseline_metrics['delta_mean']):.12f}",
                "comparison_delta_mean": f"{float(comparison_metrics['delta_mean']):.12f}",
                "delta_mean_shift": f"{float(comparison_metrics['delta_mean']) - float(baseline_metrics['delta_mean']):.12f}",
                "baseline_delta_l2": f"{float(baseline_metrics['delta_l2']):.12f}",
                "comparison_delta_l2": f"{float(comparison_metrics['delta_l2']):.12f}",
                "delta_l2_ratio": f"{delta_l2_ratio:.12f}",
                "baseline_delta_curvature_l2": f"{float(baseline_metrics['delta_curvature_l2']):.12f}",
                "comparison_delta_curvature_l2": f"{float(comparison_metrics['delta_curvature_l2']):.12f}",
                "delta_curvature_l2_ratio": f"{delta_curvature_l2_ratio:.12f}",
                "baseline_delta_zero_crossings": int(baseline_metrics["delta_zero_crossings"]),
                "comparison_delta_zero_crossings": int(comparison_metrics["delta_zero_crossings"]),
                "delta_zero_crossing_shift": int(comparison_metrics["delta_zero_crossings"]) - int(baseline_metrics["delta_zero_crossings"]),
                "baseline_sigma_mean": f"{float(baseline_metrics['sigma_mean']):.12f}",
                "comparison_sigma_mean": f"{float(comparison_metrics['sigma_mean']):.12f}",
                "sigma_mean_shift": f"{float(comparison_metrics['sigma_mean']) - float(baseline_metrics['sigma_mean']):.12f}",
                "baseline_sigma_l2": f"{float(baseline_metrics['sigma_l2']):.12f}",
                "comparison_sigma_l2": f"{float(comparison_metrics['sigma_l2']):.12f}",
                "sigma_l2_ratio": f"{sigma_l2_ratio:.12f}",
                "delta_profile_correlation": f"{delta_profile_correlation:.12f}",
                "delta_curvature_correlation": f"{delta_curvature_correlation:.12f}",
                "delta_signature_similarity": f"{delta_signature_similarity:.12f}",
            }
        )
    return pair_rows


def build_summary_rows(pair_rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str, str, str, str, str], List[Dict[str, object]]] = defaultdict(list)
    for row in pair_rows:
        group_key = (
            str(row.get("label", "")),
            str(row.get("baseline_batch", "")),
            str(row.get("comparison_batch", "")),
            str(row.get("phase_expression", "")),
            str(row.get("mu", "")),
            str(row.get("nu", "")),
        )
        grouped[group_key].append(row)

    summary_rows: List[Dict[str, object]] = []
    for key in sorted(grouped):
        rows = grouped[key]
        pair_count = len(rows)
        basin_match_count = sum(1 for row in rows if str(row.get("basin_identity_match", "")).lower() == "true")
        summary_rows.append(
            {
                "label": key[0],
                "baseline_batch": key[1],
                "comparison_batch": key[2],
                "phase_expression": key[3],
                "mu": key[4],
                "nu": key[5],
                "alpha_fit": rows[0].get("alpha_fit", ""),
                "beta_fit": rows[0].get("beta_fit", ""),
                "pair_count": pair_count,
                "basin_match_count": basin_match_count,
                "basin_match_rate": f"{safe_ratio(float(basin_match_count), float(pair_count)):.6f}",
                "mean_delta_signature_similarity": f"{mean([as_float(str(row.get('delta_signature_similarity', '0'))) for row in rows]):.6f}",
                "mean_delta_profile_correlation": f"{mean([as_float(str(row.get('delta_profile_correlation', '0'))) for row in rows]):.6f}",
                "mean_delta_curvature_correlation": f"{mean([as_float(str(row.get('delta_curvature_correlation', '0'))) for row in rows]):.6f}",
                "mean_delta_l2_ratio": f"{mean([as_float(str(row.get('delta_l2_ratio', '0'))) for row in rows]):.6f}",
                "mean_sigma_l2_ratio": f"{mean([as_float(str(row.get('sigma_l2_ratio', '0'))) for row in rows]):.6f}",
            }
        )
    return summary_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare PDE runs through relational Delta/Sigma signatures.")
    parser.add_argument("--label", required=True, help="Short label for this comparison.")
    parser.add_argument("--baseline-batch", required=True, help="Standard baseline batch directory.")
    parser.add_argument("--comparison-batch", required=True, help="Comparison batch directory.")
    parser.add_argument("--pair-output", required=True, help="Destination CSV path for pair-level metrics.")
    parser.add_argument("--summary-output", required=True, help="Destination CSV path for grouped summary metrics.")
    parser.add_argument("--alpha", default="auto", help="Relational Delta scale alpha. Use 'auto' to fit from baseline profiles.")
    parser.add_argument("--beta", default="same-as-alpha", help="Sigma scale beta. Use 'same-as-alpha' or a numeric value.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    baseline_outputs = resolve_outputs_root(Path(args.baseline_batch))
    comparison_outputs = resolve_outputs_root(Path(args.comparison_batch))

    baseline_summary_rows = load_csv_rows(baseline_outputs / "final_summary.csv")
    comparison_summary_rows = load_csv_rows(comparison_outputs / "final_summary.csv")
    baseline_profiles = load_final_profiles(baseline_outputs)
    comparison_profiles = load_final_profiles(comparison_outputs)

    alpha = fit_alpha_from_profiles(baseline_profiles) if args.alpha == "auto" else float(args.alpha)
    beta = alpha if args.beta == "same-as-alpha" else float(args.beta)

    pair_rows = build_pair_rows(
        label=args.label,
        baseline_batch=baseline_outputs,
        comparison_batch=comparison_outputs,
        baseline_summary_rows=baseline_summary_rows,
        comparison_summary_rows=comparison_summary_rows,
        baseline_profiles=baseline_profiles,
        comparison_profiles=comparison_profiles,
        alpha=alpha,
        beta=beta,
    )
    summary_rows = build_summary_rows(pair_rows)

    write_csv(Path(args.pair_output).resolve(), pair_rows, PAIR_COLUMNS)
    write_csv(Path(args.summary_output).resolve(), summary_rows, SUMMARY_COLUMNS)
    print(
        f"Wrote {len(pair_rows)} pair rows and {len(summary_rows)} summary rows "
        f"(alpha={alpha:.6f}, beta={beta:.6f})"
    )


if __name__ == "__main__":
    main()
