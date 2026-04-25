#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.pyplot as plt


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS_ROOT = REPO_ROOT / "artifacts" / "runs"


Q_TO_DIR: dict[str, tuple[int, int]] = {
    "++": (1, 1),
    "+-": (1, -1),
    "-+": (-1, 1),
    "--": (-1, -1),
}


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


def scenario_mismatch_field(scenario_id: str, width: int, height: int) -> list[list[float]]:
    center = (height - 1) / 2.0
    mismatch = [[0.0 for _ in range(width)] for _ in range(height)]
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

            if scenario_id == "corridor":
                mismatch_value = base_mismatch + 0.04 * ridge - 0.12 * corridor_band + smooth_wave
            elif scenario_id == "shelf_transition":
                mismatch_value = base_mismatch + 0.18 * ridge + 0.02 * math.sin(4.0 * math.pi * xn) - 0.08 * corridor_band
            elif scenario_id == "decoupling":
                mismatch_value = base_mismatch + 0.30 * barrier + 0.10 * ridge - 0.04 * corridor_band
            else:
                raise ValueError(f"Unsupported scenario_id: {scenario_id}")

            mismatch[y][x] = max(0.02, mismatch_value)
    return mismatch


def finite_difference_grad(mismatch: list[list[float]], x: int, y: int) -> tuple[float, float]:
    height = len(mismatch)
    width = len(mismatch[0])

    x0 = max(0, x - 1)
    x1 = min(width - 1, x + 1)
    y0 = max(0, y - 1)
    y1 = min(height - 1, y + 1)

    if x1 == x0:
        gx = 0.0
    elif x0 == x:
        gx = mismatch[y][x1] - mismatch[y][x]
    elif x1 == x:
        gx = mismatch[y][x] - mismatch[y][x0]
    else:
        gx = 0.5 * (mismatch[y][x1] - mismatch[y][x0])

    if y1 == y0:
        gy = 0.0
    elif y0 == y:
        gy = mismatch[y1][x] - mismatch[y][x]
    elif y1 == y:
        gy = mismatch[y][x] - mismatch[y0][x]
    else:
        gy = 0.5 * (mismatch[y1][x] - mismatch[y0][x])

    return gx, gy


def dir_angle(dx: int, dy: int) -> float:
    angle = math.atan2(float(dy), float(dx))
    if angle < 0:
        angle += 2.0 * math.pi
    return angle


def pick_local_operator(
    mismatch: list[list[float]],
    x: int,
    y: int,
    grad_x: float,
    grad_y: float,
    selection_cost: dict,
) -> tuple[str, str, int, int, float, float, int]:
    height = len(mismatch)
    width = len(mismatch[0])
    w_next = float(selection_cost["w_mismatch_next"])
    w_uphill = float(selection_cost["w_uphill_grad"])
    w_Lminus = float(selection_cost["w_L_minus"])
    oob_penalty = float(selection_cost["oob_penalty"])
    degeneracy_abs_tol = float(selection_cost.get("degeneracy_abs_tol", 0.0))
    degeneracy_rel_tol = float(selection_cost.get("degeneracy_rel_tol", 0.0))

    best_cost = float("inf")
    best_L = "+"
    best_Q = "++"
    best_dx = 1
    best_dy = 1
    all_costs: list[float] = []

    grad_norm = math.hypot(grad_x, grad_y)
    if grad_norm <= 0:
        grad_unit_x, grad_unit_y = 0.0, 0.0
    else:
        grad_unit_x, grad_unit_y = grad_x / grad_norm, grad_y / grad_norm

    for L in ("+", "-"):
        for Q, (dx, dy) in Q_TO_DIR.items():
            step_dx, step_dy = (dx, dy) if L == "+" else (-dx, -dy)
            nx = x + step_dx
            ny = y + step_dy
            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                candidate_cost = oob_penalty
            else:
                step_norm = math.hypot(step_dx, step_dy)
                dir_unit_x = step_dx / step_norm
                dir_unit_y = step_dy / step_norm
                # "Uphill" score is positive when moving in the direction of increasing mismatch.
                uphill_score = max(0.0, grad_unit_x * dir_unit_x + grad_unit_y * dir_unit_y)
                candidate_cost = w_next * mismatch[ny][nx] + w_uphill * uphill_score + (w_Lminus if L == "-" else 0.0)
            all_costs.append(candidate_cost)

            # Deterministic tie-break: prefer '+' then lexicographic Q.
            if candidate_cost < best_cost - 1e-12:
                best_cost = candidate_cost
                best_L, best_Q = L, Q
                best_dx, best_dy = step_dx, step_dy
            elif abs(candidate_cost - best_cost) <= 1e-12:
                if best_L == "-" and L == "+":
                    best_cost = candidate_cost
                    best_L, best_Q = L, Q
                    best_dx, best_dy = step_dx, step_dy
                elif L == best_L and Q < best_Q:
                    best_cost = candidate_cost
                    best_L, best_Q = L, Q
                    best_dx, best_dy = step_dx, step_dy

    # Degeneracy: count operators within tolerance of the minimum.
    tol = max(degeneracy_abs_tol, degeneracy_rel_tol * max(1.0, abs(best_cost)))
    degeneracy_count = sum(1 for value in all_costs if value <= best_cost + tol)

    sorted_costs = sorted(all_costs)
    second_best = sorted_costs[1] if len(sorted_costs) > 1 else best_cost
    gap_to_second = second_best - best_cost

    return best_L, best_Q, best_dx, best_dy, best_cost, gap_to_second, degeneracy_count


def compute_i_field(config: dict, scenario: dict) -> tuple[dict, list[dict], list[list[float]], list[list[float]], list[list[float]], list[list[int]], list[list[int]]]:
    width = int(config["grid"]["width"])
    height = int(config["grid"]["height"])
    selection_cost = config["selection_cost"]

    mismatch = scenario_mismatch_field(scenario["id"], width, height)
    grad_x_field = [[0.0 for _ in range(width)] for _ in range(height)]
    grad_y_field = [[0.0 for _ in range(width)] for _ in range(height)]
    dx_field = [[0 for _ in range(width)] for _ in range(height)]
    dy_field = [[0 for _ in range(width)] for _ in range(height)]
    angle_field = [[0.0 for _ in range(width)] for _ in range(height)]
    degeneracy_field = [[0 for _ in range(width)] for _ in range(height)]
    gap_field = [[0.0 for _ in range(width)] for _ in range(height)]

    rows: list[dict] = []
    for y in range(height):
        for x in range(width):
            gx, gy = finite_difference_grad(mismatch, x, y)
            grad_x_field[y][x] = gx
            grad_y_field[y][x] = gy
            L, Q, dx, dy, mu_min, gap_to_second, degeneracy_count = pick_local_operator(
                mismatch, x, y, gx, gy, selection_cost
            )
            dx_field[y][x] = dx
            dy_field[y][x] = dy
            angle = dir_angle(dx, dy)
            angle_field[y][x] = angle
            degeneracy_field[y][x] = degeneracy_count
            gap_field[y][x] = gap_to_second
            rows.append(
                {
                    "scenario_id": scenario["id"],
                    "x": x,
                    "y": y,
                    "mismatch": mismatch[y][x],
                    "grad_x": gx,
                    "grad_y": gy,
                    "chosen_L": L,
                    "chosen_Q": Q,
                    "dir_dx": dx,
                    "dir_dy": dy,
                    "i_angle_rad": angle,
                    "mu_min": mu_min,
                    "mu_gap_to_second": gap_to_second,
                    "degeneracy_count": degeneracy_count,
                }
            )

    mean_mu = sum(row["mu_min"] for row in rows) / len(rows)
    degenerate_fraction = sum(1 for row in rows if int(row["degeneracy_count"]) > 1) / len(rows)
    mean_gap = sum(row["mu_gap_to_second"] for row in rows) / len(rows)
    summary = {
        "run_id": config["run_id"],
        "scenario_id": scenario["id"],
        "scenario_label": scenario["label"],
        "grid_width": width,
        "grid_height": height,
        "mu_min_mean": mean_mu,
        "mu_min_min": min(row["mu_min"] for row in rows),
        "mu_min_max": max(row["mu_min"] for row in rows),
        "degenerate_fraction": degenerate_fraction,
        "mu_gap_to_second_mean": mean_gap,
        "notes": "O* computed as argmin over (L,Q) with a simple next-cell + uphill-gradient penalty cost; degeneracy counts operators within tolerance of the local minimum.",
    }

    return summary, rows, mismatch, grad_x_field, grad_y_field, dx_field, dy_field


def plot_degeneracy_map(
    scenario_outputs: list[tuple[dict, list[dict], list[list[float]], list[list[float]], list[list[float]], list[list[int]], list[list[int]]]],
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, len(scenario_outputs), figsize=(15, 4.8))
    if len(scenario_outputs) == 1:
        axes = [axes]

    for axis, (summary, rows, mismatch, _, _, _, _) in zip(axes, scenario_outputs):
        width = int(summary["grid_width"])
        height = int(summary["grid_height"])
        deg = [[0 for _ in range(width)] for _ in range(height)]
        for row in rows:
            deg[int(row["y"])][int(row["x"])] = int(row["degeneracy_count"])

        img = axis.imshow(deg, cmap="magma", origin="lower", vmin=1)
        axis.set_title(f"{summary['scenario_label']}\nfrac_deg={summary['degenerate_fraction']:.3f}")
        axis.set_xticks([])
        axis.set_yticks([])
        # Subtle contour to keep the mismatch geometry visible.
        axis.contour(mismatch, levels=8, colors="white", linewidths=0.3, alpha=0.35, origin="lower")

        fig.colorbar(img, ax=axis, fraction=0.046, pad=0.04, label="degeneracy_count")

    fig.suptitle("Paper 3: degeneracy map (near-tied local argmin count)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_quiver(
    scenario_outputs: list[tuple[dict, list[dict], list[list[float]], list[list[float]], list[list[float]], list[list[int]], list[list[int]]]],
    output_path: Path,
    stride: int,
    scale: float,
) -> None:
    fig, axes = plt.subplots(1, len(scenario_outputs), figsize=(15, 4.8))
    if len(scenario_outputs) == 1:
        axes = [axes]

    for axis, (summary, _, mismatch, _, _, dx_field, dy_field) in zip(axes, scenario_outputs):
        height = len(mismatch)
        width = len(mismatch[0])
        axis.imshow(mismatch, cmap="viridis", origin="lower")

        xs: list[int] = []
        ys: list[int] = []
        us: list[float] = []
        vs: list[float] = []
        for y in range(0, height, stride):
            for x in range(0, width, stride):
                xs.append(x)
                ys.append(y)
                us.append(float(dx_field[y][x]))
                vs.append(float(dy_field[y][x]))

        axis.quiver(xs, ys, us, vs, color="white", angles="xy", scale_units="xy", scale=scale, width=0.004)
        axis.set_title(f"{summary['scenario_label']}\nmu_mean={summary['mu_min_mean']:.3f}")
        axis.set_xticks([])
        axis.set_yticks([])

    fig.suptitle("Paper 3: local O*/-(i) selection field (quiver)")
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
                f"- `mu_min_mean`: `{summary['mu_min_mean']}`",
                f"- `mu_min_min`: `{summary['mu_min_min']}`",
                f"- `mu_min_max`: `{summary['mu_min_max']}`",
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
            "- `i_field.csv`",
            f"- `{figure_name}`",
            "- `run_summary.md`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Paper 3 O*/-(i) field probe.")
    parser.add_argument(
        "config",
        nargs="?",
        default=str(REPO_ROOT / "sim" / "configs" / "paper3_i_field_probe_v1.json"),
        help="Path to the Paper 3 field probe config.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config, raw_text = load_config(config_path)

    run_dir = ensure_run_directory(RUNS_ROOT, config["run_id"])
    figure_name = "figure_i_field_quiver.png"
    degeneracy_figure_name = "figure_degeneracy_map.png"
    figure_run_path = run_dir / figure_name
    degeneracy_figure_run_path = run_dir / degeneracy_figure_name
    figure_doc_path = REPO_ROOT / "docs" / "manuscript" / "paper3" / "fig2_i_field_quiver.png"
    degeneracy_figure_doc_path = REPO_ROOT / "docs" / "manuscript" / "paper3" / "fig3_degeneracy_map.png"

    scenario_outputs = [compute_i_field(config, scenario) for scenario in config["scenarios"]]
    summaries = [item[0] for item in scenario_outputs]

    i_field_rows = [row for _, rows, *_ in scenario_outputs for row in rows]

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
    write_csv(run_dir / "i_field.csv", list(i_field_rows[0].keys()), i_field_rows)

    stride = int(config["plot"]["stride"])
    scale = float(config["plot"]["scale"])
    plot_quiver(scenario_outputs, figure_run_path, stride=stride, scale=scale)
    plot_quiver(scenario_outputs, figure_doc_path, stride=stride, scale=scale)
    plot_degeneracy_map(scenario_outputs, degeneracy_figure_run_path)
    plot_degeneracy_map(scenario_outputs, degeneracy_figure_doc_path)
    write_run_summary(run_dir / "run_summary.md", manifest, summaries, figure_name)
    print(run_dir)


if __name__ == "__main__":
    main()
