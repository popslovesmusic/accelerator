from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from .batch_runner import expand_run_specs, summarise_run
from .initial_conditions import build_initial_condition
from .native_backend import is_native_backend_available
from .pde_solver import GridConfig, Parameters, simulate


SUMMARY_FIELDS = [
    "final_mean_eps",
    "final_mean_rho",
    "final_mean_R",
    "final_exclusion_fraction",
    "final_interface_count",
    "late_time_mean_front_speed",
    "late_time_mean_front_width",
    "late_time_mean_sharpness",
    "late_time_residue_asymmetry",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run fallback-Python parity checks against the staged native PDE reference.")
    parser.add_argument(
        "--config",
        nargs="+",
        required=True,
        help="One or more config JSON files. Absolute paths are recommended.",
    )
    parser.add_argument("--max-run-specs", type=int, default=1, help="Max expanded run specs per config.")
    parser.add_argument("--max-seeds", type=int, default=1, help="Max seeds per run spec.")
    parser.add_argument("--max-ics", type=int, default=1, help="Max initial conditions per run spec.")
    parser.add_argument("--t-final", type=float, help="Optional override to shorten parity runs.")
    parser.add_argument("--save-every", type=int, help="Optional save cadence override.")
    parser.add_argument("--state-atol", type=float, default=1.0e-10, help="Absolute tolerance for state arrays.")
    parser.add_argument("--summary-atol", type=float, default=1.0e-9, help="Absolute tolerance for summary scalars.")
    parser.add_argument("--output-json", help="Optional path for a JSON parity report.")
    return parser.parse_args()


def load_task_specs(args: argparse.Namespace) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for config_name in args.config:
        expanded = expand_run_specs(config_name)
        for spec in expanded[: max(0, args.max_run_specs)]:
            grid_spec = dict(spec["grid"])
            if args.t_final is not None:
                grid_spec["t_final"] = args.t_final
            if args.save_every is not None:
                grid_spec["save_every"] = args.save_every

            seeds = list(spec.get("seeds", []))[: max(0, args.max_seeds)]
            initial_conditions = list(spec.get("initial_conditions", []))[: max(0, args.max_ics)]
            for seed in seeds:
                for ic_index, ic_spec in enumerate(initial_conditions):
                    tasks.append(
                        {
                            "config_name": config_name,
                            "spec_label": str(spec.get("label", "")),
                            "sim_id": str(spec.get("sim_id", "")),
                            "phase_expression": str(spec.get("phase_expression", "")),
                            "grid_spec": grid_spec,
                            "parameters": dict(spec["parameters"]),
                            "seed": int(seed),
                            "ic_index": ic_index,
                            "ic_spec": dict(ic_spec),
                        }
                    )
    return tasks


def max_abs_diff(lhs: np.ndarray, rhs: np.ndarray) -> float:
    if lhs.size == 0 and rhs.size == 0:
        return 0.0
    return float(np.max(np.abs(lhs - rhs)))


def compare_results(
    *,
    python_result: dict[str, Any],
    native_result: dict[str, Any],
    state_atol: float,
    summary_atol: float,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "times_match": False,
        "x_match": False,
        "blew_up_match": bool(python_result["blew_up"]) == bool(native_result["blew_up"]),
        "negative_undershoot_match": int(python_result["negative_undershoot_events"]) == int(native_result["negative_undershoot_events"]),
        "snapshot_count_match": len(python_result["snapshots"]) == len(native_result["snapshots"]),
        "state_max_abs_diff": {"epsilon": 0.0, "rho": 0.0, "residue": 0.0},
        "classification_match": False,
        "classification_reference": "",
        "classification_fallback": "",
        "summary_abs_diff": {},
        "summary_within_tolerance": True,
    }

    python_times = np.asarray(python_result["times"], dtype=float)
    native_times = np.asarray(native_result["times"], dtype=float)
    if python_times.shape == native_times.shape:
        result["times_match"] = bool(np.allclose(python_times, native_times, rtol=0.0, atol=1.0e-12))

    python_x = np.asarray(python_result["x"], dtype=float)
    native_x = np.asarray(native_result["x"], dtype=float)
    if python_x.shape == native_x.shape:
        result["x_match"] = bool(np.allclose(python_x, native_x, rtol=0.0, atol=1.0e-12))

    for field in ["epsilon", "rho", "residue"]:
        worst = 0.0
        for python_snapshot, native_snapshot in zip(python_result["snapshots"], native_result["snapshots"]):
            lhs = np.asarray(python_snapshot[field], dtype=float)
            rhs = np.asarray(native_snapshot[field], dtype=float)
            if lhs.shape != rhs.shape:
                worst = float("inf")
                break
            worst = max(worst, max_abs_diff(lhs, rhs))
        result["state_max_abs_diff"][field] = worst

    reference_summary = summarise_run(
        "native_reference",
        native_result["params"],
        native_result["raw_result"],
        write_profiles=False,
    )
    fallback_summary = summarise_run(
        "python_fallback",
        python_result["params"],
        python_result["raw_result"],
        write_profiles=False,
    )

    result["classification_reference"] = str(reference_summary["classification"])
    result["classification_fallback"] = str(fallback_summary["classification"])
    result["classification_match"] = result["classification_reference"] == result["classification_fallback"]

    for field in SUMMARY_FIELDS:
        lhs = float(reference_summary["summary"][field])
        rhs = float(fallback_summary["summary"][field])
        diff = abs(lhs - rhs)
        result["summary_abs_diff"][field] = diff
        if diff > summary_atol:
            result["summary_within_tolerance"] = False

    result["state_within_tolerance"] = all(
        float(value) <= state_atol for value in result["state_max_abs_diff"].values()
    )
    result["passed"] = all(
        [
            result["times_match"],
            result["x_match"],
            result["blew_up_match"],
            result["negative_undershoot_match"],
            result["snapshot_count_match"],
            result["state_within_tolerance"],
            result["classification_match"],
            result["summary_within_tolerance"],
        ]
    )
    return result


def execute_task(task: dict[str, Any], *, state_atol: float, summary_atol: float) -> dict[str, Any]:
    grid = GridConfig(**task["grid_spec"])
    params = Parameters(**task["parameters"])
    initial_state = build_initial_condition(grid, task["ic_spec"], task["seed"])

    python_raw = simulate(params, grid, initial_state, backend="python")
    native_raw = simulate(params, grid, initial_state, backend="native")
    comparison = compare_results(
        python_result={"raw_result": python_raw, "params": params, **python_raw},
        native_result={"raw_result": native_raw, "params": params, **native_raw},
        state_atol=state_atol,
        summary_atol=summary_atol,
    )

    return {
        "config_name": task["config_name"],
        "sim_id": task["sim_id"],
        "spec_label": task["spec_label"],
        "phase_expression": task["phase_expression"],
        "seed": task["seed"],
        "ic_index": task["ic_index"],
        "ic_type": task["ic_spec"]["type"],
        "grid": asdict(grid),
        "parameters": asdict(params),
        **comparison,
    }


def main() -> None:
    args = parse_args()
    if not is_native_backend_available():
        raise RuntimeError("Native backend is not available. Rebuild _level2_native before running parity checks.")

    tasks = load_task_specs(args)
    if not tasks:
        raise RuntimeError("No parity tasks were selected. Check the configs or max-* limits.")

    cases = [execute_task(task, state_atol=args.state_atol, summary_atol=args.summary_atol) for task in tasks]
    passed_count = sum(1 for case in cases if case["passed"])

    report = {
        "native_available": True,
        "reference_backend": "native",
        "fallback_backend": "python",
        "case_count": len(cases),
        "passed_count": passed_count,
        "failed_count": len(cases) - passed_count,
        "state_atol": args.state_atol,
        "summary_atol": args.summary_atol,
        "cases": cases,
    }

    if args.output_json:
        output_path = Path(args.output_json).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Native reference parity: {passed_count}/{len(cases)} cases passed")
    for case in cases:
        status = "PASS" if case["passed"] else "FAIL"
        print(
            f"[{status}] sim={case['sim_id']} label={case['spec_label']} seed={case['seed']} "
            f"ic={case['ic_type']} class={case['classification_reference']}/{case['classification_fallback']} "
            f"state_diff=max({case['state_max_abs_diff']['epsilon']:.3e}, {case['state_max_abs_diff']['rho']:.3e}, {case['state_max_abs_diff']['residue']:.3e})"
        )


if __name__ == "__main__":
    main()
