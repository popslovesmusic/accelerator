from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DSR_COMMITMENTS_PATH = ROOT / "configs" / "dsr" / "dsr_runtime_commitments_v1.json"


@dataclass(frozen=True)
class DSRCommitments:
    sigma_d_dx_multiplier: float
    sigma_phi_dx_multiplier: float
    interior_margin_multiple: float
    minimum_separation_multiple: float
    amplitude_floor: float
    eta_floor: float

    @property
    def interior_margin_sigma_phi_multiple(self) -> float:
        return self.interior_margin_multiple

    @property
    def minimum_separation_sigma_phi_multiple(self) -> float:
        return self.minimum_separation_multiple


@dataclass(frozen=True)
class SeedSelection:
    x_r: float
    x_g: float
    idx_r: int
    idx_g: int
    amplitude_r: float
    amplitude_g: float
    sigma_phi: float
    sigma_d: float
    interior_margin: float
    minimum_separation: float
    eta_floor: float
    fallback_used: bool
    fallback_reason: str


@dataclass(frozen=True)
class DeltaFloorResult:
    delta_f: np.ndarray
    delta_raw: np.ndarray
    delta_env: np.ndarray
    sign_field: np.ndarray
    sigma_phi: float
    amplitude_r: float
    amplitude_g: float
    minimum_abs_delta_f: float
    maximum_abs_delta_f: float


def load_dsr_commitments(path: Path) -> DSRCommitments:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DSRCommitments(
        sigma_d_dx_multiplier=float(payload["seed_rule"]["smoothing"]["sigma_dx_multiplier"]),
        sigma_phi_dx_multiplier=float(payload["potential_form"]["sigma_phi_dx_multiplier"]),
        interior_margin_multiple=float(payload["seed_rule"]["interior_margin"]["multiple"]),
        minimum_separation_multiple=float(payload["seed_rule"]["minimum_separation"]["multiple"]),
        amplitude_floor=float(payload["potential_form"]["amplitude_rule"]["floor"]),
        eta_floor=float(payload["delta_floor"]["envelope"]["eta_floor"]),
    )


def grid_spacing(x: Sequence[float]) -> float:
    if len(x) < 2:
        return 1.0
    return float(x[1] - x[0])


def domain_length(x: Sequence[float]) -> float:
    if not x:
        return 0.0
    dx = grid_spacing(x)
    return float(x[-1]) + dx


def gaussian_kernel(dx: float, sigma: float) -> np.ndarray:
    if sigma <= 0.0:
        return np.array([1.0], dtype=float)
    radius = max(1, int(math.ceil(4.0 * sigma / max(dx, 1.0e-12))))
    offsets = np.arange(-radius, radius + 1, dtype=float)
    kernel = np.exp(-0.5 * np.square(offsets * dx / sigma))
    kernel /= np.sum(kernel)
    return kernel


def gaussian_smooth_reflect(values: Sequence[float], dx: float, sigma: float) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    kernel = gaussian_kernel(dx, sigma)
    radius = (len(kernel) - 1) // 2
    if radius <= 0:
        return array.copy()
    padded = np.pad(array, (radius, radius), mode="reflect")
    return np.convolve(padded, kernel, mode="valid")


def _interior_indices(x: np.ndarray, interior_margin: float) -> np.ndarray:
    L = domain_length(x.tolist())
    return np.where((x >= interior_margin) & (x <= L - interior_margin))[0]


def _strict_local_maxima(values: np.ndarray, candidate_indices: np.ndarray) -> List[int]:
    maxima: List[int] = []
    n = len(values)
    for index in candidate_indices:
        if index <= 0 or index >= n - 1:
            continue
        if values[index] > values[index - 1] and values[index] > values[index + 1]:
            maxima.append(int(index))
    return maxima


def _best_index(indices: Sequence[int], values: np.ndarray) -> int:
    if not indices:
        raise ValueError("No indices provided.")
    return int(max(indices, key=lambda index: (values[index], -abs(index - len(values) / 2.0))))


def _fallback_second_index(
    x: np.ndarray,
    values: np.ndarray,
    idx_r: int,
    interior_indices: np.ndarray,
    minimum_separation: float,
) -> tuple[int, str]:
    x_r = float(x[idx_r])
    midpoint = domain_length(x.tolist()) / 2.0
    preferred_side = -1.0 if x_r >= midpoint else 1.0
    opposite_candidates = [
        int(index)
        for index in interior_indices
        if math.copysign(1.0, float(x[index]) - midpoint) == preferred_side
        and abs(float(x[index]) - x_r) >= minimum_separation
        and int(index) != idx_r
    ]
    if opposite_candidates:
        return _best_index(opposite_candidates, values), "best_opposite_side_candidate"

    interior_margin = float(x[interior_indices[0]]) if len(interior_indices) > 0 else 0.0
    L = domain_length(x.tolist())
    mirrored_target = x_r - minimum_separation if x_r >= midpoint else x_r + minimum_separation
    mirrored_target = min(max(mirrored_target, interior_margin), L - interior_margin)
    mirrored_index = int(np.argmin(np.abs(x - mirrored_target)))
    if mirrored_index != idx_r and abs(float(x[mirrored_index]) - x_r) >= 0.5 * minimum_separation:
        return mirrored_index, "mirrored_offset_by_minimum_separation"

    boundary_target = x_r + minimum_separation
    if boundary_target > L - interior_margin:
        boundary_target = x_r - minimum_separation
    boundary_target = min(max(boundary_target, interior_margin), L - interior_margin)
    boundary_index = int(np.argmin(np.abs(x - boundary_target)))
    if boundary_index == idx_r:
        all_other = [int(index) for index in interior_indices if int(index) != idx_r]
        if all_other:
            boundary_index = _best_index(all_other, values)
    return boundary_index, "boundary_clamped_offset_by_minimum_separation"


def select_seed_positions(
    x_values: Sequence[float],
    depth_values: Sequence[float],
    commitments: DSRCommitments,
) -> SeedSelection:
    x = np.asarray(x_values, dtype=float)
    depth = np.asarray(depth_values, dtype=float)
    dx = grid_spacing(x_values)
    sigma_phi = commitments.sigma_phi_dx_multiplier * dx
    sigma_d = commitments.sigma_d_dx_multiplier * dx
    interior_margin = commitments.interior_margin_multiple * sigma_phi
    minimum_separation = commitments.minimum_separation_multiple * sigma_phi
    smoothed = gaussian_smooth_reflect(depth, dx, sigma_d)
    interior_indices = _interior_indices(x, interior_margin)
    if len(interior_indices) == 0:
        interior_indices = np.arange(len(x), dtype=int)

    maxima = _strict_local_maxima(smoothed, interior_indices)
    candidate_indices = maxima if maxima else [int(index) for index in interior_indices]
    idx_primary = _best_index(candidate_indices, smoothed)
    x_primary = float(x[idx_primary])

    separated = [
        index
        for index in candidate_indices
        if index != idx_primary and abs(float(x[index]) - x_primary) >= minimum_separation
    ]
    fallback_used = False
    fallback_reason = ""
    if separated:
        idx_secondary = _best_index(separated, smoothed)
    else:
        idx_secondary, fallback_reason = _fallback_second_index(x, smoothed, idx_primary, interior_indices, minimum_separation)
        fallback_used = True

    idx_left, idx_right = sorted([idx_primary, idx_secondary], key=lambda index: float(x[index]))
    amplitude_left = max(float(smoothed[idx_left]), commitments.amplitude_floor)
    amplitude_right = max(float(smoothed[idx_right]), commitments.amplitude_floor)
    return SeedSelection(
        x_r=float(x[idx_left]),
        x_g=float(x[idx_right]),
        idx_r=int(idx_left),
        idx_g=int(idx_right),
        amplitude_r=amplitude_left,
        amplitude_g=amplitude_right,
        sigma_phi=sigma_phi,
        sigma_d=sigma_d,
        interior_margin=interior_margin,
        minimum_separation=minimum_separation,
        eta_floor=commitments.eta_floor,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )


def build_delta_floor(
    x_values: Sequence[float],
    selection: SeedSelection,
    previous_delta: Sequence[float] | None,
) -> DeltaFloorResult:
    x = np.asarray(x_values, dtype=float)
    sigma_phi = selection.sigma_phi
    K_r = np.exp(-0.5 * np.square((x - selection.x_r) / sigma_phi))
    K_g = np.exp(-0.5 * np.square((x - selection.x_g) / sigma_phi))
    g_r = selection.amplitude_r * (x - selection.x_r) / (sigma_phi * sigma_phi) * K_r
    g_g = selection.amplitude_g * (x - selection.x_g) / (sigma_phi * sigma_phi) * K_g
    delta_raw = g_r - g_g

    d_rg = abs(selection.x_g - selection.x_r)
    eta_floor = selection.eta_floor
    amplitude_mean = 0.5 * (selection.amplitude_r + selection.amplitude_g)
    delta_env = (
        eta_floor
        * (d_rg / (d_rg + sigma_phi))
        * amplitude_mean
        * (K_r + K_g)
    )
    delta_env = np.maximum(
        delta_env,
        eta_floor
        * (d_rg / (d_rg + sigma_phi))
        * amplitude_mean
        * np.finfo(float).tiny,
    )

    dominance = np.sign(selection.amplitude_r * K_r - selection.amplitude_g * K_g)
    raw_sign = np.sign(delta_raw)
    midpoint_sign = np.sign(x - 0.5 * (selection.x_r + selection.x_g))
    if previous_delta is not None:
        previous_sign = np.sign(np.asarray(previous_delta, dtype=float))
    else:
        previous_sign = np.zeros_like(x)

    sign_field = dominance.copy()
    zero_mask = sign_field == 0.0
    sign_field[zero_mask] = raw_sign[zero_mask]
    zero_mask = sign_field == 0.0
    sign_field[zero_mask] = midpoint_sign[zero_mask]
    zero_mask = sign_field == 0.0
    sign_field[zero_mask] = previous_sign[zero_mask]
    zero_mask = sign_field == 0.0
    sign_field[zero_mask] = 1.0

    delta_f = sign_field * np.maximum(np.abs(delta_raw), delta_env)
    return DeltaFloorResult(
        delta_f=delta_f,
        delta_raw=delta_raw,
        delta_env=delta_env,
        sign_field=sign_field,
        sigma_phi=sigma_phi,
        amplitude_r=selection.amplitude_r,
        amplitude_g=selection.amplitude_g,
        minimum_abs_delta_f=float(np.min(np.abs(delta_f))) if len(delta_f) > 0 else 0.0,
        maximum_abs_delta_f=float(np.max(np.abs(delta_f))) if len(delta_f) > 0 else 0.0,
    )


def commitments_from_path(path: Path) -> DSRCommitments:
    return load_dsr_commitments(path)


def default_dsr_commitments() -> DSRCommitments:
    return load_dsr_commitments(DEFAULT_DSR_COMMITMENTS_PATH)
