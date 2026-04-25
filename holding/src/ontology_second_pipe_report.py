from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np

from software.src.ontology_local_report import (
    classify_regime,
    fit_tail_slope,
    load_json,
    profile_time_value,
    read_csv,
    run_ic_index,
    sorted_relational_profiles,
    write_csv,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze ontology-local second-pipe probe outputs.")
    parser.add_argument("--output-root", required=True, help="Batch output root containing ontology-local run outputs.")
    parser.add_argument("--config", required=True, help="Config path used to recover IC metadata.")
    parser.add_argument("--param-a", default="ont_chi", help="First structural parameter to track.")
    parser.add_argument("--param-b", default="ont_lambda", help="Second structural parameter to track.")
    parser.add_argument("--features-csv", required=True, help="Destination CSV for per-run features.")
    parser.add_argument("--clusters-csv", required=True, help="Destination CSV for metastable cluster assignments.")
    parser.add_argument("--json-output", required=True, help="Destination JSON summary.")
    parser.add_argument("--md-output", required=True, help="Destination Markdown summary.")
    return parser.parse_args()


def mean_field(profile_rows: Sequence[Dict[str, str]], key: str) -> float:
    values = np.asarray([float(row.get(key, 0.0) or 0.0) for row in profile_rows], dtype=float)
    if values.size == 0:
        return 0.0
    return float(np.mean(values))


def max_field(profile_rows: Sequence[Dict[str, str]], key: str) -> float:
    values = np.asarray([float(row.get(key, 0.0) or 0.0) for row in profile_rows], dtype=float)
    if values.size == 0:
        return 0.0
    return float(np.max(values))


def compute_reactivations(times: Sequence[float], values: Sequence[float], activation_floor: float) -> int:
    time_array = np.asarray(times, dtype=float)
    value_array = np.asarray(values, dtype=float)
    if time_array.size < 3 or value_array.size != time_array.size:
        return 0
    tolerance = max(1.0e-5, 0.02 * max(float(np.max(value_array)), activation_floor))
    peaks: List[int] = []
    for index in range(1, value_array.size - 1):
        if value_array[index] >= activation_floor and value_array[index] >= value_array[index - 1] and value_array[index] > value_array[index + 1]:
            if (value_array[index] - value_array[index - 1] > tolerance) or (value_array[index] - value_array[index + 1] > tolerance):
                peaks.append(index)
    return max(0, len(peaks) - 1)


def compute_residue_decay_rate(times: Sequence[float], residue_means: Sequence[float]) -> float:
    time_array = np.asarray(times, dtype=float)
    residue_array = np.asarray(residue_means, dtype=float)
    if time_array.size < 2 or residue_array.size != time_array.size:
        return 0.0
    peak_index = int(np.argmax(residue_array))
    tail_times = time_array[peak_index:]
    tail_values = residue_array[peak_index:]
    if tail_times.size < 2:
        return 0.0
    return fit_tail_slope(tail_times, tail_values, tail_fraction=1.0)


def standardize_matrix(matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0:
        return matrix
    mean = np.mean(matrix, axis=0)
    std = np.std(matrix, axis=0)
    std = np.where(std < 1.0e-12, 1.0, std)
    return (matrix - mean) / std


def kmeans_two_clusters(matrix: np.ndarray, max_iter: int = 100) -> np.ndarray:
    if matrix.shape[0] < 2:
        return np.zeros(matrix.shape[0], dtype=int)
    centroid_a = matrix[0].copy()
    distances = np.linalg.norm(matrix - centroid_a, axis=1)
    centroid_b = matrix[int(np.argmax(distances))].copy()
    labels = np.zeros(matrix.shape[0], dtype=int)
    for _ in range(max_iter):
        new_labels = (np.linalg.norm(matrix - centroid_b, axis=1) < np.linalg.norm(matrix - centroid_a, axis=1)).astype(int)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        if np.any(labels == 0):
            centroid_a = np.mean(matrix[labels == 0], axis=0)
        if np.any(labels == 1):
            centroid_b = np.mean(matrix[labels == 1], axis=0)
    return labels


def pairwise_distance(point_a: np.ndarray, point_b: np.ndarray) -> float:
    return float(np.linalg.norm(point_a - point_b))


def complete_linkage_distance(cluster_a: Sequence[int], cluster_b: Sequence[int], matrix: np.ndarray) -> float:
    return max(pairwise_distance(matrix[index_a], matrix[index_b]) for index_a in cluster_a for index_b in cluster_b)


def hierarchical_two_clusters(matrix: np.ndarray) -> np.ndarray:
    count = matrix.shape[0]
    if count < 2:
        return np.zeros(count, dtype=int)
    clusters: List[List[int]] = [[index] for index in range(count)]
    while len(clusters) > 2:
        best_pair = (0, 1)
        best_distance = math.inf
        for index_a in range(len(clusters)):
            for index_b in range(index_a + 1, len(clusters)):
                distance = complete_linkage_distance(clusters[index_a], clusters[index_b], matrix)
                if distance < best_distance:
                    best_distance = distance
                    best_pair = (index_a, index_b)
        merged = clusters[best_pair[0]] + clusters[best_pair[1]]
        clusters = [cluster for index, cluster in enumerate(clusters) if index not in best_pair]
        clusters.append(merged)
    labels = np.zeros(count, dtype=int)
    for label, cluster in enumerate(clusters):
        for index in cluster:
            labels[index] = label
    return labels


def unique_seed_count(rows: Sequence[Dict[str, object]], labels: np.ndarray, cluster_id: int) -> int:
    return len({int(row["seed"]) for row, label in zip(rows, labels) if int(label) == cluster_id})


def cluster_contains_both_amplitudes(rows: Sequence[Dict[str, object]], labels: np.ndarray, cluster_id: int) -> bool:
    amplitudes = {float(row["A0"]) for row, label in zip(rows, labels) if int(label) == cluster_id}
    return len(amplitudes) > 1


def render_markdown(
    output_root: Path,
    run_rows: Sequence[Dict[str, object]],
    metastable_rows: Sequence[Dict[str, object]],
    cluster_rows: Sequence[Dict[str, object]],
    summary: Dict[str, object],
    param_a: str,
    param_b: str,
) -> str:
    lines = [
        "# Ontology Second Pipe Report",
        "",
        "Date: `2026-04-04`",
        "",
        "## Scope",
        "",
        f"Output root: `{output_root}`",
        "",
        f"This note tests whether the confirmed ontology-local metastable corridor contains more than one repeatable internal response family under local `{param_a}` and `{param_b}` perturbations.",
        "",
        "## Run Counts",
        "",
        f"- total runs: `{len(run_rows)}`",
        f"- metastable runs used for clustering: `{len(metastable_rows)}`",
        "",
        "## Decision",
        "",
        f"- second_pipe_detected: `{summary['second_pipe_detected']}`",
        f"- kmeans_two_clusters: `{summary['kmeans_two_clusters']}`",
        f"- hierarchical_two_clusters: `{summary['hierarchical_two_clusters']}`",
        f"- repeats_across_seeds: `{summary['repeats_across_seeds']}`",
        f"- not_reducible_to_A0_split: `{summary['not_reducible_to_A0_split']}`",
        "",
        "## Metastable Cluster Summary",
        "",
    ]
    for cluster_id in sorted({int(row["kmeans_cluster"]) for row in cluster_rows}) if cluster_rows else []:
        cluster_members = [row for row in cluster_rows if int(row["kmeans_cluster"]) == cluster_id]
        seeds = sorted({int(row["seed"]) for row in cluster_members})
        amplitudes = sorted({float(row["A0"]) for row in cluster_members})
        param_a_values = sorted({float(row[param_a]) for row in cluster_members})
        param_b_values = sorted({float(row[param_b]) for row in cluster_members})
        lines.append(
            f"- cluster `{cluster_id}`: runs=`{len(cluster_members)}`, seeds=`{seeds}`, A0=`{amplitudes}`, "
            f"{param_a}=`{param_a_values}`, {param_b}=`{param_b_values}`, "
            f"mean_time_to_peak=`{np.mean([float(row['time_to_peak']) for row in cluster_members]):.3f}`, "
            f"mean_late_time_slope=`{np.mean([float(row['late_time_slope']) for row in cluster_members]):.6e}`, "
            f"mean_reactivations=`{np.mean([float(row['number_of_reactivations']) for row in cluster_members]):.3f}`, "
            f"mean_residue_decay_rate=`{np.mean([float(row['residue_decay_rate']) for row in cluster_members]):.6e}`"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["interpretation"]),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root).resolve()
    config_payload = load_json(Path(args.config).resolve())
    param_a = str(args.param_a)
    param_b = str(args.param_b)
    manifest_rows = read_csv(output_root / "run_manifest.csv")
    summary_rows = {row["run_id"]: row for row in read_csv(output_root / "final_summary.csv")}
    initial_conditions = list(config_payload.get("initial_conditions", []))

    run_rows: List[Dict[str, object]] = []
    for manifest_row in manifest_rows:
        run_id = str(manifest_row["run_id"])
        profile_paths = sorted_relational_profiles(output_root, run_id)
        if not profile_paths:
            continue

        profile_times: List[float] = []
        profile_peak_deltas: List[float] = []
        residue_means: List[float] = []
        persistence_start: float | None = None
        persistence_end: float | None = None
        final_profile_rows: List[Dict[str, str]] = []
        final_profile_time = 0.0
        delta_phi_min = 0.0
        kappa_proxy = 0.0
        for profile_path in profile_paths:
            profile_rows = read_csv(profile_path)
            current_time = profile_time_value(profile_path)
            current_peak_delta = max_field(profile_rows, "delta")
            current_delta_phi_min = float(profile_rows[0].get("delta_phi_min", summary_rows.get(run_id, {}).get("ontology_delta_phi_min", 0.0)) or 0.0)
            current_kappa_proxy = float(profile_rows[0].get("kappa_proxy", summary_rows.get(run_id, {}).get("ontology_kappa_proxy", 0.0)) or 0.0)
            current_residue_mean = mean_field(profile_rows, "D")
            profile_times.append(current_time)
            profile_peak_deltas.append(current_peak_delta)
            residue_means.append(current_residue_mean)
            if current_peak_delta >= current_delta_phi_min:
                if persistence_start is None:
                    persistence_start = current_time
                persistence_end = current_time
            final_profile_rows = profile_rows
            final_profile_time = current_time
            delta_phi_min = current_delta_phi_min
            kappa_proxy = current_kappa_proxy

        final_max_delta = max_field(final_profile_rows, "delta")
        final_mean_C = mean_field(final_profile_rows, "C")
        final_mean_D = mean_field(final_profile_rows, "D")
        peak_max_delta = max(profile_peak_deltas) if profile_peak_deltas else 0.0
        peak_index = int(np.argmax(np.asarray(profile_peak_deltas, dtype=float))) if profile_peak_deltas else 0
        residue_peak_index = int(np.argmax(np.asarray(residue_means, dtype=float))) if residue_means else 0
        persistence_window = 0.0
        if persistence_start is not None and persistence_end is not None:
            persistence_window = max(0.0, persistence_end - persistence_start)
        late_time_slope = fit_tail_slope(profile_times, profile_peak_deltas)
        residue_written = (kappa_proxy >= 1.0) or (final_mean_D > 1.0e-5)
        ontology_local_label = classify_regime(
            peak_max_delta=peak_max_delta,
            final_max_delta=final_max_delta,
            delta_phi_min=delta_phi_min,
            final_mean_C=final_mean_C,
            final_mean_D=final_mean_D,
            residue_written=residue_written,
            persistence_window=persistence_window,
            late_time_slope=late_time_slope,
        )
        ic_metadata: Dict[str, object] = {}
        ic_index = run_ic_index(run_id)
        if ic_index is not None and 0 <= ic_index < len(initial_conditions):
            ic_spec = initial_conditions[ic_index]
            ic_metadata = {
                "A0": float(ic_spec.get("A0", np.nan)),
                "width": float(ic_spec.get("sigma0", np.nan)),
                "noise": float(ic_spec.get("noise", np.nan)),
            }

        row = {
            "run_id": run_id,
            "seed": int(manifest_row.get("seed", 0) or 0),
            "A0": ic_metadata.get("A0", np.nan),
            "width": ic_metadata.get("width", np.nan),
            "noise": ic_metadata.get("noise", np.nan),
            param_a: float(manifest_row.get(param_a, 0.0) or 0.0),
            param_b: float(manifest_row.get(param_b, 0.0) or 0.0),
            "ontology_local_label": ontology_local_label,
            "legacy_classification": summary_rows.get(run_id, {}).get("classification", manifest_row.get("classification", "")),
            "peak_delta": peak_max_delta,
            "time_to_peak": float(profile_times[peak_index]) if profile_times else 0.0,
            "late_time_slope": late_time_slope,
            "delta_at_end": final_max_delta,
            "area_under_delta_curve": float(np.trapezoid(np.asarray(profile_peak_deltas, dtype=float), np.asarray(profile_times, dtype=float))) if len(profile_times) >= 2 else 0.0,
            "number_of_reactivations": compute_reactivations(profile_times, profile_peak_deltas, delta_phi_min),
            "residue_written": str(residue_written).lower(),
            "residue_peak_time": float(profile_times[residue_peak_index]) if profile_times else 0.0,
            "residue_decay_rate": compute_residue_decay_rate(profile_times, residue_means),
            "persistence_window": persistence_window,
            "notes": f"{ontology_local_label}_{param_a}_{float(manifest_row.get(param_a, 0.0) or 0.0):.3f}_{param_b}_{float(manifest_row.get(param_b, 0.0) or 0.0):.3f}",
        }
        run_rows.append(row)

    run_rows.sort(key=lambda row: str(row["run_id"]))
    metastable_rows = [row for row in run_rows if str(row["ontology_local_label"]) == "metastable"]
    cluster_rows: List[Dict[str, object]] = []
    summary: Dict[str, object] = {
        "total_runs": len(run_rows),
        "metastable_runs": len(metastable_rows),
        "kmeans_two_clusters": False,
        "hierarchical_two_clusters": False,
        "repeats_across_seeds": False,
        "not_reducible_to_A0_split": False,
        "second_pipe_detected": False,
        "interpretation": "The metastable corridor remains unresolved at this parameter scale.",
    }
    if len(metastable_rows) >= 4:
        feature_matrix = np.asarray(
            [
                [
                    float(row["time_to_peak"]),
                    float(row["late_time_slope"]),
                    float(row["number_of_reactivations"]),
                    float(row["residue_decay_rate"]),
                ]
                for row in metastable_rows
            ],
            dtype=float,
        )
        standardized = standardize_matrix(feature_matrix)
        kmeans_labels = kmeans_two_clusters(standardized)
        hierarchical_labels = hierarchical_two_clusters(standardized)
        summary["kmeans_two_clusters"] = len(set(int(label) for label in kmeans_labels)) == 2
        summary["hierarchical_two_clusters"] = len(set(int(label) for label in hierarchical_labels)) == 2
        summary["repeats_across_seeds"] = all(unique_seed_count(metastable_rows, kmeans_labels, cluster_id) > 1 for cluster_id in sorted(set(int(label) for label in kmeans_labels)))
        summary["not_reducible_to_A0_split"] = all(cluster_contains_both_amplitudes(metastable_rows, kmeans_labels, cluster_id) for cluster_id in sorted(set(int(label) for label in kmeans_labels)))
        summary["second_pipe_detected"] = bool(
            summary["kmeans_two_clusters"]
            and summary["hierarchical_two_clusters"]
            and summary["repeats_across_seeds"]
            and summary["not_reducible_to_A0_split"]
        )
        summary["interpretation"] = (
            "First evidence for a second pipe inside the metastable ontology-local corridor."
            if summary["second_pipe_detected"]
            else "Metastable runs do not yet show a repeatable seed-stable two-family split that is independent of the A0 partition."
        )
        for row, kmeans_label, hierarchical_label in zip(metastable_rows, kmeans_labels, hierarchical_labels):
            cluster_rows.append(
                {
                    **row,
                    "kmeans_cluster": int(kmeans_label),
                    "hierarchical_cluster": int(hierarchical_label),
                }
            )

    write_csv(
        Path(args.features_csv).resolve(),
        run_rows,
        [
            "run_id",
            "seed",
            "A0",
            "width",
            "noise",
            param_a,
            param_b,
            "ontology_local_label",
            "legacy_classification",
            "peak_delta",
            "time_to_peak",
            "late_time_slope",
            "delta_at_end",
            "area_under_delta_curve",
            "number_of_reactivations",
            "residue_written",
            "residue_peak_time",
            "residue_decay_rate",
            "persistence_window",
            "notes",
        ],
    )
    write_csv(
        Path(args.clusters_csv).resolve(),
        cluster_rows,
        [
            "run_id",
            "seed",
            "A0",
            param_a,
            param_b,
            "ontology_local_label",
            "time_to_peak",
            "late_time_slope",
            "number_of_reactivations",
            "residue_decay_rate",
            "kmeans_cluster",
            "hierarchical_cluster",
            "notes",
        ],
    )
    write_json(
        Path(args.json_output).resolve(),
        {
            "date": "2026-04-04",
            "output_root": str(output_root),
            "summary": summary,
            "runs": run_rows,
            "metastable_clusters": cluster_rows,
        },
    )
    Path(args.md_output).resolve().write_text(
        render_markdown(output_root, run_rows, metastable_rows, cluster_rows, summary, param_a, param_b),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
