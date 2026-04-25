from __future__ import annotations

from typing import Dict

import numpy as np

from .pde_solver import GridConfig


def smooth_step(x: np.ndarray, center: float, width: float) -> np.ndarray:
    width = max(width, 1.0e-6)
    return 0.5 * (1.0 + np.tanh((x - center) / width))


def front_seeded(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    del seed
    x = grid.x
    transition = smooth_step(x, 0.5 * grid.L, spec.get("smoothing_width", 5.0))
    epsilon = spec["eps_left"] * (1.0 - transition) + spec["eps_right"] * transition
    rho = spec["rho_left"] * (1.0 - transition) + spec["rho_right"] * transition
    residue = np.full_like(x, spec.get("R_init", 0.0), dtype=float)
    return {"epsilon": epsilon, "rho": rho, "residue": residue}


def front_seeded_noise(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    base = front_seeded(grid, spec, seed)
    noise_amp = float(spec.get("noise_amp", 0.01))
    epsilon = np.maximum(base["epsilon"] + noise_amp * rng.standard_normal(grid.Nx), 0.0)
    rho = np.maximum(base["rho"] + noise_amp * rng.standard_normal(grid.Nx), 0.0)
    return {"epsilon": epsilon, "rho": rho, "residue": base["residue"]}


def near_uniform_noise(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = grid.x
    epsilon = np.full_like(x, spec.get("eps0", 0.8), dtype=float)
    rho = np.full_like(x, spec.get("rho0", 0.8), dtype=float)
    residue = np.full_like(x, spec.get("R0", 0.0), dtype=float)
    noise_amp = spec.get("noise_amp", 0.02)
    epsilon = np.maximum(epsilon + noise_amp * rng.standard_normal(grid.Nx), 0.0)
    rho = np.maximum(rho + noise_amp * rng.standard_normal(grid.Nx), 0.0)
    return {"epsilon": epsilon, "rho": rho, "residue": residue}


def localized_seed(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    del seed
    x = grid.x
    epsilon = np.full_like(x, spec.get("eps_bg", 0.2), dtype=float)
    rho = np.full_like(x, spec.get("rho_bg", 1.0), dtype=float)
    residue = np.zeros_like(x, dtype=float)
    center = spec.get("seed_center", 0.5 * grid.L)
    sigma = max(spec.get("seed_sigma", 6.0), 1.0e-6)
    epsilon += spec.get("eps_seed_amp", 0.8) * np.exp(-0.5 * ((x - center) / sigma) ** 2)
    return {"epsilon": epsilon, "rho": rho, "residue": residue}


def ontology_gaussian_noise(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    x = grid.x
    amplitude = spec.get("A0", 0.45)
    sigma0 = max(spec.get("sigma0", 6.0), 1.0e-6)
    x0 = spec.get("x0", 0.5 * grid.L)
    noise_amp = spec.get("noise", 0.002)
    epsilon = amplitude * np.exp(-0.5 * ((x - x0) / sigma0) ** 2)
    epsilon = epsilon + noise_amp * rng.standard_normal(grid.Nx)
    rho = np.full_like(x, spec.get("C0", 0.0), dtype=float)
    residue = np.full_like(x, spec.get("D0", 0.0), dtype=float)
    return {"epsilon": epsilon.astype(float), "rho": rho, "residue": residue}


GENERATORS = {
    "front_seeded": front_seeded,
    "front_seeded_noise": front_seeded_noise,
    "near_uniform_noise": near_uniform_noise,
    "localized_seed": localized_seed,
    "ontology_gaussian_noise": ontology_gaussian_noise,
}


def build_initial_condition(grid: GridConfig, spec: Dict[str, float], seed: int) -> Dict[str, np.ndarray]:
    ic_type = spec["type"]
    if ic_type not in GENERATORS:
        raise ValueError(f"Unsupported initial condition type: {ic_type}")
    return GENERATORS[ic_type](grid, spec, seed)
