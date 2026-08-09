from __future__ import annotations

import hashlib
import json
import math
import platform
import shutil
import sys
import time
import warnings
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.special import softmax

warnings.filterwarnings("ignore")


@dataclass(frozen=True)
class CampaignConfig:
    campaign_id: str = "MPF_SIM_MECHANISM_ISOLATION_FAST_001"
    master_seed: int = 73190417
    temperatures: tuple = (0.08, 0.15, 0.25, 0.40)
    lambdas: tuple = tuple(np.round(np.linspace(0.10, 0.98, 8), 4))
    etas: tuple = tuple(np.round(np.linspace(0.025, 0.40, 6), 4))
    seeds_per_point: int = 8
    node_count: int = 48
    outgoing_edges: int = 6
    feature_dimension: int = 8
    steps: int = 700
    burn_in: int = 100
    beta_residue: float = 1.0
    beta_orientation: float = 0.35
    epsilon: float = -0.10
    noise_sd: float = 0.05
    history_lengths: tuple = (1, 2, 4, 8, 16, 32)
    calibration_fraction: float = 0.40
    minimum_relative_improvement: float = 0.02
    minimum_seed_consistency: float = 0.80
    minimum_effect_size: float = 0.30
    minimum_jsd: float = 0.05
    minimum_adjacent_grid_support: int = 3
    n_jobs: int = -1
    checkpoint_every: int = 128
    use_drive: bool = False


CFG = CampaignConfig()


@dataclass
class GraphWorld:
    destinations: np.ndarray
    edge_features: np.ndarray
    orientation: np.ndarray
    base_weights: np.ndarray


def derive_seed(*parts: Any) -> int:
    payload = "|".join(map(str, (CFG.master_seed,) + parts))
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little") % (2**32 - 1)


def safe_cosine_rows(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    vector_norm = np.linalg.norm(vector)
    row_norms = np.linalg.norm(matrix, axis=1)
    if vector_norm < 1e-12:
        return np.zeros(matrix.shape[0], dtype=float)
    denominator = np.maximum(row_norms * vector_norm, 1e-12)
    return (matrix @ vector) / denominator


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1.0)
    q = np.clip(np.asarray(q, dtype=float), 1e-12, 1.0)
    p /= p.sum()
    q /= q.sum()
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def standardized_effect(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    sd = values.std(ddof=1)
    if len(values) < 2 or sd < 1e-12:
        return 0.0
    return float(values.mean() / sd)


def build_world(seed: int) -> GraphWorld:
    rng = np.random.default_rng(seed)
    n = CFG.node_count
    degree = CFG.outgoing_edges
    d = CFG.feature_dimension
    destinations = np.empty((n, degree), dtype=np.int32)
    features = np.empty((n, degree, d), dtype=np.float64)
    base_weights = np.empty((n, degree), dtype=np.float64)
    for node in range(n):
        choices = np.delete(np.arange(n), node)
        destinations[node] = rng.choice(choices, size=degree, replace=False)
        features[node] = rng.normal(size=(degree, d))
        base_weights[node] = rng.normal(loc=0.0, scale=0.45, size=degree)
    flat = features.reshape(-1, d)
    flat = (flat - flat.mean(axis=0)) / np.maximum(flat.std(axis=0), 1e-9)
    features = flat.reshape(n, degree, d)
    orientation = rng.normal(size=d)
    orientation /= max(np.linalg.norm(orientation), 1e-12)
    return GraphWorld(destinations=destinations, edge_features=features, orientation=orientation, base_weights=base_weights)


def candidate_probabilities(
    world: GraphWorld,
    node: int,
    residue: np.ndarray,
    temperature: float,
    rng: np.random.Generator,
    add_noise: bool,
) -> np.ndarray:
    phi = world.edge_features[node]
    residue_alignment = safe_cosine_rows(phi, residue)
    orientation_alignment = phi @ world.orientation
    scores = world.base_weights[node] + CFG.beta_residue * residue_alignment + CFG.beta_orientation * orientation_alignment
    if add_noise:
        scores = scores + rng.normal(0.0, CFG.noise_sd, size=len(scores))
    admissible = scores > CFG.epsilon
    if not admissible.any():
        admissible[np.argmax(scores)] = True
    masked = np.full_like(scores, -1e9)
    masked[admissible] = scores[admissible]
    return softmax(masked / max(temperature, 1e-5))


def simulate_full_residue(temperature: float, residue_lambda: float, eta: float, seed: int) -> dict[str, Any]:
    world_seed = derive_seed("world", seed)
    run_seed = derive_seed("run", temperature, residue_lambda, eta, seed)
    world = build_world(world_seed)
    rng = np.random.default_rng(run_seed)
    node = int(rng.integers(CFG.node_count))
    residue = np.zeros(CFG.feature_dimension)
    feature_history: deque[np.ndarray] = deque(maxlen=max(CFG.history_lengths))
    records: list[dict[str, Any]] = []
    for t in range(CFG.steps):
        phi = world.edge_features[node]
        p_full = candidate_probabilities(world, node, residue, temperature, rng, add_noise=True)
        chosen_index = int(rng.choice(CFG.outgoing_edges, p=p_full))
        chosen_phi = phi[chosen_index].copy()
        zero_residue = np.zeros_like(residue)
        p_memoryless = candidate_probabilities(world, node, zero_residue, temperature, rng, add_noise=False)
        random_residue = rng.normal(size=CFG.feature_dimension)
        random_norm = np.linalg.norm(random_residue)
        target_norm = np.linalg.norm(residue)
        if random_norm > 1e-12:
            random_residue *= target_norm / random_norm
        p_random = candidate_probabilities(world, node, random_residue, temperature, rng, add_noise=False)
        shuffled_residue = residue[rng.permutation(CFG.feature_dimension)]
        p_shuffled = candidate_probabilities(world, node, shuffled_residue, temperature, rng, add_noise=False)
        finite_history_losses: dict[int, float] = {}
        finite_history_jsd: dict[int, float] = {}
        history_list = list(feature_history)
        for k in CFG.history_lengths:
            truncated = np.zeros(CFG.feature_dimension)
            for age, hist_phi in enumerate(reversed(history_list[-k:])):
                truncated += eta * (residue_lambda**age) * hist_phi
            p_k = candidate_probabilities(world, node, truncated, temperature, rng, add_noise=False)
            finite_history_losses[k] = -math.log(max(float(p_k[chosen_index]), 1e-12))
            finite_history_jsd[k] = js_divergence(p_full, p_k)
        if t >= CFG.burn_in:
            record = {
                "t": t,
                "chosen_index": chosen_index,
                "full_log_loss": -math.log(max(float(p_full[chosen_index]), 1e-12)),
                "memoryless_log_loss": -math.log(max(float(p_memoryless[chosen_index]), 1e-12)),
                "random_log_loss": -math.log(max(float(p_random[chosen_index]), 1e-12)),
                "shuffled_log_loss": -math.log(max(float(p_shuffled[chosen_index]), 1e-12)),
                "memoryless_jsd": js_divergence(p_full, p_memoryless),
                "random_jsd": js_divergence(p_full, p_random),
                "shuffled_jsd": js_divergence(p_full, p_shuffled),
                "residue_norm": float(np.linalg.norm(residue)),
            }
            for k in CFG.history_lengths:
                record[f"history_{k}_log_loss"] = finite_history_losses[k]
                record[f"history_{k}_jsd"] = finite_history_jsd[k]
            records.append(record)
        feature_history.append(chosen_phi)
        residue = residue_lambda * residue + eta * chosen_phi
        node = int(world.destinations[node, chosen_index])
    frame = pd.DataFrame(records)
    calibration_cut = max(1, int(len(frame) * CFG.calibration_fraction))
    calibration = frame.iloc[:calibration_cut]
    test = frame.iloc[calibration_cut:]
    history_scores = {k: calibration[f"history_{k}_log_loss"].mean() for k in CFG.history_lengths}
    best_k = min(history_scores, key=history_scores.get)
    full_loss = float(test["full_log_loss"].mean())
    memoryless_loss = float(test["memoryless_log_loss"].mean())
    random_loss = float(test["random_log_loss"].mean())
    shuffled_loss = float(test["shuffled_log_loss"].mean())
    finite_loss = float(test[f"history_{best_k}_log_loss"].mean())
    strongest_control_loss = min(memoryless_loss, random_loss, shuffled_loss, finite_loss)
    relative_improvement = (strongest_control_loss - full_loss) / max(strongest_control_loss, 1e-12)
    return {
        "temperature": temperature,
        "lambda": residue_lambda,
        "eta": eta,
        "seed": seed,
        "full_log_loss": full_loss,
        "memoryless_log_loss": memoryless_loss,
        "random_log_loss": random_loss,
        "shuffled_log_loss": shuffled_loss,
        "finite_history_log_loss": finite_loss,
        "best_history_k": int(best_k),
        "strongest_control_log_loss": strongest_control_loss,
        "relative_improvement": float(relative_improvement),
        "paired_future_jsd": float(test["memoryless_jsd"].mean()),
        "random_residue_jsd": float(test["random_jsd"].mean()),
        "shuffled_residue_jsd": float(test["shuffled_jsd"].mean()),
        "finite_history_jsd": float(test[f"history_{best_k}_jsd"].mean()),
        "mean_residue_norm": float(test["residue_norm"].mean()),
        "beats_memoryless": bool(full_loss < memoryless_loss),
        "beats_random": bool(full_loss < random_loss),
        "beats_shuffled": bool(full_loss < shuffled_loss),
        "beats_finite_history": bool(full_loss < finite_loss),
    }


def aggregate_group(group: pd.DataFrame) -> pd.Series:
    values = group["relative_improvement"].to_numpy()
    seed_consistency = float(np.mean(values >= CFG.minimum_relative_improvement))
    effect = standardized_effect(values)
    finite_win_rate = float(group["beats_finite_history"].mean())
    shuffled_win_rate = float(group["beats_shuffled"].mean())
    random_win_rate = float(group["beats_random"].mean())
    if len(values) >= 2:
        temperature, residue_lambda, eta = group.name
        rng = np.random.default_rng(derive_seed("bootstrap", temperature, residue_lambda, eta))
        boot_means = []
        for _ in range(1000):
            sample = rng.choice(values, size=len(values), replace=True)
            boot_means.append(sample.mean())
        ci_low, ci_high = np.quantile(boot_means, [0.025, 0.975])
    else:
        ci_low = ci_high = values.mean()
    return pd.Series(
        {
            "mean_relative_improvement": values.mean(),
            "median_relative_improvement": np.median(values),
            "improvement_ci_low": ci_low,
            "improvement_ci_high": ci_high,
            "seed_consistency": seed_consistency,
            "standardized_effect": effect,
            "mean_jsd": group["paired_future_jsd"].mean(),
            "finite_history_win_rate": finite_win_rate,
            "shuffled_win_rate": shuffled_win_rate,
            "random_win_rate": random_win_rate,
            "mean_best_history_k": group["best_history_k"].mean(),
        }
    )


def build_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    summary = metrics.groupby(["temperature", "lambda", "eta"], as_index=False).apply(aggregate_group, include_groups=False).reset_index(drop=True)
    summary["candidate_stable"] = (
        (summary["mean_relative_improvement"] >= CFG.minimum_relative_improvement)
        & (summary["seed_consistency"] >= CFG.minimum_seed_consistency)
        & (summary["standardized_effect"] >= CFG.minimum_effect_size)
        & (summary["mean_jsd"] >= CFG.minimum_jsd)
        & (summary["improvement_ci_low"] > 0)
        & (summary["finite_history_win_rate"] >= 0.75)
        & (summary["shuffled_win_rate"] >= 0.75)
        & (summary["random_win_rate"] >= 0.75)
    )
    lambda_values = sorted(summary["lambda"].unique())
    eta_values = sorted(summary["eta"].unique())
    lambda_index = {value: i for i, value in enumerate(lambda_values)}
    eta_index = {value: i for i, value in enumerate(eta_values)}
    summary["adjacent_stable_support"] = 0
    for temperature in CFG.temperatures:
        subset = summary[summary["temperature"] == temperature]
        stable_lookup = {
            (lambda_index[row["lambda"]], eta_index[row["eta"]]): bool(row["candidate_stable"])
            for _, row in subset.iterrows()
        }
        for idx, row in subset.iterrows():
            li = lambda_index[row["lambda"]]
            ei = eta_index[row["eta"]]
            neighbor_count = 0
            for dli, dei in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                if stable_lookup.get((li + dli, ei + dei), False):
                    neighbor_count += 1
            summary.loc[idx, "adjacent_stable_support"] = neighbor_count
    summary["stable_region"] = summary["candidate_stable"] & (summary["adjacent_stable_support"] >= CFG.minimum_adjacent_grid_support)
    return summary


def main() -> None:
    root = Path("outputs/replications") / f"{CFG.campaign_id}_codex_reproduction"
    data = root / "data"
    root.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)

    config_text = json.dumps(asdict(CFG), indent=2, default=list)
    config_hash = hashlib.sha256(config_text.encode("utf-8")).hexdigest()
    (root / "campaign.json").write_text(config_text)
    (root / "config_sha256.txt").write_text(config_hash)

    test_a = simulate_full_residue(0.15, 0.80, 0.15, 0)
    test_b = simulate_full_residue(0.15, 0.80, 0.15, 0)
    if test_a != test_b:
        raise RuntimeError("Deterministic replay failed.")
    if not np.isfinite(test_a["relative_improvement"]):
        raise RuntimeError("Metric finiteness failed.")
    if not 0 <= test_a["paired_future_jsd"] <= math.log(2) + 1e-8:
        raise RuntimeError("JSD bounds failed.")

    registry = [
        {"temperature": float(temperature), "lambda": float(residue_lambda), "eta": float(eta), "seed": int(seed)}
        for temperature in CFG.temperatures
        for residue_lambda in CFG.lambdas
        for eta in CFG.etas
        for seed in range(CFG.seeds_per_point)
    ]
    pd.DataFrame(registry).to_parquet(data / "run_registry.parquet", index=False)

    start_time = time.time()
    checkpoint_file = data / "checkpoint_metrics.parquet"
    if checkpoint_file.exists():
        checkpoint_file.unlink()

    all_results = []
    for batch_start in range(0, len(registry), CFG.checkpoint_every):
        batch = registry[batch_start : batch_start + CFG.checkpoint_every]
        batch_results = Parallel(n_jobs=CFG.n_jobs, backend="loky", verbose=0)(
            delayed(simulate_full_residue)(item["temperature"], item["lambda"], item["eta"], item["seed"]) for item in batch
        )
        all_results.extend(batch_results)
        pd.DataFrame(all_results).to_parquet(checkpoint_file, index=False)
        completed = len(all_results)
        elapsed = time.time() - start_time
        print(f"Completed {completed}/{len(registry)} ({100 * completed / len(registry):.1f}%) in {elapsed / 60:.1f} minutes", flush=True)

    metrics = pd.DataFrame(all_results)
    metrics.to_parquet(data / "full_metrics.parquet", index=False)
    metrics.to_csv(data / "full_metrics.csv", index=False)

    summary = build_summary(metrics)
    summary.to_parquet(data / "parameter_surface.parquet", index=False)
    summary.to_csv(data / "parameter_surface.csv", index=False)

    stable_points = summary[summary["stable_region"]]
    candidate_points = summary[summary["candidate_stable"]]
    stable_fraction = float(summary["stable_region"].mean())
    candidate_fraction = float(summary["candidate_stable"].mean())
    best_row = summary.sort_values(["stable_region", "seed_consistency", "mean_relative_improvement"], ascending=False).iloc[0]

    if len(stable_points) > 0:
        final_outcome = "CONTIGUOUS_STABLE_REGION_DETECTED"
        next_campaign = "MPF_SIM_INDEPENDENT_REPLICATION_001"
        reason = "At least one temperature slice contains residue-supporting points with adjacent-grid stability."
    elif len(candidate_points) > 0:
        final_outcome = "ISOLATED_CANDIDATE_POINTS_ONLY"
        next_campaign = "MPF_SIM_LOCAL_REFINEMENT_001"
        reason = "Some parameter points passed individual criteria, but no contiguous stable region was detected."
    elif best_row["mean_relative_improvement"] >= CFG.minimum_relative_improvement:
        final_outcome = "POSITIVE_BUT_SEED_UNSTABLE"
        next_campaign = "MPF_SIM_VARIANCE_SOURCE_AUDIT_001"
        reason = "A positive mean signal exists, but cross-seed or control requirements were not satisfied."
    else:
        final_outcome = "NO_OPERATIONAL_RESIDUE_REGION"
        next_campaign = "MPF_SIM_MODEL_REVISION_001"
        reason = "No sampled region produced a practically meaningful and control-resistant residue advantage."

    recommendation = {
        "campaign_id": CFG.campaign_id,
        "outcome": final_outcome,
        "next_campaign": next_campaign,
        "reason": reason,
        "stable_fraction": stable_fraction,
        "candidate_fraction": candidate_fraction,
        "stable_point_count": int(len(stable_points)),
        "candidate_point_count": int(len(candidate_points)),
        "total_parameter_points": int(len(summary)),
        "best_observed_point": {
            "temperature": float(best_row["temperature"]),
            "lambda": float(best_row["lambda"]),
            "eta": float(best_row["eta"]),
            "mean_relative_improvement": float(best_row["mean_relative_improvement"]),
            "seed_consistency": float(best_row["seed_consistency"]),
            "standardized_effect": float(best_row["standardized_effect"]),
            "mean_jsd": float(best_row["mean_jsd"]),
            "finite_history_win_rate": float(best_row["finite_history_win_rate"]),
            "adjacent_stable_support": int(best_row["adjacent_stable_support"]),
        },
        "governance": "Exploratory computational evidence only. This campaign does not establish ontology or external physical validity.",
    }
    (root / "recommend_next_campaign.json").write_text(json.dumps(recommendation, indent=2))

    runtime_seconds = time.time() - start_time
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "runtime_seconds": runtime_seconds,
        "configuration_sha256": config_hash,
    }
    (root / "environment.json").write_text(json.dumps(environment, indent=2))

    report = f"""# Falsification Report: {CFG.campaign_id}

Outcome classification: `{final_outcome}`

## Direction

This local Codex reproduction ran the notebook logic supplied by the user on the local workstation and wrote fresh metrics into `outputs/replications`.

## Results

- Parameter points: {len(summary)}
- Seed-level run blocks: {len(metrics)}
- Candidate stable points: {len(candidate_points)}
- Contiguous stable points: {len(stable_points)}
- Stable fraction: {stable_fraction:.4f}
- Runtime seconds: {runtime_seconds:.2f}

## Best observed point

- Temperature: {best_row["temperature"]}
- Lambda: {best_row["lambda"]}
- Eta: {best_row["eta"]}
- Mean relative improvement: {best_row["mean_relative_improvement"]:.6f}
- Seed consistency: {best_row["seed_consistency"]:.3f}
- Standardized effect: {best_row["standardized_effect"]:.3f}
- Mean paired-future JSD: {best_row["mean_jsd"]:.6f}
- Finite-history win rate: {best_row["finite_history_win_rate"]:.3f}
- Adjacent stable support: {int(best_row["adjacent_stable_support"])}

## Decision

Next campaign: `{next_campaign}`

Reason: {reason}

## Governance

Exploratory computational evidence only. These results do not prove the framework, establish physical residue, or establish external physical validity.
"""
    (root / "falsification_report.md").write_text(report.strip())
    archive_path = shutil.make_archive(str(root), "zip", root_dir=root.parent, base_dir=root.name)
    print(json.dumps(recommendation, indent=2))
    print(f"Evidence package: {archive_path}")


if __name__ == "__main__":
    main()
