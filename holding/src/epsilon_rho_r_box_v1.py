from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


EPSILON = 1.0e-12


@dataclass
class GridConfig:
    nx: int = 256
    length: float = 1.0
    dt: float = 1.0e-4
    t_final: float = 2.0
    save_every: int = 100

    @property
    def dx(self) -> float:
        return self.length / self.nx

    @property
    def n_steps(self) -> int:
        return int(round(self.t_final / self.dt))


@dataclass
class ModelConfig:
    D_epsilon: float = 6.0e-4
    D_rho: float = 4.0e-4
    D_R: float = 2.0e-4
    a: float = 0.60
    b: float = 1.20
    c: float = 2.00
    alpha: float = 0.70
    beta: float = 0.80
    gamma: float = 1.20
    u: float = 0.15
    v: float = 0.08
    kappa: float = 0.60
    lambda_R: float = 0.80
    s: float = 0.01
    h: float = 0.08
    clamp_nonnegative: bool = True
    epsilon_activity_threshold: float = 0.05


@dataclass
class InitialConditionConfig:
    epsilon_kind: str = "gaussian_bump"
    epsilon_base: float = 0.0
    epsilon_amplitude: float = 0.32
    epsilon_sigma: float = 0.08
    epsilon_offset: float = 0.0
    rho_kind: str = "uniform"
    rho_base: float = 0.25
    rho_amplitude: float = 0.03
    rho_sigma: float = 0.14
    rho_offset: float = 0.0
    residue_kind: str = "zero"
    residue_base: float = 0.0
    residue_amplitude: float = 0.0
    residue_sigma: float = 0.10
    residue_offset: float = 0.0
    noise_std: float = 0.0
    seed: int = 1000


@dataclass
class BoxConfig:
    epsilon_max: float = 0.45
    rho_min: float = 0.0
    rho_max: float = 0.75
    residue_max: float = 0.38


@dataclass
class RunConfig:
    grid: GridConfig
    model: ModelConfig
    initial_condition: InitialConditionConfig
    box: BoxConfig
    output_dir: str


def _parse_dataclass(cls: type, values: dict[str, Any] | None) -> Any:
    return cls(**dict(values or {}))


def load_run_config(path: Path) -> RunConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return RunConfig(
        grid=_parse_dataclass(GridConfig, payload.get("grid")),
        model=_parse_dataclass(ModelConfig, payload.get("model")),
        initial_condition=_parse_dataclass(InitialConditionConfig, payload.get("initial_condition")),
        box=_parse_dataclass(BoxConfig, payload.get("box")),
        output_dir=str(payload.get("output_dir", "kept_results/current/outputs/epsilon_rho_r_box_v1")),
    )


def laplacian_neumann_1d(field: np.ndarray, dx: float) -> np.ndarray:
    padded = np.pad(field, (1, 1), mode="edge")
    return (padded[:-2] - 2.0 * field + padded[2:]) / (dx * dx)


def make_coordinate_grid(grid: GridConfig) -> np.ndarray:
    return np.linspace(-0.5 * grid.length, 0.5 * grid.length, grid.nx, endpoint=False)


def build_field(
    grid: GridConfig,
    kind: str,
    base: float,
    amplitude: float,
    sigma: float,
    offset: float,
    rng: np.random.Generator | None,
    noise_std: float,
) -> np.ndarray:
    xx = make_coordinate_grid(grid)
    if kind == "zero":
        field = np.zeros(grid.nx, dtype=float)
    elif kind == "uniform":
        field = np.full(grid.nx, base, dtype=float)
    elif kind == "gaussian_bump":
        radius_sq = np.square(xx - offset)
        field = base + amplitude * np.exp(-0.5 * radius_sq / max(sigma * sigma, EPSILON))
    else:
        raise ValueError(f"Unsupported field kind: {kind}")
    if noise_std > 0.0 and rng is not None:
        field = field + rng.normal(scale=noise_std, size=field.shape)
    return field.astype(float, copy=False)


def validate_run_config(config: RunConfig) -> None:
    model = config.model
    box = config.box
    if config.grid.nx < 8:
        raise ValueError("nx must be at least 8")
    if config.grid.dt <= 0.0 or config.grid.t_final <= 0.0:
        raise ValueError("dt and t_final must be positive")
    if config.grid.save_every < 1:
        raise ValueError("save_every must be >= 1")
    if model.D_epsilon < 0.0 or model.D_rho < 0.0 or model.D_R < 0.0:
        raise ValueError("diffusion coefficients must be nonnegative")
    if model.c <= 0.0 or model.gamma <= 0.0 or model.kappa <= 0.0 or model.lambda_R <= 0.0:
        raise ValueError("c, gamma, kappa, and lambda_R must be positive")
    if box.epsilon_max <= 0.0 or box.rho_max <= box.rho_min or box.residue_max < 0.0:
        raise ValueError("box bounds must be ordered and nonnegative")
    if model.epsilon_activity_threshold < 0.0:
        raise ValueError("epsilon_activity_threshold must be nonnegative")


def derive_box_thresholds(model: ModelConfig, box: BoxConfig) -> dict[str, float | bool]:
    A = model.a + model.u * model.kappa / model.lambda_R
    discriminant = A * A + 4.0 * model.c * model.s
    epsilon_critical = (A + np.sqrt(max(discriminant, 0.0))) / (2.0 * model.c)
    easy_regime_limit = np.inf
    if model.v > 0.0 and model.kappa > 0.0:
        easy_regime_limit = model.h * model.lambda_R / (model.v * model.kappa)
    epsilon_face_margin = -(model.a * box.epsilon_max - model.c * box.epsilon_max * box.epsilon_max + model.u * box.residue_max + model.s)
    rho_upper_face_margin = -(model.alpha * box.rho_max - model.gamma * box.rho_max * box.rho_max + model.h)
    residue_face_margin = box.residue_max - (model.kappa / model.lambda_R) * box.epsilon_max
    support_floor_margin = (
        -model.gamma * box.rho_min * box.rho_min
        + (model.alpha - model.beta * box.epsilon_max) * box.rho_min
        + (model.h - model.v * box.residue_max)
    )
    easy_regime_margin = model.h - model.v * box.residue_max
    shifted_floor_gain_margin = model.alpha - model.beta * box.epsilon_max
    shifted_floor_discriminant = shifted_floor_gain_margin * shifted_floor_gain_margin + 4.0 * model.gamma * (
        model.h - model.v * box.residue_max
    )
    shifted_floor_feasible = shifted_floor_gain_margin > 0.0 and shifted_floor_discriminant >= 0.0 and support_floor_margin >= 0.0
    easy_regime_feasible = easy_regime_margin >= 0.0
    box_admissible = (
        epsilon_face_margin >= 0.0
        and rho_upper_face_margin >= 0.0
        and residue_face_margin >= 0.0
        and (easy_regime_feasible or shifted_floor_feasible)
    )
    return {
        "A": float(A),
        "epsilon_critical": float(epsilon_critical),
        "epsilon_threshold_gap": float(box.epsilon_max - epsilon_critical),
        "easy_regime_limit": float(easy_regime_limit),
        "epsilon_face_margin": float(epsilon_face_margin),
        "rho_upper_face_margin": float(rho_upper_face_margin),
        "residue_face_margin": float(residue_face_margin),
        "support_floor_margin": float(support_floor_margin),
        "easy_regime_margin": float(easy_regime_margin),
        "shifted_floor_gain_margin": float(shifted_floor_gain_margin),
        "shifted_floor_discriminant": float(shifted_floor_discriminant),
        "easy_regime_feasible": bool(easy_regime_feasible),
        "shifted_floor_feasible": bool(shifted_floor_feasible),
        "box_admissible": bool(box_admissible),
    }


def summarize_state(
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
    box: BoxConfig,
    model: ModelConfig,
) -> dict[str, float | bool | str]:
    epsilon_max = float(np.max(epsilon))
    rho_min = float(np.min(rho))
    rho_max = float(np.max(rho))
    residue_max = float(np.max(residue))
    box_epsilon_margin = box.epsilon_max - epsilon_max
    box_rho_lower_margin = rho_min - box.rho_min
    box_rho_upper_margin = box.rho_max - rho_max
    box_residue_margin = box.residue_max - residue_max
    live_support_floor_margin = (
        -model.gamma * box.rho_min * box.rho_min
        + (model.alpha - model.beta * epsilon_max) * box.rho_min
        + (model.h - model.v * residue_max)
    )
    live_easy_regime_margin = model.h - model.v * residue_max
    box_margins = {
        "epsilon": box_epsilon_margin,
        "rho_lower": box_rho_lower_margin,
        "rho_upper": box_rho_upper_margin,
        "residue": box_residue_margin,
    }
    violation_face = min(box_margins, key=box_margins.get)
    return {
        "epsilon_mean": float(np.mean(epsilon)),
        "epsilon_max": epsilon_max,
        "rho_mean": float(np.mean(rho)),
        "rho_min": rho_min,
        "rho_max": rho_max,
        "residue_mean": float(np.mean(residue)),
        "residue_max": residue_max,
        "epsilon_active_fraction": float(np.mean(epsilon >= model.epsilon_activity_threshold)),
        "box_epsilon_margin": float(box_epsilon_margin),
        "box_rho_lower_margin": float(box_rho_lower_margin),
        "box_rho_upper_margin": float(box_rho_upper_margin),
        "box_residue_margin": float(box_residue_margin),
        "live_support_floor_margin": float(live_support_floor_margin),
        "live_easy_regime_margin": float(live_easy_regime_margin),
        "within_box": bool(min(box_margins.values()) >= -1.0e-9),
        "worst_box_face": str(violation_face),
        "worst_box_margin": float(box_margins[violation_face]),
    }


def step_fields(
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
    grid: GridConfig,
    model: ModelConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    epsilon_rhs = (
        model.D_epsilon * laplacian_neumann_1d(epsilon, grid.dx)
        + model.a * epsilon
        - model.b * epsilon * rho
        - model.c * epsilon * epsilon
        + model.u * residue
        + model.s
    )
    rho_rhs = (
        model.D_rho * laplacian_neumann_1d(rho, grid.dx)
        + model.alpha * rho
        - model.beta * epsilon * rho
        - model.gamma * rho * rho
        - model.v * residue
        + model.h
    )
    residue_rhs = (
        model.D_R * laplacian_neumann_1d(residue, grid.dx)
        + model.kappa * epsilon
        - model.lambda_R * residue
    )
    next_epsilon = epsilon + grid.dt * epsilon_rhs
    next_rho = rho + grid.dt * rho_rhs
    next_residue = residue + grid.dt * residue_rhs
    if model.clamp_nonnegative:
        next_epsilon = np.maximum(next_epsilon, 0.0)
        next_rho = np.maximum(next_rho, 0.0)
        next_residue = np.maximum(next_residue, 0.0)
    return next_epsilon, next_rho, next_residue


def simulate(config: RunConfig) -> dict[str, Any]:
    validate_run_config(config)
    rng = np.random.default_rng(config.initial_condition.seed)
    epsilon = build_field(
        config.grid,
        config.initial_condition.epsilon_kind,
        config.initial_condition.epsilon_base,
        config.initial_condition.epsilon_amplitude,
        config.initial_condition.epsilon_sigma,
        config.initial_condition.epsilon_offset,
        rng,
        config.initial_condition.noise_std,
    )
    rho = build_field(
        config.grid,
        config.initial_condition.rho_kind,
        config.initial_condition.rho_base,
        config.initial_condition.rho_amplitude,
        config.initial_condition.rho_sigma,
        config.initial_condition.rho_offset,
        rng,
        0.0,
    )
    residue = build_field(
        config.grid,
        config.initial_condition.residue_kind,
        config.initial_condition.residue_base,
        config.initial_condition.residue_amplitude,
        config.initial_condition.residue_sigma,
        config.initial_condition.residue_offset,
        rng,
        0.0,
    )
    if config.model.clamp_nonnegative:
        epsilon = np.maximum(epsilon, 0.0)
        rho = np.maximum(rho, 0.0)
        residue = np.maximum(residue, 0.0)

    box_analysis = derive_box_thresholds(config.model, config.box)
    times: list[float] = []
    diagnostics: list[dict[str, Any]] = []
    epsilon_snapshots: list[np.ndarray] = []
    rho_snapshots: list[np.ndarray] = []
    residue_snapshots: list[np.ndarray] = []
    first_box_violation: dict[str, Any] | None = None

    for step in range(config.grid.n_steps + 1):
        if step % config.grid.save_every == 0 or step == config.grid.n_steps:
            current_time = step * config.grid.dt
            diag = summarize_state(epsilon, rho, residue, config.box, config.model)
            times.append(current_time)
            diagnostics.append(diag)
            epsilon_snapshots.append(epsilon.copy())
            rho_snapshots.append(rho.copy())
            residue_snapshots.append(residue.copy())
            if first_box_violation is None and not bool(diag["within_box"]):
                first_box_violation = {
                    "time": float(current_time),
                    "step": int(step),
                    "face": str(diag["worst_box_face"]),
                    "margin": float(diag["worst_box_margin"]),
                }
        if step == config.grid.n_steps:
            break
        epsilon, rho, residue = step_fields(epsilon, rho, residue, config.grid, config.model)

    return {
        "config": {
            "grid": asdict(config.grid),
            "model": asdict(config.model),
            "initial_condition": asdict(config.initial_condition),
            "box": asdict(config.box),
            "output_dir": config.output_dir,
        },
        "times": np.array(times, dtype=float),
        "x": make_coordinate_grid(config.grid),
        "diagnostics": diagnostics,
        "epsilon_snapshots": np.stack(epsilon_snapshots, axis=0),
        "rho_snapshots": np.stack(rho_snapshots, axis=0),
        "residue_snapshots": np.stack(residue_snapshots, axis=0),
        "box_analysis": box_analysis,
        "first_box_violation": first_box_violation,
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "diagnostics.json").write_text(json.dumps(result["diagnostics"], indent=2), encoding="utf-8")
    np.savez_compressed(
        output_dir / "snapshots.npz",
        times=result["times"],
        x=result["x"],
        epsilon_snapshots=result["epsilon_snapshots"],
        rho_snapshots=result["rho_snapshots"],
        residue_snapshots=result["residue_snapshots"],
    )
    summary = {
        "config": result["config"],
        "box_analysis": result["box_analysis"],
        "first_box_violation": result["first_box_violation"],
        "final": dict(result["diagnostics"][-1], saved_steps=len(result["diagnostics"])),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="epsilon-rho-R invariant-box scaffold")
    parser.add_argument("--config", required=True, help="Path to JSON config")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    run_config = load_run_config(config_path)
    result = simulate(run_config)
    output_dir = Path(run_config.output_dir)
    if not output_dir.is_absolute():
        output_dir = (config_path.parent / output_dir).resolve()
    write_outputs(result, output_dir)


if __name__ == "__main__":
    main()
