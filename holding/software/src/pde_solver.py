from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal

import numpy as np

from .dsr_geometry import build_delta_floor, default_dsr_commitments, select_seed_positions


EPSILON = 1.0e-12
PHASE_EXPRESSION_STANDARD = "standard"
PHASE_EXPRESSION_INVERTED = "I_phi_inverted"
PHASE_EXPRESSION_BASIS_INVERSE = "I_phi_v2_basis_inverse"
PHASE_EXPRESSION_DELTA_SIGMA_RHO = "I_phi_v3_delta_sigma_rho"
PHASE_EXPRESSION_DSR = "I_phi_v4_dsr"
PHASE_EXPRESSION_ONTOLOGY_1D = "ontology_1d_pde_v1"


@dataclass
class Parameters:
    a: float
    alpha: float
    b: float
    beta: float
    c: float
    gamma: float
    kappa: float
    lam: float
    u: float
    v: float
    s: float
    h: float
    D_eps: float
    D_rho: float
    D_R: float
    eta_kappa: float = 1.0
    eta_u: float = 1.0
    mu: float = 0.0
    nu: float = 0.0
    delta_alpha: float = 0.0
    delta_beta: float = 0.0
    dsr_lambda_D: float = 1.5
    dsr_theta: float = 0.08
    dsr_event_gain: float = 0.10
    dsr_sigma_decay: float = 0.25
    dsr_sigma_load: float = 1.00
    dsr_rho_gain: float = 0.75
    dsr_rho_relax: float = 0.20
    dsr_bootstrap_gain: float = 1.00
    ont_M0: float = 0.25
    ont_aC: float = 0.8
    ont_aD: float = 0.5
    ont_lambda: float = 0.08
    ont_chi: float = 0.6
    ont_kappa_D: float = 0.35
    ont_alpha_C: float = 0.20
    ont_mu_C: float = 0.03
    ont_nu_C: float = 0.10
    ont_beta_D: float = 0.12
    ont_eta_D: float = 0.02
    ont_theta0: float = 0.30
    ont_theta1: float = 0.25
    ont_epsilon_gate: float = 0.03
    ont_gamma_flat: float = 0.15
    ont_c_flat: float = 1.0
    ont_p_flat: float = 4.0
    ont_ell_min: float = 1.0
    ont_eps_speed: float = 1.0e-6


@dataclass
class GridConfig:
    L: float
    Nx: int
    t_final: float
    dt: float
    save_every: int

    @property
    def dx(self) -> float:
        """Uniform spacing for a half-open node-centered grid on [0, L)."""
        return self.L / self.Nx

    @property
    def n_steps(self) -> int:
        return int(round(self.t_final / self.dt))

    @property
    def x(self) -> np.ndarray:
        """Grid nodes on the half-open interval [0, L) with endpoint excluded."""
        return np.linspace(0.0, self.L, self.Nx, endpoint=False)


def laplacian_neumann(field: np.ndarray, dx: float) -> np.ndarray:
    left = np.roll(field, 1)
    right = np.roll(field, -1)
    lap = (left - 2.0 * field + right) / (dx * dx)
    lap[0] = 2.0 * (field[1] - field[0]) / (dx * dx)
    lap[-1] = 2.0 * (field[-2] - field[-1]) / (dx * dx)
    return lap


def normalize_phase_expression(phase_expression: str) -> str:
    normalized = str(phase_expression or PHASE_EXPRESSION_STANDARD).strip() or PHASE_EXPRESSION_STANDARD
    if normalized not in {
        PHASE_EXPRESSION_STANDARD,
        PHASE_EXPRESSION_INVERTED,
        PHASE_EXPRESSION_BASIS_INVERSE,
        PHASE_EXPRESSION_DELTA_SIGMA_RHO,
        PHASE_EXPRESSION_DSR,
        PHASE_EXPRESSION_ONTOLOGY_1D,
    }:
        raise ValueError(f"Unsupported phase_expression: {phase_expression}")
    return normalized


def basis_inverse_determinant(params: Parameters) -> float:
    return 1.0 - params.mu * params.nu


def validate_basis_inverse_params(params: Parameters) -> None:
    determinant = basis_inverse_determinant(params)
    if abs(determinant) <= 1.0e-9:
        raise ValueError(
            f"I_phi_v2_basis_inverse requires an invertible basis map; got 1 - mu*nu = {determinant:.6e}"
        )


def delta_sigma_denominator(params: Parameters) -> float:
    return params.delta_alpha + params.delta_beta


def validate_delta_sigma_params(params: Parameters) -> None:
    denominator = delta_sigma_denominator(params)
    if abs(denominator) <= 1.0e-9:
        raise ValueError(
            "I_phi_v3_delta_sigma_rho requires delta_alpha + delta_beta to be nonzero; "
            f"got {denominator:.6e}"
        )


def map_to_basis(
    epsilon: np.ndarray,
    residue: np.ndarray,
    params: Parameters,
) -> tuple[np.ndarray, np.ndarray]:
    return epsilon + params.mu * residue, residue + params.nu * epsilon


def map_from_basis(
    basis_epsilon: np.ndarray,
    basis_residue: np.ndarray,
    params: Parameters,
) -> tuple[np.ndarray, np.ndarray]:
    determinant = basis_inverse_determinant(params)
    epsilon = (basis_epsilon - params.mu * basis_residue) / determinant
    residue = (basis_residue - params.nu * basis_epsilon) / determinant
    return epsilon, residue


def map_to_delta_sigma(
    epsilon: np.ndarray,
    residue: np.ndarray,
    params: Parameters,
) -> tuple[np.ndarray, np.ndarray]:
    return epsilon - params.delta_alpha * residue, epsilon + params.delta_beta * residue


def map_from_delta_sigma(
    delta: np.ndarray,
    sigma: np.ndarray,
    params: Parameters,
) -> tuple[np.ndarray, np.ndarray]:
    denominator = delta_sigma_denominator(params)
    epsilon = (params.delta_beta * delta + params.delta_alpha * sigma) / denominator
    residue = (sigma - delta) / denominator
    return epsilon, residue


def reaction_terms(
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
    params: Parameters,
    phase_expression: str = PHASE_EXPRESSION_STANDARD,
) -> Dict[str, np.ndarray]:
    normalized_phase_expression = normalize_phase_expression(phase_expression)
    if normalized_phase_expression == PHASE_EXPRESSION_INVERTED:
        return {
            "epsilon": params.eta_kappa * params.kappa * residue - params.lam * epsilon,
            "rho": (
                params.alpha * rho
                - params.beta * epsilon * rho
                - params.gamma * rho * rho
                - params.v * residue
                + params.h
            ),
            "residue": (
                params.a * residue
                - params.b * residue * rho
                - params.c * residue * residue
                + params.eta_u * params.u * epsilon
                + params.s
            ),
        }
    if normalized_phase_expression == PHASE_EXPRESSION_DELTA_SIGMA_RHO:
        delta = epsilon
        sigma = residue
        return {
            "epsilon": (
                params.a * delta
                - params.b * delta * rho
                - params.c * np.power(delta, 3)
                - params.u * delta * sigma
                + params.s
            ),
            "rho": (
                params.alpha * rho
                - params.beta * delta * rho
                - params.gamma * rho * rho
                - params.v * sigma
                + params.h
            ),
            "residue": (
                (params.a - params.lam) * sigma
                + params.kappa * delta
                - params.b * sigma * rho
                - params.c * sigma * sigma
                + params.s
            ),
        }
    if normalized_phase_expression == PHASE_EXPRESSION_BASIS_INVERSE:
        normalized_phase_expression = PHASE_EXPRESSION_STANDARD
    return {
        "epsilon": (
            params.a * epsilon
            - params.b * epsilon * rho
            - params.c * epsilon * epsilon
            + params.u * residue
            + params.s
        ),
        "rho": (
            params.alpha * rho
            - params.beta * epsilon * rho
            - params.gamma * rho * rho
            - params.v * residue
            + params.h
        ),
        "residue": params.kappa * epsilon - params.lam * residue,
    }


def solve_tridiagonal(lower: np.ndarray, diag: np.ndarray, upper: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    n = len(diag)
    if n == 1:
        return rhs / diag

    c_prime = np.zeros(n - 1, dtype=float)
    d_prime = np.zeros(n, dtype=float)

    c_prime[0] = upper[0] / diag[0]
    d_prime[0] = rhs[0] / diag[0]

    for i in range(1, n):
        denom = diag[i] - lower[i - 1] * c_prime[i - 1]
        if i < n - 1:
            c_prime[i] = upper[i] / denom
        d_prime[i] = (rhs[i] - lower[i - 1] * d_prime[i - 1]) / denom

    solution = np.zeros(n, dtype=float)
    solution[-1] = d_prime[-1]
    for i in range(n - 2, -1, -1):
        solution[i] = d_prime[i] - c_prime[i] * solution[i + 1]
    return solution


def diffusion_matrix_bands(diffusion: float, dt: float, dx: float, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if n < 2 or diffusion == 0.0 or dt == 0.0:
        return (
            np.zeros(max(n - 1, 0), dtype=float),
            np.ones(n, dtype=float),
            np.zeros(max(n - 1, 0), dtype=float),
        )

    r = diffusion * dt / (dx * dx)
    lower = np.full(n - 1, -r, dtype=float)
    diag = np.full(n, 1.0 + 2.0 * r, dtype=float)
    upper = np.full(n - 1, -r, dtype=float)

    upper[0] = -2.0 * r
    lower[-1] = -2.0 * r
    return lower, diag, upper


def implicit_diffusion_step(field: np.ndarray, reaction: np.ndarray, diffusion: float, grid: GridConfig) -> np.ndarray:
    rhs = field + grid.dt * reaction
    if diffusion == 0.0:
        return rhs
    lower, diag, upper = diffusion_matrix_bands(diffusion, grid.dt, grid.dx, len(field))
    return solve_tridiagonal(lower, diag, upper, rhs)


def weighted_flux_divergence(field: np.ndarray, weight: np.ndarray, dx: float) -> np.ndarray:
    if len(field) < 2:
        return np.zeros_like(field)
    flux = np.zeros(len(field) + 1, dtype=float)
    face_weight = 0.5 * (weight[:-1] + weight[1:])
    flux[1:-1] = face_weight * (field[1:] - field[:-1]) / dx
    return (flux[1:] - flux[:-1]) / dx


def gradient_neumann(field: np.ndarray, dx: float) -> np.ndarray:
    if len(field) < 2:
        return np.zeros_like(field)
    gradient = (np.roll(field, -1) - np.roll(field, 1)) / (2.0 * dx)
    gradient[0] = (field[1] - field[0]) / dx
    gradient[-1] = (field[-1] - field[-2]) / dx
    return gradient


def sigmoid(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(values, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def ontology_delta_phi_min(params: Parameters) -> float:
    return float(params.ont_theta0 * np.exp(params.ont_lambda * params.ont_ell_min / max(params.ont_c_flat, EPSILON)))


def imex_euler_step_raw(
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
    params: Parameters,
    grid: GridConfig,
    phase_expression: str = PHASE_EXPRESSION_STANDARD,
) -> Dict[str, np.ndarray]:
    reaction = reaction_terms(epsilon, rho, residue, params, phase_expression=phase_expression)
    next_eps = implicit_diffusion_step(epsilon, reaction["epsilon"], params.D_eps, grid)
    next_rho = implicit_diffusion_step(rho, reaction["rho"], params.D_rho, grid)
    next_residue = implicit_diffusion_step(residue, reaction["residue"], params.D_R, grid)

    return {"epsilon": next_eps, "rho": next_rho, "residue": next_residue}


def imex_euler_step(
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
    params: Parameters,
    grid: GridConfig,
    phase_expression: str = PHASE_EXPRESSION_STANDARD,
) -> Dict[str, np.ndarray]:
    next_state = imex_euler_step_raw(epsilon, rho, residue, params, grid, phase_expression=phase_expression)
    return {
        "epsilon": np.maximum(next_state["epsilon"], 0.0),
        "rho": np.maximum(next_state["rho"], 0.0),
        "residue": np.maximum(next_state["residue"], 0.0),
    }


def simulate_dsr_python(
    params: Parameters,
    grid: GridConfig,
    initial_state: Dict[str, np.ndarray],
    blowup_threshold: float,
) -> Dict[str, List[np.ndarray] | List[float] | bool | int]:
    validate_delta_sigma_params(params)
    commitments = default_dsr_commitments()

    epsilon0 = initial_state["epsilon"].astype(float).copy()
    rho = np.maximum(initial_state["rho"].astype(float).copy(), 0.0)
    residue0 = np.maximum(initial_state["residue"].astype(float).copy(), 0.0)
    delta, sigma = map_to_delta_sigma(epsilon0, residue0, params)
    sigma = np.maximum(sigma, 0.0)
    depth = residue0 + params.dsr_bootstrap_gain * np.abs(delta)

    selection = select_seed_positions(grid.x, depth, commitments)
    floor = build_delta_floor(grid.x, selection, previous_delta=delta)
    previous_event_mask = np.zeros_like(delta, dtype=bool)

    snapshots: List[Dict[str, np.ndarray]] = []
    times: List[float] = []
    negative_undershoot_events = 0
    ratchet_event_steps = 0
    seed_update_steps = 0
    blew_up = False

    for step in range(grid.n_steps + 1):
        snapshot_epsilon, snapshot_residue = map_from_delta_sigma(delta, sigma, params)
        snapshot = {
            "epsilon": snapshot_epsilon.copy(),
            "rho": rho.copy(),
            "residue": snapshot_residue.copy(),
            "delta": delta.copy(),
            "sigma": sigma.copy(),
            "depth": depth.copy(),
            "delta_floor": floor.delta_f.copy(),
        }
        if step % grid.save_every == 0 or step == grid.n_steps:
            snapshots.append(snapshot)
            times.append(step * grid.dt)

        if step == grid.n_steps:
            break

        excess = np.maximum(np.abs(delta - floor.delta_f) - params.dsr_theta, 0.0)
        event_mask = excess > 0.0
        crossing_mask = event_mask & ~previous_event_mask
        coupling_gain = 1.0 + max(params.kappa, 0.0)
        persistence_gain = 1.0 / (1.0 + max(params.lam, 0.0))
        if np.any(crossing_mask):
            depth = depth + params.dsr_event_gain * coupling_gain * excess * crossing_mask.astype(float)
            selection = select_seed_positions(grid.x, depth, commitments)
            floor = build_delta_floor(grid.x, selection, previous_delta=delta)
            ratchet_event_steps += 1
            seed_update_steps += 1

        transport_weight = (
            params.D_eps
            * persistence_gain
            * coupling_gain
            * np.maximum(sigma, 0.0)
            / (1.0 + np.maximum(rho, 0.0))
        )
        support_drive = excess * (coupling_gain + params.u * np.tanh(depth))
        closure_drive = coupling_gain * excess + params.v * np.maximum(sigma, 0.0)
        delta_rhs = (
            -params.dsr_lambda_D * (delta - floor.delta_f)
            + weighted_flux_divergence(delta, transport_weight, grid.dx)
            + params.kappa * persistence_gain * excess * np.sign(floor.delta_f)
        )
        sigma_rhs = (
            -(params.dsr_sigma_decay + params.lam) * sigma
            + params.dsr_sigma_load * support_drive
            - params.b * sigma * rho
        )
        rho_rhs = (
            params.dsr_rho_gain * closure_drive
            - (params.dsr_rho_relax + params.gamma) * rho
        )

        next_delta = delta + grid.dt * delta_rhs
        next_sigma = np.maximum(sigma + grid.dt * sigma_rhs, 0.0)
        next_rho = np.maximum(rho + grid.dt * rho_rhs, 0.0)
        next_depth = np.maximum(depth + grid.dt * (params.kappa * excess - 0.1 * params.lam * depth), 0.0)
        next_epsilon_mapped, next_residue_mapped = map_from_delta_sigma(next_delta, next_sigma, params)

        if (
            np.any(~np.isfinite(next_delta))
            or np.any(~np.isfinite(next_sigma))
            or np.any(~np.isfinite(next_rho))
            or np.any(~np.isfinite(next_depth))
            or np.any(~np.isfinite(next_epsilon_mapped))
            or np.any(~np.isfinite(next_residue_mapped))
            or np.max(np.abs(next_delta)) > blowup_threshold
            or np.max(np.abs(next_sigma)) > blowup_threshold
            or np.max(np.abs(next_rho)) > blowup_threshold
            or np.max(np.abs(next_depth)) > blowup_threshold
            or np.max(np.abs(next_epsilon_mapped)) > blowup_threshold
            or np.max(np.abs(next_residue_mapped)) > blowup_threshold
        ):
            blew_up = True
            break

        negative_undershoot_events += int(np.any(next_epsilon_mapped < -EPSILON))
        negative_undershoot_events += int(np.any(next_rho < -EPSILON))
        negative_undershoot_events += int(np.any(next_residue_mapped < -EPSILON))

        delta = next_delta
        sigma = next_sigma
        rho = next_rho
        depth = next_depth
        previous_event_mask = event_mask

    return {
        "x": grid.x,
        "times": times,
        "snapshots": snapshots,
        "blew_up": blew_up,
        "negative_undershoot_steps_detected": negative_undershoot_events,
        "negative_undershoot_events": negative_undershoot_events,
        "nonnegativity_violations": negative_undershoot_events,
        "ratchet_event_steps": ratchet_event_steps,
        "seed_update_steps": seed_update_steps,
        "engine_name": f"python_dsr[{PHASE_EXPRESSION_DSR}]",
    }


def simulate_ontology_python(
    params: Parameters,
    grid: GridConfig,
    initial_state: Dict[str, np.ndarray],
    blowup_threshold: float,
) -> Dict[str, List[np.ndarray] | List[float] | bool | int | float]:
    delta = initial_state["epsilon"].astype(float).copy()
    constraint = np.maximum(initial_state["rho"].astype(float).copy(), 0.0)
    depth = np.maximum(initial_state["residue"].astype(float).copy(), 0.0)

    snapshots: List[Dict[str, np.ndarray | float]] = []
    times: List[float] = []
    negative_undershoot_events = 0
    ratchet_gate_integral = 0.0
    ratchet_active_steps = 0
    blew_up = False
    delta_phi_min = ontology_delta_phi_min(params)

    for step in range(grid.n_steps + 1):
        theta_field = params.ont_theta0 + params.ont_theta1 * constraint
        gate = sigmoid((delta - theta_field) / max(params.ont_epsilon_gate, EPSILON)) * np.maximum(delta, 0.0)
        kappa_proxy = float(np.floor(ratchet_gate_integral))
        snapshot = {
            "epsilon": delta.copy(),
            "rho": constraint.copy(),
            "residue": depth.copy(),
            "delta": delta.copy(),
            "C": constraint.copy(),
            "D": depth.copy(),
            "ratchet_gate": gate.copy(),
            "delta_phi_min": np.full_like(delta, delta_phi_min, dtype=float),
            "kappa_proxy": np.full_like(delta, kappa_proxy, dtype=float),
        }
        if step % grid.save_every == 0 or step == grid.n_steps:
            snapshots.append(snapshot)
            times.append(step * grid.dt)

        if step == grid.n_steps:
            break

        mobility = np.maximum(params.ont_M0 * (1.0 + params.ont_aC * constraint + params.ont_aD * depth), EPSILON)
        transport = weighted_flux_divergence(delta, mobility, grid.dx)
        lap_delta = laplacian_neumann(delta, grid.dx)
        gradient_delta = gradient_neumann(delta, grid.dx)
        drive_without_flatten = transport - params.ont_lambda * delta + params.ont_chi * constraint * delta + params.ont_kappa_D * depth
        speed_proxy = np.abs(drive_without_flatten) / (np.abs(gradient_delta) + max(params.ont_eps_speed, EPSILON))
        speed_ratio = np.minimum(np.maximum(speed_proxy / max(params.ont_c_flat, EPSILON), 0.0), 4.0)
        flatten = params.ont_gamma_flat * np.power(speed_ratio, params.ont_p_flat) * delta

        delta_rhs = drive_without_flatten - flatten
        constraint_rhs = params.ont_alpha_C * gate - params.ont_mu_C * constraint + params.ont_nu_C * lap_delta
        depth_rhs = params.ont_beta_D * gate - params.ont_eta_D * depth

        next_delta = delta + grid.dt * delta_rhs
        next_constraint = np.maximum(constraint + grid.dt * constraint_rhs, 0.0)
        next_depth = np.maximum(depth + grid.dt * depth_rhs, 0.0)

        positive_gate = np.maximum(gate, 0.0)
        ratchet_gate_integral += float(np.sum(positive_gate) * grid.dx * grid.dt)
        if np.any(positive_gate > 0.0):
            ratchet_active_steps += 1

        if (
            np.any(~np.isfinite(next_delta))
            or np.any(~np.isfinite(next_constraint))
            or np.any(~np.isfinite(next_depth))
            or np.max(np.abs(next_delta)) > blowup_threshold
            or np.max(np.abs(next_constraint)) > blowup_threshold
            or np.max(np.abs(next_depth)) > blowup_threshold
        ):
            blew_up = True
            break

        negative_undershoot_events += int(np.any(next_constraint < -EPSILON))
        negative_undershoot_events += int(np.any(next_depth < -EPSILON))

        delta = next_delta
        constraint = next_constraint
        depth = next_depth

    return {
        "x": grid.x,
        "times": times,
        "snapshots": snapshots,
        "blew_up": blew_up,
        "negative_undershoot_steps_detected": negative_undershoot_events,
        "negative_undershoot_events": negative_undershoot_events,
        "nonnegativity_violations": negative_undershoot_events,
        "ontology_delta_phi_min": delta_phi_min,
        "ontology_kappa_proxy": float(np.floor(ratchet_gate_integral)),
        "ontology_gate_integral": ratchet_gate_integral,
        "ontology_ratchet_active_steps": ratchet_active_steps,
        "engine_name": f"python_ontology[{PHASE_EXPRESSION_ONTOLOGY_1D}]",
    }


def simulate(
    params: Parameters,
    grid: GridConfig,
    initial_state: Dict[str, np.ndarray],
    blowup_threshold: float = 1.0e6,
    backend: Literal["auto", "python", "native"] = "auto",
    phase_expression: str = PHASE_EXPRESSION_STANDARD,
) -> Dict[str, List[np.ndarray] | List[float] | bool]:
    if backend not in {"auto", "python", "native"}:
        raise ValueError(f"Unsupported backend: {backend}")
    normalized_phase_expression = normalize_phase_expression(phase_expression)
    use_basis_inverse = normalized_phase_expression == PHASE_EXPRESSION_BASIS_INVERSE
    use_delta_sigma = normalized_phase_expression == PHASE_EXPRESSION_DELTA_SIGMA_RHO
    use_dsr = normalized_phase_expression == PHASE_EXPRESSION_DSR
    use_ontology = normalized_phase_expression == PHASE_EXPRESSION_ONTOLOGY_1D

    if use_dsr or use_ontology:
        if backend == "native":
            raise RuntimeError(f"{normalized_phase_expression} is currently implemented only in the Python solver path.")
        if use_dsr:
            return simulate_dsr_python(params, grid, initial_state, blowup_threshold)
        return simulate_ontology_python(params, grid, initial_state, blowup_threshold)

    # Native C++ is the reference PDE engine when available.
    if backend != "python":
        from .native_backend import is_native_backend_available, simulate_native

        if is_native_backend_available():
            return simulate_native(
                params,
                grid,
                initial_state,
                blowup_threshold,
                phase_expression=normalized_phase_expression,
            )
        if backend == "native":
            raise RuntimeError("Requested native backend, but no native module is installed.")

    epsilon = initial_state["epsilon"].astype(float).copy()
    rho = initial_state["rho"].astype(float).copy()
    residue = initial_state["residue"].astype(float).copy()
    if use_basis_inverse:
        validate_basis_inverse_params(params)
        epsilon, residue = map_to_basis(epsilon, residue, params)
    elif use_delta_sigma:
        validate_delta_sigma_params(params)
        epsilon, residue = map_to_delta_sigma(epsilon, residue, params)

    snapshots: List[Dict[str, np.ndarray]] = []
    times: List[float] = []
    negative_undershoot_events = 0
    blew_up = False

    for step in range(grid.n_steps + 1):
        if use_basis_inverse:
            snapshot_epsilon, snapshot_residue = map_from_basis(epsilon, residue, params)
            snapshot = {
                "epsilon": snapshot_epsilon.copy(),
                "rho": rho.copy(),
                "residue": snapshot_residue.copy(),
            }
        elif use_delta_sigma:
            snapshot_epsilon, snapshot_residue = map_from_delta_sigma(epsilon, residue, params)
            snapshot = {
                "epsilon": snapshot_epsilon.copy(),
                "rho": rho.copy(),
                "residue": snapshot_residue.copy(),
                "delta": epsilon.copy(),
                "sigma": residue.copy(),
            }
        else:
            snapshot_epsilon = epsilon
            snapshot_residue = residue
            snapshot = {
                "epsilon": snapshot_epsilon.copy(),
                "rho": rho.copy(),
                "residue": snapshot_residue.copy(),
            }
        if step % grid.save_every == 0 or step == grid.n_steps:
            snapshots.append(snapshot)
            times.append(step * grid.dt)

        if step == grid.n_steps:
            break

        next_state = imex_euler_step_raw(
            epsilon,
            rho,
            residue,
            params,
            grid,
            phase_expression=normalized_phase_expression,
        )
        if use_basis_inverse:
            next_epsilon_mapped, next_residue_mapped = map_from_basis(
                next_state["epsilon"],
                next_state["residue"],
                params,
            )
        elif use_delta_sigma:
            next_epsilon_mapped, next_residue_mapped = map_from_delta_sigma(
                next_state["epsilon"],
                next_state["residue"],
                params,
            )
        else:
            next_epsilon_mapped = next_state["epsilon"]
            next_residue_mapped = next_state["residue"]
        if (
            np.any(~np.isfinite(next_state["epsilon"]))
            or np.any(~np.isfinite(next_state["rho"]))
            or np.any(~np.isfinite(next_state["residue"]))
            or np.any(~np.isfinite(next_epsilon_mapped))
            or np.any(~np.isfinite(next_residue_mapped))
            or np.max(np.abs(next_state["epsilon"])) > blowup_threshold
            or np.max(np.abs(next_state["rho"])) > blowup_threshold
            or np.max(np.abs(next_state["residue"])) > blowup_threshold
            or np.max(np.abs(next_epsilon_mapped)) > blowup_threshold
            or np.max(np.abs(next_residue_mapped)) > blowup_threshold
        ):
            blew_up = True
            break

        negative_undershoot_events += int(np.any(next_epsilon_mapped < -EPSILON))
        negative_undershoot_events += int(np.any(next_state["rho"] < -EPSILON))
        negative_undershoot_events += int(np.any(next_residue_mapped < -EPSILON))

        if use_delta_sigma:
            epsilon = next_state["epsilon"]
            rho = np.maximum(next_state["rho"], 0.0)
            residue = np.maximum(next_state["residue"], 0.0)
        else:
            epsilon = np.maximum(next_state["epsilon"], 0.0)
            rho = np.maximum(next_state["rho"], 0.0)
            residue = np.maximum(next_state["residue"], 0.0)

    return {
        "x": grid.x,
        "times": times,
        "snapshots": snapshots,
        "blew_up": blew_up,
        # Compatibility alias: this is an event counter, not a count of all negative entries.
        "negative_undershoot_steps_detected": negative_undershoot_events,
        "negative_undershoot_events": negative_undershoot_events,
        "nonnegativity_violations": negative_undershoot_events,
        "engine_name": f"python_imex_euler[{normalized_phase_expression}]",
    }
