from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

from .delta_sigma_calibration import load_delta_sigma_calibration_table


PROFILE_PATTERN = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p\-]+)\.csv$")

NONDEGENERATE_COLUMNS = [
    "family",
    "baseline_batch",
    "comparison_batch",
    "seed",
    "IC_type",
    "kappa",
    "lam",
    "alpha",
    "baseline_classification",
    "comparison_classification",
    "basin_identity_match",
    "delta_profile_correlation",
    "delta_curvature_correlation",
    "delta_l2_ratio",
    "delta_zero_crossing_shift",
    "pair_pass",
]

SS2_COLUMNS = [
    "family",
    "baseline_batch",
    "comparison_batch",
    "seed",
    "IC_type",
    "kappa",
    "lam",
    "baseline_classification",
    "comparison_classification",
    "basin_identity_match",
    "no_new_runaway",
    "epsilon_profile_correlation",
    "epsilon_l2_ratio",
    "pair_pass",
]

SUMMARY_COLUMNS = [
    "family",
    "baseline_batch",
    "comparison_batch",
    "pair_count",
    "pass_count",
    "pass_rate",
    "accepted",
    "acceptance_rule",
]


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


def pair_key(row: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        str(row.get("seed", "")),
        str(row.get("IC_type", row.get("ic_type", ""))),
        str(row.get("kappa", "")),
        str(row.get("lam", row.get("lambda", ""))),
    )


def parse_profile_time(token: str) -> float:
    return float(token.replace("p", "."))


def load_final_profiles(outputs_root: Path) -> Dict[str, Dict[str, List[float] | float]]:
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

    loaded: Dict[str, Dict[str, List[float] | float]] = {}
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
        loaded[run_id] = {"time": time, "x": x, "eps": eps, "rho": rho, "R": residue}
    return loaded


def mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / float(len(values))


def l2_norm(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / float(len(values)))


def safe_ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1.0e-12:
        return 0.0 if abs(numerator) <= 1.0e-12 else float("inf")
    return numerator / denominator


def second_differences(values: Sequence[float], x: Sequence[float]) -> List[float]:
    if len(values) < 3:
        return []
    dx = x[1] - x[0] if len(x) > 1 else 1.0
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


def alpha_for_family_ic(family: str, ic_type: str) -> float:
    families = load_delta_sigma_calibration_table()["families"]
    family_entry = families[family]
    if family_entry["mode"] == "by_ic_type":
        return float(family_entry["alphas"][ic_type])
    return float(family_entry["alpha"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the frozen Delta-preservation acceptance gate.")
    parser.add_argument("--family", required=True, choices=["SS2", "SS3", "R2", "Shelf"])
    parser.add_argument("--baseline-batch", required=True)
    parser.add_argument("--comparison-batch", required=True)
    parser.add_argument("--pair-output", required=True)
    parser.add_argument("--summary-output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    family = str(args.family)
    baseline_outputs = resolve_outputs_root(Path(args.baseline_batch))
    comparison_outputs = resolve_outputs_root(Path(args.comparison_batch))

    baseline_summary_rows = {pair_key(row): row for row in load_csv_rows(baseline_outputs / "final_summary.csv")}
    comparison_summary_rows = {pair_key(row): row for row in load_csv_rows(comparison_outputs / "final_summary.csv")}
    baseline_profiles = load_final_profiles(baseline_outputs)
    comparison_profiles = load_final_profiles(comparison_outputs)

    pair_rows: List[Dict[str, object]] = []
    for key in sorted(set(baseline_summary_rows) & set(comparison_summary_rows)):
        baseline_row = baseline_summary_rows[key]
        comparison_row = comparison_summary_rows[key]
        baseline_profile = baseline_profiles.get(str(baseline_row.get("run_id", "")))
        comparison_profile = comparison_profiles.get(str(comparison_row.get("run_id", "")))
        if baseline_profile is None or comparison_profile is None:
            continue

        baseline_classification = str(
            baseline_row.get("regime_classification", baseline_row.get("classification", ""))
        )
        comparison_classification = str(
            comparison_row.get("regime_classification", comparison_row.get("classification", ""))
        )
        basin_identity_match = baseline_classification == comparison_classification
        ic_type = key[1]

        if family == "SS2":
            baseline_eps = baseline_profile["eps"]  # type: ignore[index]
            comparison_eps = comparison_profile["eps"]  # type: ignore[index]
            epsilon_profile_correlation = pearson_correlation(baseline_eps, comparison_eps)
            epsilon_l2_ratio = safe_ratio(l2_norm(comparison_eps), l2_norm(baseline_eps))
            no_new_runaway = comparison_classification != "runaway_or_unphysical"
            pair_pass = (
                basin_identity_match
                and no_new_runaway
                and epsilon_profile_correlation >= 0.95
                and 0.80 <= epsilon_l2_ratio <= 1.25
            )
            pair_rows.append(
                {
                    "family": family,
                    "baseline_batch": baseline_outputs.parent.name,
                    "comparison_batch": comparison_outputs.parent.name,
                    "seed": key[0],
                    "IC_type": ic_type,
                    "kappa": key[2],
                    "lam": key[3],
                    "baseline_classification": baseline_classification,
                    "comparison_classification": comparison_classification,
                    "basin_identity_match": str(basin_identity_match).lower(),
                    "no_new_runaway": str(no_new_runaway).lower(),
                    "epsilon_profile_correlation": f"{epsilon_profile_correlation:.12f}",
                    "epsilon_l2_ratio": f"{epsilon_l2_ratio:.12f}",
                    "pair_pass": str(pair_pass).lower(),
                }
            )
            continue

        alpha = alpha_for_family_ic(family, ic_type)
        baseline_eps = baseline_profile["eps"]  # type: ignore[index]
        baseline_residue = baseline_profile["R"]  # type: ignore[index]
        comparison_eps = comparison_profile["eps"]  # type: ignore[index]
        comparison_residue = comparison_profile["R"]  # type: ignore[index]
        x_values = baseline_profile["x"]  # type: ignore[index]

        baseline_delta = [eps_value - alpha * residue_value for eps_value, residue_value in zip(baseline_eps, baseline_residue)]
        comparison_delta = [eps_value - alpha * residue_value for eps_value, residue_value in zip(comparison_eps, comparison_residue)]
        baseline_delta_curvature = second_differences(baseline_delta, x_values)
        comparison_delta_curvature = second_differences(comparison_delta, x_values)

        delta_profile_correlation = pearson_correlation(baseline_delta, comparison_delta)
        delta_curvature_correlation = pearson_correlation(baseline_delta_curvature, comparison_delta_curvature)
        delta_l2_ratio = safe_ratio(l2_norm(comparison_delta), l2_norm(baseline_delta))
        delta_zero_crossing_shift = zero_crossings(comparison_delta) - zero_crossings(baseline_delta)
        pair_pass = (
            basin_identity_match
            and delta_profile_correlation >= 0.95
            and delta_curvature_correlation >= 0.85
            and 0.80 <= delta_l2_ratio <= 1.25
            and delta_zero_crossing_shift == 0
        )

        pair_rows.append(
            {
                "family": family,
                "baseline_batch": baseline_outputs.parent.name,
                "comparison_batch": comparison_outputs.parent.name,
                "seed": key[0],
                "IC_type": ic_type,
                "kappa": key[2],
                "lam": key[3],
                "alpha": f"{alpha:.12f}",
                "baseline_classification": baseline_classification,
                "comparison_classification": comparison_classification,
                "basin_identity_match": str(basin_identity_match).lower(),
                "delta_profile_correlation": f"{delta_profile_correlation:.12f}",
                "delta_curvature_correlation": f"{delta_curvature_correlation:.12f}",
                "delta_l2_ratio": f"{delta_l2_ratio:.12f}",
                "delta_zero_crossing_shift": delta_zero_crossing_shift,
                "pair_pass": str(pair_pass).lower(),
            }
        )

    pass_count = sum(1 for row in pair_rows if str(row.get("pair_pass", "")).lower() == "true")
    pair_count = len(pair_rows)
    accepted = pass_count == pair_count and pair_count > 0
    acceptance_rule = (
        "SS2 surrogate gate"
        if family == "SS2"
        else "Frozen Delta hard gate"
    )
    summary_rows = [
        {
            "family": family,
            "baseline_batch": baseline_outputs.parent.name,
            "comparison_batch": comparison_outputs.parent.name,
            "pair_count": pair_count,
            "pass_count": pass_count,
            "pass_rate": f"{safe_ratio(float(pass_count), float(pair_count)):.6f}" if pair_count > 0 else "0.000000",
            "accepted": str(accepted).lower(),
            "acceptance_rule": acceptance_rule,
        }
    ]

    pair_columns = SS2_COLUMNS if family == "SS2" else NONDEGENERATE_COLUMNS
    write_csv(Path(args.pair_output).resolve(), pair_rows, pair_columns)
    write_csv(Path(args.summary_output).resolve(), summary_rows, SUMMARY_COLUMNS)
    print(
        f"Evaluated {family}: {pass_count}/{pair_count} pairs passed; accepted={str(accepted).lower()}"
    )


if __name__ == "__main__":
    main()
