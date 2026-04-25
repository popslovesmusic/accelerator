from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

RHO_FLOOR = 1.0e-6
ACTIVITY_FLOOR = 1.0e-8
EXCLUSION_THRESHOLD = 1.0


@dataclass
class SnapshotDiagnostics:
    time: float
    mean_eps: float
    mean_rho: float
    mean_R: float
    var_eps: float
    var_rho: float
    var_R: float
    total_eps: float
    total_rho: float
    total_R: float
    exclusion_fraction: float
    interface_count: int
    max_sharpness: float
    n_exclusion_domains: int
    largest_exclusion_domain: float
    largest_pressure_domain: float
    mean_node_ratio: float
    median_node_ratio: float
    max_node_ratio: float
    mean_sharpness: float
    inactive_fraction: float
    active_fraction: float
    excluded_active_fraction: float
    undefined_ratio_fraction: float


def activity_mask(epsilon: np.ndarray, rho: np.ndarray) -> np.ndarray:
    return (epsilon + rho) > ACTIVITY_FLOOR


def node_ratio(epsilon: np.ndarray, rho: np.ndarray) -> np.ndarray:
    ratio = epsilon / np.maximum(rho, RHO_FLOOR)
    ratio = ratio.astype(float, copy=False)
    ratio[~activity_mask(epsilon, rho)] = np.nan
    return ratio


def sharpness(node_ratio_field: np.ndarray, dx: float) -> np.ndarray:
    sigma = np.zeros_like(node_ratio_field, dtype=float)
    if len(node_ratio_field) < 2:
        return sigma
    safe_ratio = np.where(np.isfinite(node_ratio_field), node_ratio_field, 0.0)
    sigma[:] = np.abs(np.gradient(safe_ratio, dx, edge_order=1))
    inactive_neighbors = ~np.isfinite(node_ratio_field)
    sigma[inactive_neighbors] = 0.0
    return sigma


def connected_lengths(mask: np.ndarray, dx: float) -> List[float]:
    lengths: List[float] = []
    start = None
    for idx, value in enumerate(mask):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            lengths.append((idx - start) * dx)
            start = None
    if start is not None:
        lengths.append((len(mask) - start) * dx)
    return lengths


def interface_positions(x: np.ndarray, ratio: np.ndarray) -> List[float]:
    positions: List[float] = []
    shifted = ratio - 1.0
    for idx in range(len(shifted) - 1):
        left = shifted[idx]
        right = shifted[idx + 1]
        if not np.isfinite(left) or not np.isfinite(right):
            continue
        if left == 0.0:
            positions.append(float(x[idx]))
        elif left * right < 0.0:
            frac = abs(left) / (abs(left) + abs(right))
            positions.append(float(x[idx] + frac * (x[idx + 1] - x[idx])))
    return positions


def front_width(sharpness_field: np.ndarray, position_index: int) -> float:
    local_sharpness = max(sharpness_field[position_index], RHO_FLOOR)
    return 1.0 / local_sharpness


def residue_side_means(x: np.ndarray, residue: np.ndarray, position: float) -> Tuple[float, float]:
    left_mask = x < position
    right_mask = x >= position
    left_mean = float(np.mean(residue[left_mask])) if np.any(left_mask) else float(residue[0])
    right_mean = float(np.mean(residue[right_mask])) if np.any(right_mask) else float(residue[-1])
    return left_mean, right_mean


def compute_snapshot_metrics(
    x: np.ndarray,
    time: float,
    epsilon: np.ndarray,
    rho: np.ndarray,
    residue: np.ndarray,
) -> Tuple[SnapshotDiagnostics, List[Dict[str, float]], Dict[str, np.ndarray]]:
    dx = float(x[1] - x[0]) if len(x) > 1 else 1.0
    ratio = node_ratio(epsilon, rho)
    sigma = sharpness(ratio, dx)
    active = activity_mask(epsilon, rho)
    exclusion_mask = active & (ratio > EXCLUSION_THRESHOLD)
    pressure_mask = active & ~exclusion_mask
    inactive_fraction = float(np.mean((~active).astype(float))) if len(active) else 0.0
    active_fraction = float(np.mean(active.astype(float))) if len(active) else 0.0
    excluded_active_fraction = float(np.mean(exclusion_mask[active].astype(float))) if np.any(active) else 0.0
    undefined_ratio_fraction = float(np.mean((~np.isfinite(ratio)).astype(float))) if len(ratio) else 0.0

    exclusion_lengths = connected_lengths(exclusion_mask, dx)
    pressure_lengths = connected_lengths(pressure_mask, dx)
    front_positions = interface_positions(x, ratio)
    fronts: List[Dict[str, float]] = []
    for front_id, position in enumerate(front_positions):
        nearest_idx = int(np.clip(np.searchsorted(x, position), 0, len(x) - 1))
        left_mean_R, right_mean_R = residue_side_means(x, residue, position)
        fronts.append(
            {
                "time": time,
                "front_id": front_id,
                "front_position": position,
                "front_velocity": 0.0,
                "front_width": front_width(sigma, nearest_idx),
                "front_sharpness": float(sigma[nearest_idx]),
                "left_mean_R": left_mean_R,
                "right_mean_R": right_mean_R,
                "residue_asymmetry": left_mean_R - right_mean_R,
            }
        )

    snapshot = SnapshotDiagnostics(
        time=time,
        mean_eps=float(np.mean(epsilon)),
        mean_rho=float(np.mean(rho)),
        mean_R=float(np.mean(residue)),
        var_eps=float(np.var(epsilon)),
        var_rho=float(np.var(rho)),
        var_R=float(np.var(residue)),
        total_eps=float(np.trapezoid(epsilon, x)),
        total_rho=float(np.trapezoid(rho, x)),
        total_R=float(np.trapezoid(residue, x)),
        exclusion_fraction=excluded_active_fraction,
        interface_count=len(front_positions),
        max_sharpness=float(np.max(sigma)),
        n_exclusion_domains=len(exclusion_lengths),
        largest_exclusion_domain=float(max(exclusion_lengths) if exclusion_lengths else 0.0),
        largest_pressure_domain=float(max(pressure_lengths) if pressure_lengths else 0.0),
        mean_node_ratio=float(np.mean(ratio[active])) if np.any(active) else 0.0,
        median_node_ratio=float(np.median(ratio[active])) if np.any(active) else 0.0,
        max_node_ratio=float(np.max(ratio[active])) if np.any(active) else 0.0,
        mean_sharpness=float(np.mean(sigma[active])) if np.any(active) else 0.0,
        inactive_fraction=inactive_fraction,
        active_fraction=active_fraction,
        excluded_active_fraction=excluded_active_fraction,
        undefined_ratio_fraction=undefined_ratio_fraction,
    )

    profile = {
        "x": x,
        "eps": epsilon,
        "rho": rho,
        "R": residue,
        "node_ratio": ratio,
        "sharpness": sigma,
    }
    return snapshot, fronts, profile


def assign_front_velocities(front_rows: List[Dict[str, float]]) -> None:
    rows_by_front: Dict[int, List[Dict[str, float]]] = {}
    for row in front_rows:
        rows_by_front.setdefault(int(row["front_id"]), []).append(row)

    for rows in rows_by_front.values():
        rows.sort(key=lambda item: item["time"])
        if len(rows) < 2:
            continue
        previous = rows[0]
        for current in rows[1:]:
            dt = current["time"] - previous["time"]
            current["front_velocity"] = 0.0 if dt <= 0.0 else (current["front_position"] - previous["front_position"]) / dt
            previous = current


def track_fronts(front_frames: List[List[Dict[str, float]]], max_match_distance: float) -> List[Dict[str, float]]:
    tracked_rows: List[Dict[str, float]] = []
    next_front_id = 0
    active_tracks: Dict[int, float] = {}

    for frame in front_frames:
        if not frame:
            active_tracks = {}
            continue

        frame_rows = sorted(frame, key=lambda item: item["front_position"])
        current_tracks: Dict[int, float] = {}
        candidate_track_ids_by_row: Dict[int, List[int]] = {}
        candidate_row_indices_by_track: Dict[int, List[int]] = {track_id: [] for track_id in active_tracks}
        distances: Dict[tuple[int, int], float] = {}

        for row_index, row in enumerate(frame_rows):
            candidates: List[int] = []
            for track_id, previous_position in active_tracks.items():
                distance = abs(row["front_position"] - previous_position)
                if distance <= max_match_distance:
                    candidates.append(track_id)
                    candidate_row_indices_by_track[track_id].append(row_index)
                    distances[(row_index, track_id)] = distance
            candidate_track_ids_by_row[row_index] = candidates

        primary_row_by_track: Dict[int, int] = {}
        for track_id, row_indices in candidate_row_indices_by_track.items():
            if not row_indices:
                continue
            primary_row_by_track[track_id] = min(row_indices, key=lambda idx: distances[(idx, track_id)])

        used_track_ids: set[int] = set()

        for row_index, row in enumerate(frame_rows):
            candidates = candidate_track_ids_by_row[row_index]
            tracked = dict(row)

            if not candidates:
                tracked["front_id"] = next_front_id
                tracked["front_status"] = "created"
                tracked["source_front_id"] = None
                tracked["predecessor_count"] = 0
                tracked["successor_count"] = 1
                next_front_id += 1
            elif len(candidates) > 1:
                chosen_track = min(candidates, key=lambda track_id: distances[(row_index, track_id)])
                if chosen_track in used_track_ids:
                    tracked["front_id"] = next_front_id
                    next_front_id += 1
                else:
                    tracked["front_id"] = chosen_track
                    used_track_ids.add(chosen_track)
                tracked["front_status"] = "merged"
                tracked["source_front_id"] = chosen_track
                tracked["predecessor_count"] = len(candidates)
                tracked["successor_count"] = len(candidate_row_indices_by_track.get(chosen_track, []))
            else:
                source_track = candidates[0]
                successor_count = len(candidate_row_indices_by_track.get(source_track, []))
                is_primary_match = primary_row_by_track.get(source_track) == row_index and source_track not in used_track_ids
                if is_primary_match:
                    tracked["front_id"] = source_track
                    used_track_ids.add(source_track)
                    tracked["front_status"] = "continued" if successor_count == 1 else "split"
                else:
                    tracked["front_id"] = next_front_id
                    next_front_id += 1
                    tracked["front_status"] = "split"
                tracked["source_front_id"] = source_track
                tracked["predecessor_count"] = 1
                tracked["successor_count"] = successor_count

            tracked_rows.append(tracked)
            current_tracks[int(tracked["front_id"])] = row["front_position"]

        active_tracks = current_tracks

    assign_front_velocities(tracked_rows)
    return tracked_rows
