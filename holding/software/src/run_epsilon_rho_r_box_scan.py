from __future__ import annotations

import argparse
import csv
import json
from copy import deepcopy
from itertools import product
from pathlib import Path
from typing import Any

from software.src.epsilon_rho_r_box_v1 import RunConfig, load_run_config, simulate


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def build_case_config(
    base: RunConfig,
    alpha: float,
    beta: float,
    gamma: float,
    v: float,
    h: float,
    rho_max: float,
    output_dir: str,
) -> RunConfig:
    config = deepcopy(base)
    config.model.alpha = alpha
    config.model.beta = beta
    config.model.gamma = gamma
    config.model.v = v
    config.model.h = h
    config.box.rho_max = rho_max
    config.output_dir = output_dir
    return config


def summarize_case(
    case_id: str,
    result: dict[str, Any],
    alpha: float,
    beta: float,
    gamma: float,
    v: float,
    h: float,
    rho_max: float,
) -> dict[str, Any]:
    diagnostics = result["diagnostics"]
    times = result["times"]
    final = diagnostics[-1]
    min_epsilon_margin = min(float(row["box_epsilon_margin"]) for row in diagnostics)
    min_rho_lower_margin = min(float(row["box_rho_lower_margin"]) for row in diagnostics)
    min_rho_upper_margin = min(float(row["box_rho_upper_margin"]) for row in diagnostics)
    min_residue_margin = min(float(row["box_residue_margin"]) for row in diagnostics)
    min_support_floor_margin = min(float(row["live_support_floor_margin"]) for row in diagnostics)
    min_easy_regime_margin = min(float(row["live_easy_regime_margin"]) for row in diagnostics)
    peak_rho_index = max(range(len(diagnostics)), key=lambda index: float(diagnostics[index]["rho_max"]))
    peak_rho_time = float(times[peak_rho_index])
    peak_rho_max = float(diagnostics[peak_rho_index]["rho_max"])
    peak_epsilon_max = float(diagnostics[peak_rho_index]["epsilon_max"])
    peak_residue_max = float(diagnostics[peak_rho_index]["residue_max"])
    peak_followup_1_index = min(peak_rho_index + 1, len(diagnostics) - 1)
    peak_followup_2_index = min(peak_rho_index + 2, len(diagnostics) - 1)
    peak_followup_4_index = min(peak_rho_index + 4, len(diagnostics) - 1)
    rho_drop_1 = peak_rho_max - float(diagnostics[peak_followup_1_index]["rho_max"])
    rho_drop_2 = peak_rho_max - float(diagnostics[peak_followup_2_index]["rho_max"])
    rho_drop_4 = peak_rho_max - float(diagnostics[peak_followup_4_index]["rho_max"])
    peak_rho_excess = max(0.0, peak_rho_max - rho_max)
    rho_relaxation_to_final = max(0.0, peak_rho_max - float(final["rho_max"]))
    rho_relaxation_reserve = rho_relaxation_to_final - peak_rho_excess
    rho_recovery_ratio = rho_relaxation_to_final / peak_rho_excess if peak_rho_excess > 0.0 else None
    negative_indices = [index for index, row in enumerate(diagnostics) if float(row["box_rho_upper_margin"]) < 0.0]
    first_negative_time = None
    last_negative_time = None
    negative_duration = 0.0
    reentered_by_end = False
    if negative_indices:
        first_negative_time = float(times[negative_indices[0]])
        last_negative_time = float(times[negative_indices[-1]])
        negative_duration = last_negative_time - first_negative_time
        reentered_by_end = float(final["box_rho_upper_margin"]) >= 0.0
    limiting = {
        "epsilon": min_epsilon_margin,
        "rho_lower": min_rho_lower_margin,
        "rho_upper": min_rho_upper_margin,
        "residue": min_residue_margin,
        "support_floor": min_support_floor_margin,
    }
    limiting_face = min(limiting, key=limiting.get)
    box_analysis = result["box_analysis"]
    return {
        "case_id": case_id,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "v": v,
        "h": h,
        "rho_max": rho_max,
        "box_admissible": bool(box_analysis["box_admissible"]),
        "easy_regime_feasible": bool(box_analysis["easy_regime_feasible"]),
        "shifted_floor_feasible": bool(box_analysis["shifted_floor_feasible"]),
        "epsilon_critical": float(box_analysis["epsilon_critical"]),
        "epsilon_threshold_gap": float(box_analysis["epsilon_threshold_gap"]),
        "rho_upper_face_margin": float(box_analysis["rho_upper_face_margin"]),
        "min_epsilon_margin": min_epsilon_margin,
        "min_rho_lower_margin": min_rho_lower_margin,
        "min_rho_upper_margin": min_rho_upper_margin,
        "min_residue_margin": min_residue_margin,
        "min_support_floor_margin": min_support_floor_margin,
        "min_easy_regime_margin": min_easy_regime_margin,
        "peak_rho_time": peak_rho_time,
        "peak_rho_max": peak_rho_max,
        "peak_epsilon_max": peak_epsilon_max,
        "peak_residue_max": peak_residue_max,
        "rho_drop_1": rho_drop_1,
        "rho_drop_2": rho_drop_2,
        "rho_drop_4": rho_drop_4,
        "peak_rho_excess": peak_rho_excess,
        "rho_relaxation_to_final": rho_relaxation_to_final,
        "rho_relaxation_reserve": rho_relaxation_reserve,
        "rho_recovery_ratio": rho_recovery_ratio,
        "rho_upper_negative_count": len(negative_indices),
        "rho_upper_first_negative_time": first_negative_time,
        "rho_upper_last_negative_time": last_negative_time,
        "rho_upper_negative_duration": negative_duration,
        "rho_upper_reentered_by_end": reentered_by_end,
        "limiting_face": limiting_face,
        "limiting_margin": float(limiting[limiting_face]),
        "final_epsilon_max": float(final["epsilon_max"]),
        "final_rho_min": float(final["rho_min"]),
        "final_rho_max": float(final["rho_max"]),
        "final_residue_max": float(final["residue_max"]),
        "final_within_box": bool(final["within_box"]),
        "final_worst_box_face": str(final["worst_box_face"]),
        "final_worst_box_margin": float(final["worst_box_margin"]),
        "first_box_violation": result["first_box_violation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Narrow support-side scan for epsilon-rho-R box branch")
    parser.add_argument("--config", required=True, help="Path to base JSON config")
    parser.add_argument(
        "--output-dir",
        default="G:\\MPF\\orientation\\level2\\rerun_v23\\kept_results\\current\\outputs\\epsilon_rho_r_box_support_scan",
        help="Directory for scan outputs",
    )
    parser.add_argument("--alpha-values", default="0.65,0.75", help="Comma-separated alpha values")
    parser.add_argument("--beta-values", default="0.70,0.90", help="Comma-separated beta values")
    parser.add_argument("--gamma-values", default="1.00,1.40", help="Comma-separated gamma values")
    parser.add_argument("--v-values", default="0.06,0.10", help="Comma-separated v values")
    parser.add_argument("--h-values", default="0.07,0.09", help="Comma-separated h values")
    parser.add_argument("--rho-max-values", default="", help="Comma-separated rho_max values; empty uses config value")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    base = load_run_config(config_path)

    alpha_values = parse_float_list(args.alpha_values)
    beta_values = parse_float_list(args.beta_values)
    gamma_values = parse_float_list(args.gamma_values)
    v_values = parse_float_list(args.v_values)
    h_values = parse_float_list(args.h_values)
    rho_max_values = parse_float_list(args.rho_max_values) if args.rho_max_values.strip() else [base.box.rho_max]

    rows: list[dict[str, Any]] = []
    for index, (alpha, beta, gamma, v, h, rho_max) in enumerate(
        product(alpha_values, beta_values, gamma_values, v_values, h_values, rho_max_values),
        start=1,
    ):
        case_id = f"case_{index:02d}"
        case_output = str((output_dir / case_id).resolve())
        config = build_case_config(base, alpha, beta, gamma, v, h, rho_max, case_output)
        result = simulate(config)
        rows.append(summarize_case(case_id, result, alpha, beta, gamma, v, h, rho_max))

    rows.sort(key=lambda row: (0 if row["box_admissible"] else 1, row["limiting_margin"]))

    summary_json_path = output_dir / "scan_summary.json"
    summary_csv_path = output_dir / "scan_summary.csv"
    aggregate_path = output_dir / "aggregate.json"

    summary_json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with summary_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    limiting_face_counts: dict[str, int] = {}
    for row in rows:
        limiting_face = str(row["limiting_face"])
        limiting_face_counts[limiting_face] = limiting_face_counts.get(limiting_face, 0) + 1

    aggregate = {
        "case_count": len(rows),
        "admissible_case_count": sum(1 for row in rows if row["box_admissible"]),
        "within_box_case_count": sum(1 for row in rows if row["final_within_box"]),
        "limiting_face_counts": limiting_face_counts,
        "best_case": rows[0],
    }
    aggregate_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
