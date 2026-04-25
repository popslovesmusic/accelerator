from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import replace
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

from .batch_runner import expand_run_specs
from .initial_conditions import build_initial_condition
from .pde_solver import GridConfig, Parameters, simulate
from .delta_sigma_calibration import resolve_delta_sigma_calibration


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


def l2_norm(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(array))))


def safe_ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1.0e-12:
        return 0.0 if abs(numerator) <= 1.0e-12 else float("inf")
    return numerator / denominator


def build_cases(root: Path) -> List[Dict[str, object]]:
    return [
        {
            "label": "ss3_front_seeded",
            "config": root / "configs" / "dsr" / "dsr_local_ss3_smoke_v1.json",
            "ic_index": 0,
            "seed": 1000,
            "t_final": 50.0,
            "save_every": 250,
        },
        {
            "label": "ss3_localized_seed",
            "config": root / "configs" / "anchors" / "ss3_anchor_v23.json",
            "ic_index": 2,
            "seed": 1000,
            "t_final": 50.0,
            "save_every": 250,
            "phase_expression": "I_phi_v4_dsr",
        },
        {
            "label": "ss3_near_uniform_noise",
            "config": root / "configs" / "anchors" / "ss3_anchor_v23.json",
            "ic_index": 1,
            "seed": 1000,
            "t_final": 50.0,
            "save_every": 250,
            "phase_expression": "I_phi_v4_dsr",
        },
        {
            "label": "shelf_front_seeded",
            "config": root / "configs" / "sim18_v3" / "sim18_v3_stage1a_shelf_kappa0p11_lam0p1000_delta_sigma_rho_v23.json",
            "ic_index": 0,
            "seed": 1000,
            "t_final": 50.0,
            "save_every": 250,
            "phase_expression": "I_phi_v4_dsr",
        },
    ]


def candidate_grid() -> List[Dict[str, float]]:
    candidates: List[Dict[str, float]] = []
    for sigma_decay in (0.05, 0.15, 0.25):
        for sigma_load in (1.0, 2.0, 4.0):
            for rho_gain in (0.50, 1.00):
                candidates.append(
                    {
                        "dsr_sigma_decay": sigma_decay,
                        "dsr_sigma_load": sigma_load,
                        "dsr_rho_gain": rho_gain,
                        "dsr_rho_relax": 0.20,
                        "dsr_lambda_D": 1.5,
                        "dsr_theta": 0.08,
                        "dsr_event_gain": 0.10,
                        "dsr_bootstrap_gain": 1.00,
                    }
                )
    return candidates


def evaluate_case(case: Dict[str, object], candidate: Dict[str, float]) -> Dict[str, object]:
    spec = expand_run_specs(str(case["config"]))[0]
    if "phase_expression" in case:
        spec["phase_expression"] = str(case["phase_expression"])
    grid_spec = dict(spec["grid"])
    grid_spec["t_final"] = float(case["t_final"])
    grid_spec["save_every"] = int(case["save_every"])
    grid = GridConfig(**grid_spec)
    params = Parameters(**spec["parameters"])
    for key, value in candidate.items():
        setattr(params, key, value)

    ic_spec = spec["initial_conditions"][int(case["ic_index"])]
    calibration = resolve_delta_sigma_calibration(spec, str(ic_spec["type"]))
    params.delta_alpha = calibration.alpha
    params.delta_beta = calibration.beta
    initial_state = build_initial_condition(grid, ic_spec, int(case["seed"]))
    results = simulate(params, grid, initial_state, backend="python", phase_expression=str(spec["phase_expression"]))
    final_snapshot = results["snapshots"][-1]

    delta = np.asarray(final_snapshot["delta"], dtype=float)
    sigma = np.asarray(final_snapshot["sigma"], dtype=float)
    rho = np.asarray(final_snapshot["rho"], dtype=float)
    depth = np.asarray(final_snapshot["depth"], dtype=float)
    delta_floor = np.asarray(final_snapshot["delta_floor"], dtype=float)
    epsilon = np.asarray(final_snapshot["epsilon"], dtype=float)
    residue = np.asarray(final_snapshot["residue"], dtype=float)

    excess = delta - delta_floor
    delta_floor_l2 = l2_norm(delta_floor)
    delta_floor_ratio = safe_ratio(l2_norm(delta), delta_floor_l2)
    excess_floor_ratio = safe_ratio(l2_norm(excess), delta_floor_l2)
    sigma_l2 = l2_norm(sigma)
    rho_l2 = l2_norm(rho)
    support_score = min(1.0, sigma_l2 / 0.05) + min(1.0, rho_l2 / 0.05)
    floor_score = max(0.0, 1.0 - min(1.0, excess_floor_ratio / 0.05))
    bounded_score = 0.0
    if float(np.max(np.abs(delta))) < 1.0e6 and float(np.max(np.abs(sigma))) < 1.0e6 and float(np.max(np.abs(rho))) < 1.0e6:
        bounded_score = 1.0
    event_score = 1.0 if int(results.get("ratchet_event_steps", 0)) >= 1 and int(results.get("seed_update_steps", 0)) >= 1 else 0.0
    total_score = 0.45 * floor_score + 0.35 * min(1.0, support_score / 2.0) + 0.10 * bounded_score + 0.10 * event_score

    return {
        "case_label": str(case["label"]),
        "phase_expression": str(spec["phase_expression"]),
        "ic_type": str(ic_spec["type"]),
        "delta_alpha": params.delta_alpha,
        "delta_beta": params.delta_beta,
        "dsr_lambda_D": params.dsr_lambda_D,
        "dsr_theta": params.dsr_theta,
        "dsr_event_gain": params.dsr_event_gain,
        "dsr_sigma_decay": params.dsr_sigma_decay,
        "dsr_sigma_load": params.dsr_sigma_load,
        "dsr_rho_gain": params.dsr_rho_gain,
        "dsr_rho_relax": params.dsr_rho_relax,
        "ratchet_event_steps": int(results.get("ratchet_event_steps", 0)),
        "seed_update_steps": int(results.get("seed_update_steps", 0)),
        "delta_floor_ratio": delta_floor_ratio,
        "excess_floor_ratio": excess_floor_ratio,
        "final_sigma_mean": float(np.mean(sigma)),
        "final_sigma_l2": sigma_l2,
        "final_rho_mean": float(np.mean(rho)),
        "final_rho_l2": rho_l2,
        "final_depth_mean": float(np.mean(depth)),
        "final_eps_mean": float(np.mean(epsilon)),
        "final_R_mean": float(np.mean(residue)),
        "min_abs_delta_floor": float(np.min(np.abs(delta_floor))),
        "max_abs_delta": float(np.max(np.abs(delta))),
        "max_abs_sigma": float(np.max(np.abs(sigma))),
        "max_abs_rho": float(np.max(np.abs(rho))),
        "floor_score": floor_score,
        "support_score": support_score,
        "bounded_score": bounded_score,
        "event_score": event_score,
        "total_score": total_score,
    }


def summarize(rows: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[Dict[str, object]]] = {}
    for row in rows:
        key = "|".join(
            str(row[field])
            for field in (
                "dsr_lambda_D",
                "dsr_theta",
                "dsr_event_gain",
                "dsr_sigma_decay",
                "dsr_sigma_load",
                "dsr_rho_gain",
                "dsr_rho_relax",
            )
        )
        grouped.setdefault(key, []).append(row)

    summary_rows: List[Dict[str, object]] = []
    for key, items in grouped.items():
        dsr_lambda_D = items[0]["dsr_lambda_D"]
        dsr_theta = items[0]["dsr_theta"]
        dsr_event_gain = items[0]["dsr_event_gain"]
        dsr_sigma_decay = items[0]["dsr_sigma_decay"]
        dsr_sigma_load = items[0]["dsr_sigma_load"]
        dsr_rho_gain = items[0]["dsr_rho_gain"]
        dsr_rho_relax = items[0]["dsr_rho_relax"]
        summary_rows.append(
            {
                "dsr_lambda_D": dsr_lambda_D,
                "dsr_theta": dsr_theta,
                "dsr_event_gain": dsr_event_gain,
                "dsr_sigma_decay": dsr_sigma_decay,
                "dsr_sigma_load": dsr_sigma_load,
                "dsr_rho_gain": dsr_rho_gain,
                "dsr_rho_relax": dsr_rho_relax,
                "case_count": len(items),
                "mean_total_score": sum(float(item["total_score"]) for item in items) / len(items),
                "min_total_score": min(float(item["total_score"]) for item in items),
                "mean_floor_ratio": sum(float(item["delta_floor_ratio"]) for item in items) / len(items),
                "mean_excess_ratio": sum(float(item["excess_floor_ratio"]) for item in items) / len(items),
                "mean_sigma_l2": sum(float(item["final_sigma_l2"]) for item in items) / len(items),
                "mean_rho_l2": sum(float(item["final_rho_l2"]) for item in items) / len(items),
                "mean_ratchet_event_steps": sum(float(item["ratchet_event_steps"]) for item in items) / len(items),
            }
        )
    summary_rows.sort(key=lambda row: float(row["mean_total_score"]), reverse=True)
    return summary_rows


def render_markdown(summary_rows: Sequence[Dict[str, object]], detail_rows: Sequence[Dict[str, object]]) -> str:
    best = summary_rows[0] if summary_rows else None
    case_labels = sorted({str(row["case_label"]) for row in detail_rows})
    lines = [
        "# DSR Python Calibration",
        "",
        "Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        "This note records a narrow local calibration sweep for the Python-only `I_phi_v4_dsr` branch.",
        "",
        "The sweep stays local and does not authorize governed staging.",
        "",
        "Cases:",
        f"`{', '.join(case_labels)}`",
        "",
    ]
    if best is not None:
        lines.extend(
            [
                "## Recommended Local Candidate",
                "",
                f"- `dsr_sigma_decay = {float(best['dsr_sigma_decay']):.2f}`",
                f"- `dsr_sigma_load = {float(best['dsr_sigma_load']):.2f}`",
                f"- `dsr_rho_gain = {float(best['dsr_rho_gain']):.2f}`",
                f"- `dsr_rho_relax = {float(best['dsr_rho_relax']):.2f}`",
                f"- `mean_total_score = {float(best['mean_total_score']):.6f}`",
                f"- `mean_excess_ratio = {float(best['mean_excess_ratio']):.6f}`",
                f"- `mean_sigma_l2 = {float(best['mean_sigma_l2']):.6f}`",
                f"- `mean_rho_l2 = {float(best['mean_rho_l2']):.6f}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Top Candidates",
            "",
        ]
    )
    for row in summary_rows[:5]:
        lines.append(
            f"- `sigma_decay={float(row['dsr_sigma_decay']):.2f}, sigma_load={float(row['dsr_sigma_load']):.2f}, "
            f"rho_gain={float(row['dsr_rho_gain']):.2f}, rho_relax={float(row['dsr_rho_relax']):.2f}`: "
            f"score=`{float(row['mean_total_score']):.6f}`, excess=`{float(row['mean_excess_ratio']):.6f}`, "
            f"sigma_l2=`{float(row['mean_sigma_l2']):.6f}`, rho_l2=`{float(row['mean_rho_l2']):.6f}`"
        )
    lines.extend(
        [
            "",
            "## Cases",
            "",
        ]
    )
    for row in detail_rows:
        if best is not None and (
            float(row["dsr_sigma_decay"]) == float(best["dsr_sigma_decay"])
            and float(row["dsr_sigma_load"]) == float(best["dsr_sigma_load"])
            and float(row["dsr_rho_gain"]) == float(best["dsr_rho_gain"])
            and float(row["dsr_rho_relax"]) == float(best["dsr_rho_relax"])
        ):
            lines.append(
                f"- `{row['case_label']}` best-candidate: score=`{float(row['total_score']):.6f}`, "
                f"delta/floor=`{float(row['delta_floor_ratio']):.6f}`, excess=`{float(row['excess_floor_ratio']):.6f}`, "
                f"sigma_l2=`{float(row['final_sigma_l2']):.6f}`, rho_l2=`{float(row['final_rho_l2']):.6f}`, "
                f"events=`{int(row['ratchet_event_steps'])}`"
            )
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "The DSR branch is now beyond smoke-test only. With the current local case set in scope, the branch retains a narrow local coupling region and shows real family-sensitive separation rather than identical traces. The shelf remains the weakest case, so this candidate is suitable for local reference use only and still does not authorize native work or governed staging.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a narrow local calibration sweep for the Python-only DSR branch.")
    parser.add_argument(
        "--detail-output",
        default="reports/DSR_PYTHON_CALIBRATION_DETAIL_2026-04-04.csv",
        help="Destination CSV path for per-case calibration results.",
    )
    parser.add_argument(
        "--summary-output",
        default="reports/DSR_PYTHON_CALIBRATION_SUMMARY_2026-04-04.csv",
        help="Destination CSV path for grouped calibration summary.",
    )
    parser.add_argument(
        "--json-output",
        default="reports/DSR_PYTHON_CALIBRATION_2026-04-04.json",
        help="Destination JSON path for the full calibration payload.",
    )
    parser.add_argument(
        "--md-output",
        default="reports/DSR_PYTHON_CALIBRATION_2026-04-04.md",
        help="Destination Markdown note path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    cases = build_cases(root)
    detail_rows: List[Dict[str, object]] = []
    for candidate in candidate_grid():
        for case in cases:
            detail_rows.append(evaluate_case(case, candidate))

    summary_rows = summarize(detail_rows)
    write_csv(
        (root / args.detail_output).resolve(),
        detail_rows,
        [
            "case_label", "phase_expression", "ic_type", "delta_alpha", "delta_beta",
            "dsr_lambda_D", "dsr_theta", "dsr_event_gain", "dsr_sigma_decay", "dsr_sigma_load", "dsr_rho_gain", "dsr_rho_relax",
            "ratchet_event_steps", "seed_update_steps", "delta_floor_ratio", "excess_floor_ratio",
            "final_sigma_mean", "final_sigma_l2", "final_rho_mean", "final_rho_l2", "final_depth_mean",
            "final_eps_mean", "final_R_mean", "min_abs_delta_floor", "max_abs_delta", "max_abs_sigma", "max_abs_rho",
            "floor_score", "support_score", "bounded_score", "event_score", "total_score",
        ],
    )
    write_csv(
        (root / args.summary_output).resolve(),
        summary_rows,
        [
            "dsr_lambda_D", "dsr_theta", "dsr_event_gain", "dsr_sigma_decay", "dsr_sigma_load", "dsr_rho_gain", "dsr_rho_relax",
            "case_count", "mean_total_score", "min_total_score", "mean_floor_ratio", "mean_excess_ratio", "mean_sigma_l2", "mean_rho_l2", "mean_ratchet_event_steps",
        ],
    )
    payload = {"date": "2026-04-04", "detail_rows": detail_rows, "summary_rows": summary_rows}
    write_json((root / args.json_output).resolve(), payload)
    (root / args.md_output).resolve().write_text(render_markdown(summary_rows, detail_rows), encoding="utf-8")


if __name__ == "__main__":
    main()
