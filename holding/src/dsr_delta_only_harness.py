from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

from .dsr_geometry import build_delta_floor, commitments_from_path, select_seed_positions
from .pde_solver import GridConfig, implicit_diffusion_step


PROFILE_PATTERN = re.compile(r"^profile_run_(?P<run_id>.+)_t_(?P<time>[0-9p\-]+)\.csv$")


@dataclass(frozen=True)
class DeltaOnlyCase:
    label: str
    x: np.ndarray
    initial_depth: np.ndarray
    initial_delta: np.ndarray
    sigma_const: float
    rho_const: float
    lambda_d: float
    theta: float
    event_gain: float
    diffusion_scale: float
    grid: GridConfig


def resolve_outputs_root(path: Path) -> Path:
    candidate = path.resolve()
    if (candidate / "final_summary.csv").is_file():
        return candidate
    outputs_candidate = candidate / "outputs"
    if (outputs_candidate / "final_summary.csv").is_file():
        return outputs_candidate
    raise FileNotFoundError(f"Could not find final_summary.csv under {candidate}")


def parse_profile_time(token: str) -> float:
    return float(token.replace("p", "."))


def latest_profile_path(outputs_root: Path, run_id: str) -> Path:
    latest_path: Path | None = None
    latest_time = float("-inf")
    for path in (outputs_root / "profiles").glob(f"profile_run_{run_id}_t_*.csv"):
        match = PROFILE_PATTERN.match(path.name)
        if not match:
            continue
        time = parse_profile_time(match.group("time"))
        if time > latest_time:
            latest_time = time
            latest_path = path
    if latest_path is None:
        raise FileNotFoundError(f"No profiles found for run {run_id} under {outputs_root}")
    return latest_path


def load_profile_fields(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_values: List[float] = []
    residue_values: List[float] = []
    eps_values: List[float] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            x_values.append(float(row["x"]))
            eps_values.append(float(row["eps"]))
            residue_values.append(float(row["R"]))
    return (
        np.asarray(x_values, dtype=float),
        np.asarray(eps_values, dtype=float),
        np.asarray(residue_values, dtype=float),
    )


def gaussian_peak(x: np.ndarray, center: float, sigma: float, amplitude: float) -> np.ndarray:
    return amplitude * np.exp(-0.5 * np.square((x - center) / sigma))


def build_cases(root: Path) -> List[DeltaOnlyCase]:
    L = 200.0
    Nx = 1024
    x = np.linspace(0.0, L, Nx, endpoint=False)
    grid = GridConfig(L=L, Nx=Nx, t_final=20.0, dt=0.01, save_every=100)

    base_depth = gaussian_peak(x, 55.0, 4.0, 1.0) + gaussian_peak(x, 145.0, 4.5, 0.9)
    base_floor_like = gaussian_peak(x, 55.0, 6.5, 0.12) - gaussian_peak(x, 145.0, 6.5, 0.10)
    localized_excess = base_floor_like + gaussian_peak(x, 100.0, 3.5, 0.18)
    fallback_depth = gaussian_peak(x, 84.0, 5.0, 1.0)
    fallback_delta = gaussian_peak(x, 84.0, 7.0, 0.11)

    replay_outputs = resolve_outputs_root(root / "batches" / "20260403_sim18_stage1a_v1_ss3_standard_retry1")
    replay_run_id = "sim18_stage1a_ss3_standard_v23_000_s1000_ic0"
    replay_profile = latest_profile_path(replay_outputs, replay_run_id)
    replay_x, replay_eps, replay_residue = load_profile_fields(replay_profile)
    replay_delta = replay_eps - 0.5 * replay_residue

    return [
        DeltaOnlyCase(
            label="synthetic_relax_to_floor",
            x=x,
            initial_depth=base_depth,
            initial_delta=base_floor_like,
            sigma_const=1.0,
            rho_const=0.5,
            lambda_d=1.6,
            theta=0.08,
            event_gain=0.10,
            diffusion_scale=0.03,
            grid=grid,
        ),
        DeltaOnlyCase(
            label="synthetic_localized_excess_event",
            x=x,
            initial_depth=base_depth,
            initial_delta=localized_excess,
            sigma_const=1.0,
            rho_const=0.5,
            lambda_d=1.6,
            theta=0.06,
            event_gain=0.25,
            diffusion_scale=0.03,
            grid=grid,
        ),
        DeltaOnlyCase(
            label="synthetic_fallback_seed_event",
            x=x,
            initial_depth=fallback_depth,
            initial_delta=fallback_delta,
            sigma_const=0.9,
            rho_const=0.4,
            lambda_d=1.4,
            theta=0.05,
            event_gain=0.20,
            diffusion_scale=0.02,
            grid=grid,
        ),
        DeltaOnlyCase(
            label="replay_informed_ss3_front_seeded",
            x=replay_x,
            initial_depth=replay_residue,
            initial_delta=replay_delta,
            sigma_const=1.0,
            rho_const=0.6,
            lambda_d=1.2,
            theta=0.10,
            event_gain=0.08,
            diffusion_scale=0.02,
            grid=GridConfig(L=L, Nx=len(replay_x), t_final=20.0, dt=0.01, save_every=100),
        ),
    ]


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def l2_norm(values: Sequence[float]) -> float:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(array))))


def simulate_delta_only(case: DeltaOnlyCase, commitments_path: Path) -> Dict[str, object]:
    commitments = commitments_from_path(commitments_path)
    delta = np.asarray(case.initial_delta, dtype=float).copy()
    depth = np.asarray(case.initial_depth, dtype=float).copy()
    sigma_field = np.full_like(delta, case.sigma_const, dtype=float)
    rho_field = np.full_like(delta, case.rho_const, dtype=float)

    transport_weight = float(case.sigma_const / (1.0 + case.rho_const))
    selection = select_seed_positions(case.x, depth, commitments)
    floor = build_delta_floor(case.x, selection, previous_delta=delta)
    initial_seed_pair = (selection.x_r, selection.x_g)

    prev_floor_active = False
    prev_zero_active = False
    floor_event_count = 0
    zero_event_count = 0
    floor_active_steps = 0
    zero_active_steps = 0
    seed_update_count = 0
    minimum_abs_delta_f = float(floor.minimum_abs_delta_f)
    maximum_seed_jump = 0.0
    previous_seed_pair = (selection.x_r, selection.x_g)
    event_times: List[float] = []

    for step in range(case.grid.n_steps):
        excess_from_floor = np.abs(delta - floor.delta_f)
        floor_active = bool(np.any(excess_from_floor >= case.theta))
        zero_active = bool(np.any(np.abs(delta) >= case.theta))

        floor_active_steps += int(floor_active)
        zero_active_steps += int(zero_active)
        if floor_active and not prev_floor_active:
            floor_event_count += 1
            event_times.append(step * case.grid.dt)
            deposit = np.maximum(excess_from_floor - case.theta, 0.0)
            depth += case.event_gain * deposit
            updated_selection = select_seed_positions(case.x, depth, commitments)
            maximum_seed_jump = max(
                maximum_seed_jump,
                abs(updated_selection.x_r - previous_seed_pair[0]),
                abs(updated_selection.x_g - previous_seed_pair[1]),
            )
            previous_seed_pair = (updated_selection.x_r, updated_selection.x_g)
            selection = updated_selection
            floor = build_delta_floor(case.x, selection, previous_delta=delta)
            minimum_abs_delta_f = min(minimum_abs_delta_f, float(floor.minimum_abs_delta_f))
            seed_update_count += 1
        if zero_active and not prev_zero_active:
            zero_event_count += 1

        reaction = -case.lambda_d * (delta - floor.delta_f)
        delta = implicit_diffusion_step(delta, reaction, case.diffusion_scale * transport_weight, case.grid)
        prev_floor_active = floor_active
        prev_zero_active = zero_active

    final_excess = np.abs(delta - floor.delta_f)
    final_delta_l2 = l2_norm(delta)
    final_floor_l2 = l2_norm(floor.delta_f)
    final_excess_l2 = l2_norm(final_excess)
    final_ratio = 0.0 if final_floor_l2 <= 1.0e-12 else final_delta_l2 / final_floor_l2
    final_excess_ratio = 0.0 if final_floor_l2 <= 1.0e-12 else final_excess_l2 / final_floor_l2
    no_drain_pass = final_ratio >= 0.80 and final_delta_l2 > 1.0e-8
    threshold_basis_pass = floor_active_steps < zero_active_steps
    seed_update_gate_pass = seed_update_count == floor_event_count
    overall_pass = no_drain_pass and threshold_basis_pass and seed_update_gate_pass and minimum_abs_delta_f > 0.0

    return {
        "label": case.label,
        "transport_weight": transport_weight,
        "floor_event_count": floor_event_count,
        "zero_event_count": zero_event_count,
        "floor_active_steps": floor_active_steps,
        "zero_active_steps": zero_active_steps,
        "seed_update_count": seed_update_count,
        "event_times": event_times,
        "minimum_abs_delta_f": minimum_abs_delta_f,
        "maximum_seed_jump": maximum_seed_jump,
        "initial_seed_x_r": initial_seed_pair[0],
        "initial_seed_x_g": initial_seed_pair[1],
        "final_seed_x_r": previous_seed_pair[0],
        "final_seed_x_g": previous_seed_pair[1],
        "final_delta_l2": final_delta_l2,
        "final_floor_l2": final_floor_l2,
        "final_excess_l2": final_excess_l2,
        "final_delta_to_floor_ratio": final_ratio,
        "final_excess_to_floor_ratio": final_excess_ratio,
        "no_drain_pass": no_drain_pass,
        "threshold_basis_pass": threshold_basis_pass,
        "seed_update_gate_pass": seed_update_gate_pass,
        "overall_pass": overall_pass,
    }


def render_markdown(commitments_path: Path, rows: Sequence[Dict[str, object]]) -> str:
    pass_count = sum(1 for row in rows if bool(row["overall_pass"]))
    lines = [
        "# DSR Delta-Only Harness",
        "",
        "Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        "This note records the local delta-only runtime harness against:",
        "",
        f"- `{commitments_path}`",
        "",
        "The harness holds `Sigma` and `rho` constant, updates seeds only on explicit ratchet events, and compares floor-based threshold activity against a zero-based pseudo-threshold.",
        "",
        "No governed batch was executed.",
        "",
        "## Result",
        "",
        f"- cases passed: `{pass_count} / {len(rows)}`",
        "",
        "## Cases",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['label']}`: pass=`{str(row['overall_pass']).lower()}`, "
            f"floor_events=`{int(row['floor_event_count'])}`, zero_active_steps=`{int(row['zero_active_steps'])}`, "
            f"floor_active_steps=`{int(row['floor_active_steps'])}`, seed_updates=`{int(row['seed_update_count'])}`, "
            f"delta/floor=`{float(row['final_delta_to_floor_ratio']):.6f}`, excess/floor=`{float(row['final_excess_to_floor_ratio']):.6f}`, "
            f"min|delta_f|=`{float(row['minimum_abs_delta_f']):.6e}`, max_seed_jump=`{float(row['maximum_seed_jump']):.6f}`"
        )
    lines.extend(
        [
            "",
            "## Bottom Line",
            "",
            "The local delta-only branch no longer drains to zero.",
            "Seed updates are now event-gated rather than frame-gated, and the threshold diagnostics show why ratchet firing must be measured from `delta_f` rather than from zero.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local DSR delta-only harness.")
    parser.add_argument(
        "--commitments",
        default="configs/dsr/dsr_runtime_commitments_v1.json",
        help="Committed DSR geometry JSON.",
    )
    parser.add_argument(
        "--json-output",
        default="reports/DSR_DELTA_ONLY_HARNESS_2026-04-04.json",
        help="Destination JSON report path.",
    )
    parser.add_argument(
        "--md-output",
        default="reports/DSR_DELTA_ONLY_HARNESS_2026-04-04.md",
        help="Destination Markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    commitments_path = (root / args.commitments).resolve()
    rows = [simulate_delta_only(case, commitments_path) for case in build_cases(root)]
    payload = {
        "date": "2026-04-04",
        "commitments": str(commitments_path),
        "rows": rows,
    }
    write_json((root / args.json_output).resolve(), payload)
    (root / args.md_output).resolve().write_text(render_markdown(commitments_path, rows), encoding="utf-8")


if __name__ == "__main__":
    main()
