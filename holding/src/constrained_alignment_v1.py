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
    nx: int = 96
    ny: int = 96
    length_x: float = 1.0
    length_y: float = 1.0
    dt: float = 2.5e-4
    t_final: float = 2.0
    save_every: int = 40

    @property
    def dx(self) -> float:
        return self.length_x / self.nx

    @property
    def dy(self) -> float:
        return self.length_y / self.ny

    @property
    def n_steps(self) -> int:
        return int(round(self.t_final / self.dt))


@dataclass
class ModelConfig:
    alpha: float = 1.0
    beta: float = 0.12
    gamma: float = 0.08
    D_phi: float = 4.0e-4
    D_R: float = 2.0e-4
    D_S: float = 1.0e-4
    m_min: float = 0.08
    sigma_f: float = 0.035
    eta: float = 0.18
    lambda_R: float = 0.12
    lambda_S: float = 0.10
    residue_gate_center: float = 0.10
    residue_gate_width: float = 0.05
    mismatch_threshold: float = 0.10
    closure_tolerance: float = 0.035
    clamp_residue_nonnegative: bool = True
    clamp_reservoir_nonnegative: bool = True
    enable_event_return: bool = False
    theta_epsilon: float = 0.12
    event_smoothing_passes: int = 2
    event_trigger_fraction: float = 0.02
    event_cooldown_steps: int = 800
    a_w: float = 0.16
    a_s: float = 0.20
    b: float = 0.24
    c: float = 0.08
    chi_ref: float = 2.0
    chi_residue: float = 1.0
    return_gate_bias: float = -1.0
    event_noise_floor: float = 0.0
    regen_saturation_mismatch: float = 0.0
    regen_saturation_residue: float = 0.0
    return_saturation_support_scale: float = 0.0
    return_saturation_reservoir_scale: float = 0.0
    event_dissipation_gain: float = 0.0
    event_dissipation_threshold: float = 0.0
    enable_identity_gate: bool = False
    identity_weight_ref: float = 0.25
    identity_weight_res: float = 0.35
    identity_weight_hist: float = 0.40
    identity_weight_core: float = 0.35
    identity_weight_family: float = 0.35
    identity_gate_threshold: float = 0.45
    identity_gate_sharpness: float = 8.0
    identity_eta_support: float = 0.0
    identity_eta_S: float = 0.0
    identity_core_threshold: float = 0.45
    trigger_history_decay: float = 0.88
    trigger_history_smoothing_passes: int = 1
    core_memory_update_rate: float = 0.18
    canonical_decay: float = 0.995
    signature_membership_floor: float = 0.30
    early_seed_event_count: int = 4
    cycle_phase_period: int = 4
    signature_reinforcement_gain: float = 0.0
    signature_decay_gain: float = 0.0
    signature_core_attractor_gain: float = 0.0
    identity_inter_event_gain: float = 0.0
    family_similarity_smoothing_passes: int = 1
    family_success_similarity_threshold: float = 0.94
    family_success_phase_threshold: float = 0.30
    event_closure_similarity_threshold: float = 0.94
    event_closure_trigger_tolerance: float = 0.08
    event_closure_phase_threshold: float = 0.70
    event_closure_conversion_threshold: float = 0.15


@dataclass
class InitialConditionConfig:
    kind: str = "gaussian_bump"
    amplitude: float = 0.30
    sigma: float = 0.10
    offset_x: float = 0.0
    offset_y: float = 0.0
    noise_std: float = 0.01
    seed: int = 1000


@dataclass
class ReferenceConfig:
    kind: str = "zero"
    amplitude: float = 0.0
    sigma: float = 0.18
    offset_x: float = 0.0
    offset_y: float = 0.0
    tilt_x: float = 0.0
    tilt_y: float = 0.0


@dataclass
class RunConfig:
    grid: GridConfig
    model: ModelConfig
    initial_condition: InitialConditionConfig
    reference: ReferenceConfig
    output_dir: str


def _parse_dataclass(cls: type, values: dict[str, Any] | None) -> Any:
    payload = dict(values or {})
    return cls(**payload)


def load_run_config(path: Path) -> RunConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return RunConfig(
        grid=_parse_dataclass(GridConfig, payload.get("grid")),
        model=_parse_dataclass(ModelConfig, payload.get("model")),
        initial_condition=_parse_dataclass(InitialConditionConfig, payload.get("initial_condition")),
        reference=_parse_dataclass(ReferenceConfig, payload.get("reference")),
        output_dir=str(payload.get("output_dir", "outputs/constrained_alignment_v1")),
    )


def laplacian_neumann_2d(field: np.ndarray, dx: float, dy: float) -> np.ndarray:
    padded = np.pad(field, ((1, 1), (1, 1)), mode="edge")
    lap_x = (padded[1:-1, 2:] - 2.0 * field + padded[1:-1, :-2]) / (dx * dx)
    lap_y = (padded[2:, 1:-1] - 2.0 * field + padded[:-2, 1:-1]) / (dy * dy)
    return lap_x + lap_y


def smooth_local_average(field: np.ndarray, passes: int) -> np.ndarray:
    smoothed = np.array(field, dtype=float, copy=True)
    for _ in range(max(0, int(passes))):
        padded = np.pad(smoothed, ((1, 1), (1, 1)), mode="edge")
        smoothed = (
            padded[1:-1, 1:-1]
            + padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
        ) / 5.0
    return smoothed


def make_coordinate_grid(grid: GridConfig) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(-0.5 * grid.length_x, 0.5 * grid.length_x, grid.nx, endpoint=False)
    y = np.linspace(-0.5 * grid.length_y, 0.5 * grid.length_y, grid.ny, endpoint=False)
    return np.meshgrid(x, y, indexing="xy")


def build_initial_phi(grid: GridConfig, ic: InitialConditionConfig) -> np.ndarray:
    xx, yy = make_coordinate_grid(grid)
    radius_sq = np.square(xx - ic.offset_x) + np.square(yy - ic.offset_y)
    if ic.kind == "gaussian_bump":
        field = ic.amplitude * np.exp(-0.5 * radius_sq / max(ic.sigma * ic.sigma, EPSILON))
    elif ic.kind == "gaussian_ring":
        radius = np.sqrt(radius_sq)
        ring_radius = max(ic.sigma, 0.05)
        field = ic.amplitude * np.exp(-0.5 * np.square(radius - ring_radius) / max(0.25 * ic.sigma * ic.sigma, EPSILON))
    elif ic.kind == "noisy_plateau":
        rng = np.random.default_rng(ic.seed)
        field = np.full((grid.ny, grid.nx), ic.amplitude, dtype=float)
        field += rng.normal(scale=ic.noise_std, size=field.shape)
    else:
        raise ValueError(f"Unsupported initial condition kind: {ic.kind}")
    if ic.noise_std > 0.0 and ic.kind != "noisy_plateau":
        rng = np.random.default_rng(ic.seed)
        field = field + rng.normal(scale=ic.noise_std, size=field.shape)
    return field.astype(float, copy=False)


def build_reference_phi(grid: GridConfig, reference: ReferenceConfig) -> np.ndarray:
    xx, yy = make_coordinate_grid(grid)
    radius_sq = np.square(xx - reference.offset_x) + np.square(yy - reference.offset_y)
    if reference.kind == "zero":
        field = np.zeros((grid.ny, grid.nx), dtype=float)
    elif reference.kind == "gaussian_bump":
        field = reference.amplitude * np.exp(-0.5 * radius_sq / max(reference.sigma * reference.sigma, EPSILON))
    elif reference.kind == "gaussian_ring":
        radius = np.sqrt(radius_sq)
        ring_radius = max(reference.sigma, 0.05)
        field = reference.amplitude * np.exp(
            -0.5 * np.square(radius - ring_radius) / max(0.25 * reference.sigma * reference.sigma, EPSILON)
        )
    elif reference.kind == "tilted_plane":
        field = reference.amplitude + reference.tilt_x * xx + reference.tilt_y * yy
    else:
        raise ValueError(f"Unsupported reference kind: {reference.kind}")
    return field.astype(float, copy=False)


def floor_activation(mismatch: np.ndarray, model: ModelConfig) -> np.ndarray:
    return np.exp(-np.square(mismatch - model.m_min) / max(model.sigma_f * model.sigma_f, EPSILON))


def residue_activation(mismatch: np.ndarray, model: ModelConfig) -> np.ndarray:
    return np.exp(
        -np.square(mismatch - model.residue_gate_center)
        / max(model.residue_gate_width * model.residue_gate_width, EPSILON)
    )


def regeneration_saturation(mismatch: np.ndarray, residue: np.ndarray, model: ModelConfig) -> np.ndarray:
    saturation = np.ones_like(mismatch, dtype=float)
    if model.regen_saturation_mismatch > 0.0:
        saturation *= 1.0 / (1.0 + mismatch / model.regen_saturation_mismatch)
    if model.regen_saturation_residue > 0.0:
        saturation *= 1.0 / (1.0 + residue / model.regen_saturation_residue)
    return saturation


def normalize_nonnegative(field: np.ndarray) -> np.ndarray:
    max_value = float(np.max(field))
    if max_value <= EPSILON:
        return np.zeros_like(field, dtype=float)
    return np.clip(field / max_value, 0.0, 1.0)


def sigmoid(field: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-field))


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_flat = np.ravel(a)
    b_flat = np.ravel(b)
    denom = float(np.linalg.norm(a_flat) * np.linalg.norm(b_flat))
    if denom <= EPSILON:
        return 0.0
    return float(np.dot(a_flat, b_flat) / denom)


def local_cosine_similarity_map(a: np.ndarray, b: np.ndarray, passes: int) -> np.ndarray:
    a_field = np.array(a, dtype=float, copy=False)
    b_field = np.array(b, dtype=float, copy=False)
    if float(np.max(np.abs(a_field))) <= EPSILON or float(np.max(np.abs(b_field))) <= EPSILON:
        return np.zeros_like(a_field, dtype=float)
    prod = smooth_local_average(a_field * b_field, passes)
    a_sq = smooth_local_average(a_field * a_field, passes)
    b_sq = smooth_local_average(b_field * b_field, passes)
    denom = np.sqrt(np.maximum(a_sq * b_sq, EPSILON))
    return np.clip(prod / denom, 0.0, 1.0)


def gradient_magnitude(field: np.ndarray, dx: float, dy: float) -> np.ndarray:
    grad_y, grad_x = np.gradient(field, dy, dx, edge_order=1)
    return np.sqrt(np.square(grad_x) + np.square(grad_y))


def cycle_phase_map(shape: tuple[int, int], event_index: int, period: int) -> np.ndarray:
    if period <= 1:
        phase_value = 0.0
    else:
        phase_value = float(event_index % period) / float(period - 1)
    return np.full(shape, phase_value, dtype=float)


def build_signature_components(
    phi: np.ndarray,
    phi_ref: np.ndarray,
    residue: np.ndarray,
    grid: GridConfig,
    model: ModelConfig,
    event_index: int,
) -> dict[str, np.ndarray]:
    delta = phi - phi_ref
    mismatch = np.abs(delta)
    phase_offset = 0.5 * (1.0 + delta / (mismatch + model.m_min + EPSILON))
    amp = normalize_nonnegative(np.maximum(mismatch - model.m_min, 0.0))
    grad = normalize_nonnegative(gradient_magnitude(mismatch, grid.dx, grid.dy))
    residue_norm = normalize_nonnegative(residue)
    cycle_phase = cycle_phase_map(phi.shape, event_index, model.cycle_phase_period)
    return {
        "phase_offset": np.clip(phase_offset, 0.0, 1.0),
        "amp": amp,
        "grad": grad,
        "residue": residue_norm,
        "cycle_phase": cycle_phase,
    }


def validate_model_config(model: ModelConfig) -> None:
    if not 0.0 <= model.a_w <= 1.0:
        raise ValueError(f"a_w must lie in [0, 1]; got {model.a_w}")
    if not 0.0 <= model.a_s <= 1.0:
        raise ValueError(f"a_s must lie in [0, 1]; got {model.a_s}")
    if model.a_w + model.a_s > 1.0 + 1.0e-9:
        raise ValueError(f"a_w + a_s must be <= 1; got {model.a_w + model.a_s}")
    if not 0.0 <= model.c <= 1.0:
        raise ValueError(f"c must lie in [0, 1]; got {model.c}")
    if model.event_smoothing_passes < 0:
        raise ValueError("event_smoothing_passes must be nonnegative")
    if model.trigger_history_smoothing_passes < 0:
        raise ValueError("trigger_history_smoothing_passes must be nonnegative")
    if model.event_cooldown_steps < 0:
        raise ValueError("event_cooldown_steps must be nonnegative")
    if not 0.0 <= model.event_trigger_fraction <= 1.0:
        raise ValueError("event_trigger_fraction must lie in [0, 1]")
    if model.return_saturation_support_scale < 0.0:
        raise ValueError("return_saturation_support_scale must be nonnegative")
    if model.return_saturation_reservoir_scale < 0.0:
        raise ValueError("return_saturation_reservoir_scale must be nonnegative")
    if model.event_dissipation_gain < 0.0:
        raise ValueError("event_dissipation_gain must be nonnegative")
    if model.event_dissipation_threshold < 0.0:
        raise ValueError("event_dissipation_threshold must be nonnegative")
    if model.identity_weight_ref < 0.0 or model.identity_weight_res < 0.0 or model.identity_weight_hist < 0.0:
        raise ValueError("identity weights must be nonnegative")
    if model.identity_weight_core < 0.0 or model.identity_weight_family < 0.0:
        raise ValueError("identity core/family weights must be nonnegative")
    if model.identity_gate_sharpness < 0.0:
        raise ValueError("identity_gate_sharpness must be nonnegative")
    if model.identity_eta_support < 0.0 or model.identity_eta_S < 0.0:
        raise ValueError("identity eta terms must be nonnegative")
    if not 0.0 <= model.identity_core_threshold <= 1.0:
        raise ValueError("identity_core_threshold must lie in [0, 1]")
    if not 0.0 <= model.trigger_history_decay <= 1.0:
        raise ValueError("trigger_history_decay must lie in [0, 1]")
    if not 0.0 <= model.core_memory_update_rate <= 1.0:
        raise ValueError("core_memory_update_rate must lie in [0, 1]")
    if not 0.0 <= model.canonical_decay <= 1.0:
        raise ValueError("canonical_decay must lie in [0, 1]")
    if not 0.0 <= model.signature_membership_floor <= 1.0:
        raise ValueError("signature_membership_floor must lie in [0, 1]")
    if model.early_seed_event_count < 0:
        raise ValueError("early_seed_event_count must be nonnegative")
    if model.cycle_phase_period < 1:
        raise ValueError("cycle_phase_period must be >= 1")
    if model.signature_reinforcement_gain < 0.0:
        raise ValueError("signature_reinforcement_gain must be nonnegative")
    if model.signature_decay_gain < 0.0:
        raise ValueError("signature_decay_gain must be nonnegative")
    if model.signature_core_attractor_gain < 0.0:
        raise ValueError("signature_core_attractor_gain must be nonnegative")
    if model.identity_inter_event_gain < 0.0:
        raise ValueError("identity_inter_event_gain must be nonnegative")
    if model.family_similarity_smoothing_passes < 0:
        raise ValueError("family_similarity_smoothing_passes must be nonnegative")
    if not 0.0 <= model.family_success_similarity_threshold <= 1.0:
        raise ValueError("family_success_similarity_threshold must lie in [0, 1]")
    if not 0.0 <= model.family_success_phase_threshold <= 1.0:
        raise ValueError("family_success_phase_threshold must lie in [0, 1]")
    if not 0.0 <= model.event_closure_similarity_threshold <= 1.0:
        raise ValueError("event_closure_similarity_threshold must lie in [0, 1]")
    if model.event_closure_trigger_tolerance < 0.0:
        raise ValueError("event_closure_trigger_tolerance must be nonnegative")
    if not 0.0 <= model.event_closure_phase_threshold <= 1.0:
        raise ValueError("event_closure_phase_threshold must lie in [0, 1]")
    if model.event_closure_conversion_threshold < 0.0:
        raise ValueError("event_closure_conversion_threshold must be nonnegative")


def active_region_count(mask: np.ndarray) -> int:
    if mask.size == 0 or not np.any(mask):
        return 0
    visited = np.zeros_like(mask, dtype=bool)
    ny, nx = mask.shape
    count = 0
    for y in range(ny):
        for x in range(nx):
            if visited[y, x] or not mask[y, x]:
                continue
            count += 1
            stack = [(y, x)]
            visited[y, x] = True
            while stack:
                cy, cx = stack.pop()
                for nyi, nxi in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= nyi < ny and 0 <= nxi < nx and mask[nyi, nxi] and not visited[nyi, nxi]:
                        visited[nyi, nxi] = True
                        stack.append((nyi, nxi))
    return count


def signature_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def summarize_state(
    phi: np.ndarray,
    phi_ref: np.ndarray,
    residue: np.ndarray,
    reservoir: np.ndarray,
    model: ModelConfig,
    baseline_signature: np.ndarray | None,
    closure_count: int,
    was_outside_closure: bool,
    event_state: dict[str, Any],
) -> tuple[dict[str, float], np.ndarray, int, bool]:
    delta = phi - phi_ref
    mismatch = np.abs(delta)
    active_mask = mismatch > model.mismatch_threshold
    signature = np.array(
        [
            float(np.mean(mismatch)),
            float(np.std(mismatch)),
            float(np.mean(active_mask)),
            float(active_region_count(active_mask)),
        ],
        dtype=float,
    )
    if baseline_signature is None:
        baseline_signature = signature.copy()
    distance = signature_distance(signature, baseline_signature)
    if distance > model.closure_tolerance:
        was_outside_closure = True
    elif was_outside_closure:
        closure_count += 1
        was_outside_closure = False
    diagnostics = {
        "mean_mismatch": signature[0],
        "std_mismatch": signature[1],
        "support_fraction": signature[2],
        "region_count": signature[3],
        "closure_distance": distance,
        "closure_count": float(closure_count),
        "mean_residue": float(np.mean(residue)),
        "mean_reservoir": float(np.mean(reservoir)),
        "event_count": float(event_state["event_count"]),
        "trigger_fraction": float(event_state["last_trigger_fraction"]),
        "phase_alignment_score": float(event_state["last_phase_alignment_score"]),
        "cycle_similarity_score": float(event_state["last_cycle_similarity_score"]),
        "reservoir_to_deviation_conversion_efficiency": float(event_state["last_conversion_efficiency"]),
        "return_gain_scale": float(event_state["last_return_gain_scale"]),
        "event_dissipation_fraction": float(event_state["last_event_dissipation_fraction"]),
        "mean_identity_proxy": float(event_state["last_mean_identity_proxy"]),
        "mean_family_similarity": float(event_state["last_mean_family_similarity"]),
        "mean_signature_similarity": float(event_state["last_mean_signature_similarity"]),
        "mean_canonical_core": float(event_state["last_mean_canonical_core"]),
        "canonical_signature_strength": float(event_state["last_canonical_signature_strength"]),
        "family_membership_mass": float(event_state["last_family_membership_mass"]),
        "signature_variance_within_family": float(event_state["last_signature_variance_within_family"]),
        "signature_variance_outside_family": float(event_state["last_signature_variance_outside_family"]),
        "early_seed_capture_fraction": float(event_state["last_early_seed_capture_fraction"]),
        "core_overlap_score": float(event_state["last_core_overlap_score"]),
        "successful_family_event_count": float(event_state["successful_family_event_count"]),
        "core_attractor_fraction": float(event_state["last_core_attractor_fraction"]),
        "on_core_return_fraction": float(event_state["last_on_core_return_fraction"]),
        "off_core_return_fraction": float(event_state["last_off_core_return_fraction"]),
        "event_closure_count": float(event_state["event_closure_count"]),
        "event_closed": float(event_state["last_event_closed"]),
    }
    return diagnostics, baseline_signature, closure_count, was_outside_closure


def apply_event_return(
    phi: np.ndarray,
    phi_ref: np.ndarray,
    residue: np.ndarray,
    reservoir: np.ndarray,
    grid: GridConfig,
    model: ModelConfig,
    trigger_mask: np.ndarray,
    event_state: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    delta = phi - phi_ref
    mismatch = np.abs(delta)
    sign = np.sign(delta)
    sign[sign == 0.0] = 1.0
    trigger = trigger_mask.astype(float)
    trigger_fraction = float(np.mean(trigger_mask))
    smoothed_trigger = smooth_local_average(trigger, model.trigger_history_smoothing_passes)
    current_profile = normalize_nonnegative(smooth_local_average(mismatch * trigger, 1))
    signature_components = build_signature_components(
        phi,
        phi_ref,
        residue,
        grid,
        model,
        int(event_state["event_count"]),
    )

    reference_mask = normalize_nonnegative(np.abs(phi_ref))
    residue_mask = normalize_nonnegative(smooth_local_average(residue, 1))
    trigger_history_core = normalize_nonnegative(event_state["rolling_trigger_core"])
    canonical_core = normalize_nonnegative(event_state["canonical_core_memory"])
    local_support = normalize_nonnegative(smoothed_trigger)
    reservoir_mask = normalize_nonnegative(reservoir)
    if model.enable_identity_gate:
        core_signal = canonical_core if event_state["successful_family_event_count"] > 0 else trigger_history_core
        canonical_components = event_state["canonical_signature_components"]
        if event_state["successful_family_event_count"] > 0:
            similarity_components = [
                local_cosine_similarity_map(
                    signature_components[key],
                    normalize_nonnegative(canonical_components[key]),
                    model.family_similarity_smoothing_passes,
                )
                for key in ("phase_offset", "amp", "grad", "residue", "cycle_phase")
            ]
            family_similarity_map = sum(similarity_components) / float(len(similarity_components))
        else:
            family_similarity_map = trigger_history_core.copy()
        residue_coherence = local_cosine_similarity_map(
            residue_mask,
            core_signal,
            model.family_similarity_smoothing_passes,
        )
        weight_total = (
            model.identity_weight_ref
            + model.identity_weight_res
            + model.identity_weight_core
            + model.identity_weight_family
        )
        if weight_total <= EPSILON:
            identity_proxy = np.zeros_like(reference_mask, dtype=float)
        else:
            identity_proxy = (
                model.identity_weight_ref * reference_mask
                + model.identity_weight_res * residue_coherence
                + model.identity_weight_core * core_signal
                + model.identity_weight_family * family_similarity_map
            ) / weight_total
        gate_numerator = sigmoid(model.identity_gate_sharpness * (identity_proxy - model.identity_gate_threshold))
        gate_denominator = 1.0 + model.identity_eta_support * local_support + model.identity_eta_S * reservoir_mask
        return_gate = gate_numerator / gate_denominator
    else:
        gate_input = model.return_gate_bias + model.chi_ref * reference_mask + model.chi_residue * residue_mask
        return_gate = sigmoid(gate_input)
        identity_proxy = return_gate
        family_similarity_map = trigger_history_core
        residue_coherence = residue_mask * trigger_history_core
        core_signal = trigger_history_core
    return_gain_scale = 1.0
    if model.return_saturation_support_scale > EPSILON:
        return_gain_scale *= 1.0 / (1.0 + trigger_fraction / model.return_saturation_support_scale)
    reservoir_return_scale = np.ones_like(reservoir, dtype=float)
    if model.return_saturation_reservoir_scale > EPSILON:
        reservoir_return_scale = 1.0 / (1.0 + reservoir / model.return_saturation_reservoir_scale)
    floor = model.signature_membership_floor
    membership_denominator = max(1.0 - floor, EPSILON)
    membership_map = np.clip((family_similarity_map - floor) / membership_denominator, 0.0, 1.0)
    early_seed_active = event_state["event_count"] < model.early_seed_event_count
    if early_seed_active and event_state["successful_family_event_count"] == 0:
        membership_map = np.maximum(membership_map, 0.35 * local_support + 0.35 * reference_mask)
    alignment_reinforcement = 1.0 + model.signature_reinforcement_gain * membership_map
    nonmatching_decay = 1.0 + model.signature_decay_gain * (1.0 - membership_map)

    write_amount = model.a_w * mismatch * trigger
    store_amount = model.a_s * mismatch * trigger
    available_reservoir = reservoir * trigger
    return_amount = (
        model.b * return_gain_scale * reservoir_return_scale * return_gate * alignment_reinforcement * available_reservoir
        + model.event_noise_floor * trigger
    )
    core_attractor = model.signature_core_attractor_gain * membership_map * core_signal * mismatch * trigger
    broad_excess = max(0.0, trigger_fraction - model.event_dissipation_threshold)
    event_dissipation_fraction = min(1.0, model.event_dissipation_gain * broad_excess)
    retained_amount = (1.0 - model.a_w - model.a_s) * mismatch / nonmatching_decay
    dissipation_amount = event_dissipation_fraction * mismatch * trigger
    event_mismatch = np.maximum(retained_amount + return_amount + core_attractor - dissipation_amount, 0.0)

    next_delta = delta.copy()
    next_delta[trigger_mask] = sign[trigger_mask] * event_mismatch[trigger_mask]
    next_phi = phi_ref + next_delta

    write_gain = 0.5 + 0.5 * return_gate
    next_residue = residue + write_amount * write_gain
    next_reservoir = reservoir * np.maximum(1.0 - (model.c + event_dissipation_fraction) * trigger, 0.0) + store_amount - return_amount
    if model.clamp_residue_nonnegative:
        next_residue = np.maximum(next_residue, 0.0)
    if model.clamp_reservoir_nonnegative:
        next_reservoir = np.maximum(next_reservoir, 0.0)

    triggered_gate = return_gate[trigger_mask]
    phase_alignment_score = float(np.mean(triggered_gate)) if triggered_gate.size else 0.0
    previous_profile = event_state["last_event_profile"]
    cycle_similarity_score = cosine_similarity(current_profile, previous_profile) if previous_profile is not None else 0.0
    reservoir_mass = float(np.sum(available_reservoir))
    conversion_efficiency = float(np.sum(return_amount)) / reservoir_mass if reservoir_mass > EPSILON else 0.0
    previous_trigger_fraction = event_state["last_event_trigger_fraction"]
    event_closed = 0.0
    if previous_profile is not None:
        trigger_delta = abs(trigger_fraction - previous_trigger_fraction)
        if (
            cycle_similarity_score >= model.event_closure_similarity_threshold
            and trigger_delta <= model.event_closure_trigger_tolerance
            and phase_alignment_score >= model.event_closure_phase_threshold
            and conversion_efficiency >= model.event_closure_conversion_threshold
        ):
            event_state["event_closure_count"] += 1
            event_closed = 1.0
    mean_signature_similarity = float(np.mean(family_similarity_map))
    if early_seed_active and event_state["successful_family_event_count"] == 0:
        membership_map = np.maximum(membership_map, 0.35 * local_support + 0.35 * reference_mask)
    mu_map = np.clip(model.core_memory_update_rate * membership_map, 0.0, 1.0)
    decay = model.canonical_decay
    event_state["canonical_core_memory"] = (
        (1.0 - mu_map) * (decay * event_state["canonical_core_memory"]) + mu_map * local_support
    )
    for key, current_component in signature_components.items():
        old_component = event_state["canonical_signature_components"][key]
        event_state["canonical_signature_components"][key] = (
            (1.0 - mu_map) * (decay * old_component) + mu_map * current_component
        )
    family_success = mean_signature_similarity >= model.family_success_similarity_threshold and (
        phase_alignment_score >= model.family_success_phase_threshold
    )
    if family_success:
        event_state["successful_family_event_count"] += 1
    total_return_mass = float(np.sum(return_amount))
    total_reseed_mass = float(np.sum(return_amount + core_attractor))
    updated_core = normalize_nonnegative(event_state["canonical_core_memory"])
    core_mask = updated_core >= model.identity_core_threshold
    on_core_return_fraction = float(np.sum(return_amount[core_mask])) / total_return_mass if total_return_mass > EPSILON else 0.0
    off_core_return_fraction = 1.0 - on_core_return_fraction if total_return_mass > EPSILON else 0.0
    core_attractor_fraction = float(np.sum(core_attractor)) / total_reseed_mass if total_reseed_mass > EPSILON else 0.0
    mean_identity_proxy = float(np.mean(identity_proxy))
    mean_family_similarity = float(np.mean(family_similarity_map))
    mean_canonical_core = float(np.mean(updated_core))
    core_overlap_score = cosine_similarity(current_profile, updated_core)
    canonical_signature_strength = float(
        np.mean(
            [
                np.mean(np.abs(event_state["canonical_signature_components"][key]))
                for key in ("phase_offset", "amp", "grad", "residue", "cycle_phase")
            ]
        )
    )
    family_membership_mass = float(np.mean(membership_map))
    family_mask = membership_map > 0.0
    signature_variance_within_family = float(np.var(family_similarity_map[family_mask])) if np.any(family_mask) else 0.0
    signature_variance_outside_family = float(np.var(family_similarity_map[~family_mask])) if np.any(~family_mask) else 0.0
    early_seed_capture_fraction = float(np.mean(membership_map)) if early_seed_active else 0.0
    event_state["last_event_profile"] = current_profile
    event_state["last_event_trigger_fraction"] = trigger_fraction
    event_state["event_count"] += 1
    event_state["last_trigger_fraction"] = trigger_fraction
    event_state["last_phase_alignment_score"] = phase_alignment_score
    event_state["last_cycle_similarity_score"] = cycle_similarity_score
    event_state["last_conversion_efficiency"] = conversion_efficiency
    event_state["last_return_gain_scale"] = return_gain_scale
    event_state["last_event_dissipation_fraction"] = event_dissipation_fraction
    event_state["last_mean_identity_proxy"] = mean_identity_proxy
    event_state["last_mean_family_similarity"] = mean_family_similarity
    event_state["last_mean_signature_similarity"] = mean_signature_similarity
    event_state["last_mean_canonical_core"] = mean_canonical_core
    event_state["last_canonical_signature_strength"] = canonical_signature_strength
    event_state["last_family_membership_mass"] = family_membership_mass
    event_state["last_signature_variance_within_family"] = signature_variance_within_family
    event_state["last_signature_variance_outside_family"] = signature_variance_outside_family
    event_state["last_early_seed_capture_fraction"] = early_seed_capture_fraction
    event_state["last_core_overlap_score"] = core_overlap_score
    event_state["last_core_attractor_fraction"] = core_attractor_fraction
    event_state["last_on_core_return_fraction"] = on_core_return_fraction
    event_state["last_off_core_return_fraction"] = off_core_return_fraction
    event_state["last_event_closed"] = event_closed
    event_state["last_identity_proxy_map"] = identity_proxy.copy()
    event_state["last_family_similarity_map"] = family_similarity_map.copy()
    event_state["last_canonical_core_map"] = updated_core.copy()
    event_state["rolling_trigger_core"] = (
        model.trigger_history_decay * event_state["rolling_trigger_core"]
        + (1.0 - model.trigger_history_decay) * smoothed_trigger
    )
    return next_phi, next_residue, next_reservoir, {
        "trigger_fraction": trigger_fraction,
        "phase_alignment_score": phase_alignment_score,
        "cycle_similarity_score": cycle_similarity_score,
        "conversion_efficiency": conversion_efficiency,
        "return_gain_scale": return_gain_scale,
        "event_dissipation_fraction": event_dissipation_fraction,
        "mean_identity_proxy": mean_identity_proxy,
        "mean_family_similarity": mean_family_similarity,
        "mean_signature_similarity": mean_signature_similarity,
        "mean_canonical_core": mean_canonical_core,
        "canonical_signature_strength": canonical_signature_strength,
        "family_membership_mass": family_membership_mass,
        "signature_variance_within_family": signature_variance_within_family,
        "signature_variance_outside_family": signature_variance_outside_family,
        "early_seed_capture_fraction": early_seed_capture_fraction,
        "core_overlap_score": core_overlap_score,
        "core_attractor_fraction": core_attractor_fraction,
        "on_core_return_fraction": on_core_return_fraction,
        "off_core_return_fraction": off_core_return_fraction,
        "family_success": 1.0 if family_success else 0.0,
        "event_closed": event_closed,
    }


def step_fields(
    phi: np.ndarray,
    phi_ref: np.ndarray,
    residue: np.ndarray,
    reservoir: np.ndarray,
    grid: GridConfig,
    model: ModelConfig,
    core_bias_map: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    delta = phi - phi_ref
    mismatch = np.abs(delta)
    unit_delta = delta / (mismatch + EPSILON)
    floor_push = model.beta * unit_delta * floor_activation(mismatch, model)
    regen_push = (
        model.gamma
        * residue
        * unit_delta
        * residue_activation(mismatch, model)
        * regeneration_saturation(mismatch, residue, model)
    )
    if core_bias_map is None:
        identity_push = 0.0
    else:
        core_bias = np.clip(core_bias_map, 0.0, 1.0)
        identity_push = model.identity_inter_event_gain * core_bias * unit_delta * residue_activation(mismatch, model)
    phi_rhs = -model.alpha * delta + floor_push + regen_push + identity_push + model.D_phi * laplacian_neumann_2d(phi, grid.dx, grid.dy)
    residue_rhs = model.D_R * laplacian_neumann_2d(residue, grid.dx, grid.dy) + model.eta * mismatch - model.lambda_R * residue
    reservoir_rhs = model.D_S * laplacian_neumann_2d(reservoir, grid.dx, grid.dy) - model.lambda_S * reservoir
    next_phi = phi + grid.dt * phi_rhs
    next_residue = residue + grid.dt * residue_rhs
    next_reservoir = reservoir + grid.dt * reservoir_rhs
    if model.clamp_residue_nonnegative:
        next_residue = np.maximum(next_residue, 0.0)
    if model.clamp_reservoir_nonnegative:
        next_reservoir = np.maximum(next_reservoir, 0.0)
    return next_phi, next_residue, next_reservoir


def simulate(config: RunConfig) -> dict[str, Any]:
    validate_model_config(config.model)
    phi = build_initial_phi(config.grid, config.initial_condition)
    phi_ref = build_reference_phi(config.grid, config.reference)
    residue = np.zeros_like(phi)
    reservoir = np.zeros_like(phi)
    times: list[float] = []
    diagnostics: list[dict[str, float]] = []
    phi_snapshots: list[np.ndarray] = []
    residue_snapshots: list[np.ndarray] = []
    reservoir_snapshots: list[np.ndarray] = []
    canonical_core_snapshots: list[np.ndarray] = []
    identity_proxy_snapshots: list[np.ndarray] = []
    family_similarity_snapshots: list[np.ndarray] = []
    event_log: list[dict[str, float]] = []
    baseline_signature: np.ndarray | None = None
    closure_count = 0
    was_outside_closure = False
    event_state: dict[str, Any] = {
        "event_count": 0,
        "last_event_profile": None,
        "last_trigger_fraction": 0.0,
        "last_phase_alignment_score": 0.0,
        "last_cycle_similarity_score": 0.0,
        "last_conversion_efficiency": 0.0,
        "last_return_gain_scale": 1.0,
        "last_event_dissipation_fraction": 0.0,
        "last_mean_identity_proxy": 0.0,
        "last_mean_family_similarity": 0.0,
        "last_mean_signature_similarity": 0.0,
        "last_mean_canonical_core": 0.0,
        "last_canonical_signature_strength": 0.0,
        "last_family_membership_mass": 0.0,
        "last_signature_variance_within_family": 0.0,
        "last_signature_variance_outside_family": 0.0,
        "last_early_seed_capture_fraction": 0.0,
        "last_core_overlap_score": 0.0,
        "last_core_attractor_fraction": 0.0,
        "last_on_core_return_fraction": 0.0,
        "last_off_core_return_fraction": 0.0,
        "event_closure_count": 0,
        "last_event_closed": 0.0,
        "last_event_trigger_fraction": 0.0,
        "successful_family_event_count": 0,
        "rolling_trigger_core": np.zeros_like(phi),
        "canonical_core_memory": np.zeros_like(phi),
        "canonical_signature_components": {
            "phase_offset": np.zeros_like(phi),
            "amp": np.zeros_like(phi),
            "grad": np.zeros_like(phi),
            "residue": np.zeros_like(phi),
            "cycle_phase": np.zeros_like(phi),
        },
        "last_identity_proxy_map": np.zeros_like(phi),
        "last_family_similarity_map": np.zeros_like(phi),
        "last_canonical_core_map": np.zeros_like(phi),
    }
    last_event_step = -config.model.event_cooldown_steps - 1

    for step in range(config.grid.n_steps + 1):
        if step % config.grid.save_every == 0 or step == config.grid.n_steps:
            current_time = step * config.grid.dt
            diag, baseline_signature, closure_count, was_outside_closure = summarize_state(
                phi,
                phi_ref,
                residue,
                reservoir,
                config.model,
                baseline_signature,
                closure_count,
                was_outside_closure,
                event_state,
            )
            times.append(current_time)
            diagnostics.append(diag)
            phi_snapshots.append(phi.copy())
            residue_snapshots.append(residue.copy())
            reservoir_snapshots.append(reservoir.copy())
            canonical_core_snapshots.append(np.array(event_state["last_canonical_core_map"], copy=True))
            identity_proxy_snapshots.append(np.array(event_state["last_identity_proxy_map"], copy=True))
            family_similarity_snapshots.append(np.array(event_state["last_family_similarity_map"], copy=True))
        if step == config.grid.n_steps:
            break
        core_bias_map = normalize_nonnegative(event_state["canonical_core_memory"])
        phi, residue, reservoir = step_fields(phi, phi_ref, residue, reservoir, config.grid, config.model, core_bias_map)
        if config.model.enable_event_return and step - last_event_step >= config.model.event_cooldown_steps:
            mismatch = np.abs(phi - phi_ref)
            smoothed_mismatch = smooth_local_average(mismatch, config.model.event_smoothing_passes)
            trigger_mask = smoothed_mismatch >= config.model.theta_epsilon
            trigger_fraction = float(np.mean(trigger_mask))
            if trigger_fraction >= config.model.event_trigger_fraction:
                phi, residue, reservoir, event_metrics = apply_event_return(
                    phi,
                    phi_ref,
                    residue,
                    reservoir,
                    config.grid,
                    config.model,
                    trigger_mask,
                    event_state,
                )
                last_event_step = step
                event_log.append(
                    {
                        "step": float(step),
                        "time": float((step + 1) * config.grid.dt),
                        "trigger_fraction": event_metrics["trigger_fraction"],
                        "phase_alignment_score": event_metrics["phase_alignment_score"],
                        "cycle_similarity_score": event_metrics["cycle_similarity_score"],
                        "reservoir_to_deviation_conversion_efficiency": event_metrics["conversion_efficiency"],
                        "return_gain_scale": event_metrics["return_gain_scale"],
                        "event_dissipation_fraction": event_metrics["event_dissipation_fraction"],
                        "mean_identity_proxy": event_metrics["mean_identity_proxy"],
                        "mean_family_similarity": event_metrics["mean_family_similarity"],
                        "mean_signature_similarity": event_metrics["mean_signature_similarity"],
                        "mean_canonical_core": event_metrics["mean_canonical_core"],
                        "canonical_signature_strength": event_metrics["canonical_signature_strength"],
                        "family_membership_mass": event_metrics["family_membership_mass"],
                        "signature_variance_within_family": event_metrics["signature_variance_within_family"],
                        "signature_variance_outside_family": event_metrics["signature_variance_outside_family"],
                        "early_seed_capture_fraction": event_metrics["early_seed_capture_fraction"],
                        "core_overlap_score": event_metrics["core_overlap_score"],
                        "on_core_return_fraction": event_metrics["on_core_return_fraction"],
                        "off_core_return_fraction": event_metrics["off_core_return_fraction"],
                        "family_success": event_metrics["family_success"],
                        "event_closed": event_metrics["event_closed"],
                    }
                )

    return {
        "config": {
            "grid": asdict(config.grid),
            "model": asdict(config.model),
            "initial_condition": asdict(config.initial_condition),
            "reference": asdict(config.reference),
            "output_dir": config.output_dir,
        },
        "times": np.array(times, dtype=float),
        "diagnostics": diagnostics,
        "phi_ref": phi_ref,
        "phi_snapshots": np.stack(phi_snapshots, axis=0),
        "residue_snapshots": np.stack(residue_snapshots, axis=0),
        "reservoir_snapshots": np.stack(reservoir_snapshots, axis=0),
        "canonical_core_snapshots": np.stack(canonical_core_snapshots, axis=0),
        "identity_proxy_snapshots": np.stack(identity_proxy_snapshots, axis=0),
        "family_similarity_snapshots": np.stack(family_similarity_snapshots, axis=0),
        "event_log": event_log,
    }


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics_path = output_dir / "diagnostics.json"
    event_log_path = output_dir / "event_log.json"
    snapshots_path = output_dir / "snapshots.npz"
    summary_path = output_dir / "summary.json"

    diagnostics_path.write_text(json.dumps(result["diagnostics"], indent=2), encoding="utf-8")
    event_log_path.write_text(json.dumps(result["event_log"], indent=2), encoding="utf-8")
    np.savez_compressed(
        snapshots_path,
        times=result["times"],
        phi_ref=result["phi_ref"],
        phi_snapshots=result["phi_snapshots"],
        residue_snapshots=result["residue_snapshots"],
        reservoir_snapshots=result["reservoir_snapshots"],
        canonical_core_snapshots=result["canonical_core_snapshots"],
        identity_proxy_snapshots=result["identity_proxy_snapshots"],
        family_similarity_snapshots=result["family_similarity_snapshots"],
    )

    final_diag = dict(result["diagnostics"][-1])
    final_diag["saved_steps"] = len(result["diagnostics"])
    summary = {
        "config": result["config"],
        "final": final_diag,
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrained alignment Version A scaffold")
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
