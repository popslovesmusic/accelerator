#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "artifacts" / "runs"


def load_config(config_path: Path) -> tuple[dict, str]:
    raw_text = config_path.read_text(encoding="utf-8")
    return json.loads(raw_text), raw_text


def get_code_version() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "untracked"


def compute_sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ensure_run_directory(root: Path, run_id: str) -> Path:
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scenario_fields(scenario_id: str, width: int, height: int) -> tuple[list[list[float]], list[list[float]], list[list[float]], list[list[int]]]:
    center = (height - 1) / 2.0
    mismatch = [[0.0 for _ in range(width)] for _ in range(height)]
    target_a = [[0.0 for _ in range(width)] for _ in range(height)]
    target_b = [[0.0 for _ in range(width)] for _ in range(height)]
    operators = [[0 for _ in range(width)] for _ in range(height)]

    for y in range(height):
        for x in range(width):
            xn = x / max(1, width - 1)
            yn = y / max(1, height - 1)
            dy = (y - center) / max(1.0, height / 2.0)
            corridor_band = math.exp(-(dy / 0.28) ** 2)
            ridge = math.exp(-((xn - 0.55) / 0.11) ** 2)
            barrier = math.exp(-((xn - 0.50) / 0.075) ** 2)

            base_mismatch = 0.18 + 0.65 * abs(dy) + 0.05 * (1.0 - corridor_band)
            smooth_wave = 0.03 * math.sin(2.0 * math.pi * xn) * math.cos(math.pi * yn)
            base_target = 0.26 + 0.18 * xn + 0.08 * dy

            if scenario_id == "corridor":
                mismatch_value = base_mismatch + 0.04 * ridge - 0.12 * corridor_band + smooth_wave
                divergence_offset = 0.03 + 0.02 * ridge
                operator_value = 1 if abs(dy) < 0.33 else 0
            elif scenario_id == "shelf_transition":
                mismatch_value = base_mismatch + 0.18 * ridge + 0.02 * math.sin(4.0 * math.pi * xn) - 0.08 * corridor_band
                divergence_offset = 0.05 + 0.10 * ridge + 0.03 * max(0.0, xn - 0.45)
                operator_value = 1 if abs(dy) < 0.25 else (2 if xn > 0.52 else 0)
            elif scenario_id == "decoupling":
                mismatch_value = base_mismatch + 0.30 * barrier + 0.10 * ridge - 0.04 * corridor_band
                divergence_offset = 0.07 + 0.22 * barrier + 0.08 * max(0.0, xn - 0.40)
                operator_value = 3 if barrier > 0.35 else (2 if abs(dy) < 0.30 else 0)
            else:
                raise ValueError(f"Unsupported scenario_id: {scenario_id}")

            mismatch[y][x] = max(0.02, mismatch_value)
            target_a[y][x] = min(0.95, max(0.05, base_target))
            target_b[y][x] = min(0.98, max(0.08, base_target + divergence_offset))
            operators[y][x] = operator_value

    return mismatch, target_a, target_b, operators


def neighbors(x: int, y: int, width: int, height: int) -> list[tuple[int, int, float]]:
    points: list[tuple[int, int, float]] = []
    for dx, dy in ((1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1)):
        nx = x + dx
        ny = y + dy
        if 0 <= nx < width and 0 <= ny < height:
            distance = math.sqrt(2.0) if dx != 0 and dy != 0 else 1.0
            points.append((nx, ny, distance))
    return points


def shortest_path(
    mismatch: list[list[float]],
    target_a: list[list[float]],
    target_b: list[list[float]],
    operators: list[list[int]],
    row_bias: int,
    weights: dict,
) -> tuple[list[tuple[int, int]], float]:
    height = len(mismatch)
    width = len(mismatch[0])
    start = (0, max(0, min(height - 1, row_bias)))
    goal = (width - 1, max(0, min(height - 1, row_bias)))
    distances: dict[tuple[int, int], float] = {start: 0.0}
    previous: dict[tuple[int, int], tuple[int, int]] = {}
    heap: list[tuple[float, tuple[int, int]]] = [(0.0, start)]

    while heap:
        current_cost, current = heapq.heappop(heap)
        if current == goal:
            break
        if current_cost > distances[current]:
            continue
        x, y = current
        for nx, ny, step_distance in neighbors(x, y, width, height):
            local_divergence = abs(target_a[ny][nx] - target_b[ny][nx])
            operator_penalty = 1.0 if operators[ny][nx] != operators[y][x] else 0.0
            step_cost = step_distance * (
                1.0
                + weights["mismatch"] * mismatch[ny][nx]
                + weights["reference_divergence"] * local_divergence
                + weights["operator_switch"] * operator_penalty
            )
            next_cost = current_cost + step_cost
            neighbor_key = (nx, ny)
            if next_cost < distances.get(neighbor_key, float("inf")):
                distances[neighbor_key] = next_cost
                previous[neighbor_key] = current
                heapq.heappush(heap, (next_cost, neighbor_key))

    if goal not in previous and goal != start:
        raise RuntimeError("Failed to construct a relational geodesic path.")

    path = [goal]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    return path, distances[goal]


def transport_path(
    path: list[tuple[int, int]],
    mismatch: list[list[float]],
    target_field: list[list[float]],
    operators: list[list[int]],
    gain: float,
    operator_gain: float,
    mismatch_gain: float,
) -> tuple[list[float], list[float], list[int]]:
    start_x, start_y = path[0]
    ref = target_field[start_y][start_x]
    references = [ref]
    deltas = [0.0]
    switches = [0]

    for index in range(1, len(path)):
        prev_x, prev_y = path[index - 1]
        x, y = path[index]
        target_next = target_field[y][x]
        predicted = ref + gain * (target_next - ref)
        operator_switch = 1 if operators[y][x] != operators[prev_y][prev_x] else 0
        direction = 1.0 if target_next >= predicted else -1.0
        actual = predicted + direction * (
            operator_gain * operator_switch + mismatch_gain * mismatch[y][x]
        )
        actual = min(1.0, max(0.0, actual))
        delta_t = abs(actual - predicted)
        ref = actual
        references.append(ref)
        deltas.append(delta_t)
        switches.append(operator_switch)

    return references, deltas, switches


def summarize_scenario(config: dict, scenario: dict) -> tuple[dict, list[dict], list[list[float]], list[tuple[int, int]]]:
    grid = config["grid"]
    weights = config["cost_weights"]
    transport = config["transport"]
    width = int(grid["width"])
    height = int(grid["height"])
    row_bias = int(grid["row_bias"])

    mismatch, target_a, target_b, operators = scenario_fields(scenario["id"], width, height)
    path, geodesic_cost = shortest_path(mismatch, target_a, target_b, operators, row_bias, weights)

    refs_a, deltas_a, switches_a = transport_path(
        path,
        mismatch,
        target_a,
        operators,
        float(transport["gain"]),
        float(transport["operator_gain"]),
        float(transport["mismatch_gain"]),
    )
    refs_b, deltas_b, switches_b = transport_path(
        path,
        mismatch,
        target_b,
        operators,
        float(transport["gain"]),
        float(transport["operator_gain"]),
        float(transport["mismatch_gain"]),
    )

    tau = float(transport["alignment_tau"])
    hotspot_threshold = float(transport["hotspot_kappa_threshold"])
    lambda_weight = float(transport["curvature_lambda"])

    path_rows: list[dict] = []
    alignment_values: list[float] = []
    delta_t_values: list[float] = []
    kappa_values: list[float] = []
    accumulated_mismatch = 0.0

    for index, (x, y) in enumerate(path):
        alignment = abs(refs_a[index] - refs_b[index])
        delta_t = 0.5 * (deltas_a[index] + deltas_b[index])
        previous_alignment = alignment_values[-1] if alignment_values else alignment
        d_align = abs(alignment - previous_alignment)
        kappa = d_align + lambda_weight * delta_t
        accumulated_mismatch += mismatch[y][x]
        alignment_values.append(alignment)
        delta_t_values.append(delta_t)
        kappa_values.append(kappa)
        path_rows.append(
            {
                "scenario_id": scenario["id"],
                "step": index,
                "x": x,
                "y": y,
                "mismatch": mismatch[y][x],
                "target_ref_a": target_a[y][x],
                "target_ref_b": target_b[y][x],
                "ref_a": refs_a[index],
                "ref_b": refs_b[index],
                "delta_align": alignment,
                "delta_t": delta_t,
                "kappa": kappa,
                "operator_state": operators[y][x],
                "operator_switch": max(switches_a[index], switches_b[index]),
            }
        )

    delta_align_mean = sum(alignment_values) / len(alignment_values)
    delta_align_max = max(alignment_values)
    delta_t_mean = sum(delta_t_values) / len(delta_t_values)
    delta_t_max = max(delta_t_values)
    kappa_mean = sum(kappa_values) / len(kappa_values)
    kappa_max = max(kappa_values)
    operator_switch_rate = sum(max(a, b) for a, b in zip(switches_a, switches_b)) / len(path)
    hotspot_count = sum(1 for value in kappa_values if value >= hotspot_threshold)
    decoupling_events = sum(1 for value in alignment_values if value > tau)

    if delta_align_max > tau or hotspot_count > 0 or decoupling_events > 0:
        observed_regime = "decoupling"
    elif delta_align_mean > tau * 0.35 or kappa_mean > hotspot_threshold * 0.20:
        observed_regime = "shelf_transition"
    else:
        observed_regime = "corridor"

    summary = {
        "run_id": config["run_id"],
        "scenario_id": scenario["id"],
        "scenario_label": scenario["label"],
        "designed_regime": scenario["label"],
        "observed_regime": observed_regime,
        "path_length": len(path),
        "geodesic_cost": geodesic_cost,
        "accumulated_mismatch": accumulated_mismatch,
        "delta_align_mean": delta_align_mean,
        "delta_align_max": delta_align_max,
        "delta_t_mean": delta_t_mean,
        "delta_t_max": delta_t_max,
        "operator_switch_rate": operator_switch_rate,
        "kappa_mean": kappa_mean,
        "kappa_max": kappa_max,
        "curvature_hotspots": hotspot_count,
        "corridor_count": 1 if observed_regime == "corridor" else 0,
        "decoupling_events": decoupling_events,
        "alignment_tau": tau,
        "hotspot_kappa_threshold": hotspot_threshold,
    }
    return summary, path_rows, mismatch, path


def plot_scenarios(
    config: dict,
    scenario_outputs: list[tuple[dict, list[dict], list[list[float]], list[tuple[int, int]]]],
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, len(scenario_outputs), figsize=(15, 4.8))
    if len(scenario_outputs) == 1:
        axes = [axes]

    for axis, (summary, _, mismatch, path) in zip(axes, scenario_outputs):
        axis.imshow(mismatch, cmap="viridis", origin="lower")
        xs = [point[0] for point in path]
        ys = [point[1] for point in path]
        axis.plot(xs, ys, color="white", linewidth=2.0)
        axis.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], c=["cyan", "red"], s=20)
        axis.set_title(
            f"{summary['scenario_label']}\nobs={summary['observed_regime']}\n"
            f"k_mean={summary['kappa_mean']:.3f}, d_max={summary['delta_align_max']:.3f}"
        )
        axis.set_xticks([])
        axis.set_yticks([])

    fig.suptitle("Paper 2 relational geodesic prototype")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def write_run_summary(path: Path, manifest: dict, summaries: list[dict], figure_name: str) -> None:
    lines = [
        f"# Run Summary: {manifest['run_id']}",
        "",
        "## Identity",
        "",
        f"- `run_id`: `{manifest['run_id']}`",
        f"- `equation_mode`: `{manifest['equation_mode']}`",
        f"- `experiment_family`: `{manifest['experiment_family']}`",
        f"- `timestamp_utc`: `{manifest['timestamp_utc']}`",
        f"- `code_version`: `{manifest['code_version']}`",
        f"- `config_path`: `{manifest['config_path']}`",
        f"- `config_sha256`: `{manifest['config_sha256']}`",
        f"- `seed`: `{manifest['seed']}`",
        "",
        "## Scenario Outcomes",
        "",
    ]
    for summary in summaries:
        lines.extend(
            [
                f"### {summary['scenario_id']}",
                "",
                f"- `designed_regime`: `{summary['designed_regime']}`",
                f"- `observed_regime`: `{summary['observed_regime']}`",
                f"- `geodesic_cost`: `{summary['geodesic_cost']}`",
                f"- `delta_align_max`: `{summary['delta_align_max']}`",
                f"- `delta_t_mean`: `{summary['delta_t_mean']}`",
                f"- `kappa_mean`: `{summary['kappa_mean']}`",
                f"- `kappa_max`: `{summary['kappa_max']}`",
                f"- `curvature_hotspots`: `{summary['curvature_hotspots']}`",
                f"- `decoupling_events`: `{summary['decoupling_events']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Files",
            "",
            "- `run_manifest.json`",
            "- `config_snapshot.json`",
            "- `scenario_summary.csv`",
            "- `path_metrics.csv`",
            f"- `{figure_name}`",
            "- `run_summary.md`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Paper 2 relational geodesic prototype.")
    parser.add_argument(
        "config",
        nargs="?",
        default=str(REPO_ROOT / "sim" / "configs" / "paper2_relational_geodesic_prototype_v1.json"),
        help="Path to the Paper 2 prototype config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config, raw_text = load_config(config_path)

    run_dir = ensure_run_directory(RUNS_ROOT, config["run_id"])
    figure_name = "figure_relational_geodesic_regimes.png"
    figure_run_path = run_dir / figure_name
    figure_doc_path = REPO_ROOT / "docs" / "manuscript" / "paper2" / "fig1_relational_geodesic_regimes.png"

    scenario_outputs = [summarize_scenario(config, scenario) for scenario in config["scenarios"]]
    summaries = [item[0] for item in scenario_outputs]
    path_rows = [row for _, rows, _, _ in scenario_outputs for row in rows]

    manifest = {
        "run_id": config["run_id"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "code_version": get_code_version(),
        "config_path": str(config_path.relative_to(REPO_ROOT)),
        "config_sha256": compute_sha256(raw_text),
        "seed": config["seed"],
        "equation_mode": config["equation_mode"],
        "experiment_family": config["experiment_family"],
        "notes": config["notes"],
    }

    write_json(run_dir / "run_manifest.json", manifest)
    write_json(run_dir / "config_snapshot.json", config)
    write_csv(run_dir / "scenario_summary.csv", list(summaries[0].keys()), summaries)
    write_csv(run_dir / "path_metrics.csv", list(path_rows[0].keys()), path_rows)
    plot_scenarios(config, scenario_outputs, figure_run_path)
    plot_scenarios(config, scenario_outputs, figure_doc_path)
    write_run_summary(run_dir / "run_summary.md", manifest, summaries, figure_name)
    print(run_dir)


if __name__ == "__main__":
    main()
