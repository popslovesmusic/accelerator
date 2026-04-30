"""Simple CPU-first circular 6D accelerator simulation.

State vector columns are:

    x, px, y, py, z, delta

The ring is tracked turn by turn through a repeated lattice. The longitudinal
coordinate `z` is wrapped into one circumference after each turn, while a
separate cumulative path coordinate is not stored.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np


STATE_COLUMNS = ("x", "px", "y", "py", "z", "delta")
X, PX, Y, PY, Z, DELTA = range(6)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def initialize_bunch(config: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    particle_count = int(config["particles"])
    distribution = config["initial_distribution"]
    rng = np.random.default_rng(int(config["seed"]))

    state = np.zeros((particle_count, 6), dtype=np.float64)
    state[:, X] = rng.normal(0.0, float(distribution["x_sigma"]), particle_count)
    state[:, PX] = rng.normal(0.0, float(distribution["px_sigma"]), particle_count)
    state[:, Y] = rng.normal(0.0, float(distribution["y_sigma"]), particle_count)
    state[:, PY] = rng.normal(0.0, float(distribution["py_sigma"]), particle_count)
    state[:, Z] = rng.normal(0.0, float(distribution["z_sigma"]), particle_count)
    state[:, DELTA] = rng.normal(0.0, float(distribution["delta_sigma"]), particle_count)

    return state, np.ones(particle_count, dtype=bool)


def apply_drift(state: np.ndarray, alive: np.ndarray, length: float) -> None:
    active = alive
    inv_rigidity = 1.0 / np.maximum(1.0 + state[active, DELTA], 1.0e-12)
    state[active, X] += length * state[active, PX] * inv_rigidity
    state[active, Y] += length * state[active, PY] * inv_rigidity


def apply_quadrupole(state: np.ndarray, alive: np.ndarray, k1: float, length: float) -> None:
    active = alive
    half_length = 0.5 * length
    apply_drift(state, alive, half_length)
    state[active, PX] -= k1 * length * state[active, X]
    state[active, PY] += k1 * length * state[active, Y]
    apply_drift(state, alive, half_length)


def apply_rf_cavity(
    state: np.ndarray,
    alive: np.ndarray,
    voltage: float,
    phase: float,
    harmonic: float,
    circumference: float,
) -> None:
    active = alive
    rf_phase = 2.0 * np.pi * harmonic * state[active, Z] / circumference + phase
    state[active, DELTA] += voltage * np.sin(rf_phase)


def apply_aperture(state: np.ndarray, alive: np.ndarray, radius: float) -> int:
    active_indices = np.flatnonzero(alive)
    radius_sq = radius * radius
    radial_sq = state[active_indices, X] ** 2 + state[active_indices, Y] ** 2
    newly_lost = active_indices[radial_sq > radius_sq]
    alive[newly_lost] = False
    return int(newly_lost.size)


def apply_element(
    state: np.ndarray,
    alive: np.ndarray,
    element: dict[str, Any],
    circumference: float,
) -> int:
    element_type = element["type"]
    if element_type == "drift":
        apply_drift(state, alive, float(element["length"]))
        return 0
    if element_type == "quadrupole":
        apply_quadrupole(state, alive, float(element["k1"]), float(element["length"]))
        return 0
    if element_type == "rf_cavity":
        apply_rf_cavity(
            state,
            alive,
            float(element["voltage"]),
            float(element["phase"]),
            float(element["harmonic"]),
            circumference,
        )
        return 0
    if element_type == "aperture":
        return apply_aperture(state, alive, float(element["radius"]))
    raise ValueError(f"unsupported ring element type: {element_type}")


def wrap_longitudinal(state: np.ndarray, alive: np.ndarray, circumference: float) -> None:
    active = alive
    half_circumference = 0.5 * circumference
    state[active, Z] = ((state[active, Z] + half_circumference) % circumference) - half_circumference


def advance_turn_longitudinal(
    state: np.ndarray,
    alive: np.ndarray,
    circumference: float,
    momentum_compaction: float,
) -> None:
    active = alive
    state[active, Z] += momentum_compaction * circumference * state[active, DELTA]
    wrap_longitudinal(state, alive, circumference)


def rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean((values - np.mean(values)) ** 2)))


def emittance_proxy(position: np.ndarray, momentum: np.ndarray) -> float:
    if position.size < 2:
        return 0.0
    centered_position = position - np.mean(position)
    centered_momentum = momentum - np.mean(momentum)
    pp = np.mean(centered_position * centered_position)
    mm = np.mean(centered_momentum * centered_momentum)
    pm = np.mean(centered_position * centered_momentum)
    return float(np.sqrt(max(pp * mm - pm * pm, 0.0)))


def compute_metrics(state: np.ndarray, alive: np.ndarray, turn: int) -> dict[str, float | int]:
    active = state[alive]
    alive_count = int(active.shape[0])
    total_count = int(state.shape[0])
    row: dict[str, float | int] = {
        "turn": int(turn),
        "alive_count": alive_count,
        "survival_fraction": alive_count / total_count if total_count else 0.0,
    }
    metric_names = (
        "x_mean",
        "x_rms",
        "y_mean",
        "y_rms",
        "z_mean",
        "z_rms",
        "delta_mean",
        "delta_rms",
        "px_rms",
        "py_rms",
        "emittance_proxy_x",
        "emittance_proxy_y",
    )
    if alive_count == 0:
        row.update({name: 0.0 for name in metric_names})
        return row
    row.update(
        {
            "x_mean": float(np.mean(active[:, X])),
            "x_rms": rms(active[:, X]),
            "y_mean": float(np.mean(active[:, Y])),
            "y_rms": rms(active[:, Y]),
            "z_mean": float(np.mean(active[:, Z])),
            "z_rms": rms(active[:, Z]),
            "delta_mean": float(np.mean(active[:, DELTA])),
            "delta_rms": rms(active[:, DELTA]),
            "px_rms": rms(active[:, PX]),
            "py_rms": rms(active[:, PY]),
            "emittance_proxy_x": emittance_proxy(active[:, X], active[:, PX]),
            "emittance_proxy_y": emittance_proxy(active[:, Y], active[:, PY]),
        }
    )
    return row


def write_metrics_csv(path: Path, rows: list[dict[str, float | int]]) -> None:
    import pandas as pd

    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def write_snapshot(path: Path, state: np.ndarray, alive: np.ndarray, turn: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        state=state,
        alive=alive,
        state_columns=np.array(STATE_COLUMNS),
        turn=np.array(turn, dtype=np.int64),
    )


def write_summary_json(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def maybe_write_plots(out_dir: Path, rows: list[dict[str, float | int]]) -> bool:
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except Exception:
        return False

    figures_dir = out_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)

    plt.figure(figsize=(8, 5))
    plt.plot(df["turn"], df["survival_fraction"])
    plt.xlabel("Turn")
    plt.ylabel("Survival fraction")
    plt.title("Ring Survival")
    plt.tight_layout()
    plt.savefig(figures_dir / "survival_fraction.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["turn"], df["x_rms"], label="x")
    plt.plot(df["turn"], df["y_rms"], label="y")
    plt.xlabel("Turn")
    plt.ylabel("RMS beam size")
    plt.title("Transverse Beam Size by Turn")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "transverse_rms.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["turn"], df["z_rms"])
    plt.xlabel("Turn")
    plt.ylabel("z RMS")
    plt.title("Longitudinal Bunch Length")
    plt.tight_layout()
    plt.savefig(figures_dir / "z_rms.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["turn"], df["delta_rms"])
    plt.xlabel("Turn")
    plt.ylabel("delta RMS")
    plt.title("Energy Spread Proxy")
    plt.tight_layout()
    plt.savefig(figures_dir / "delta_rms.png", dpi=180)
    plt.close()

    return True


def run(config: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    start_time = time.perf_counter()
    state, alive = initialize_bunch(config)
    turns = int(config["turns"])
    snapshot_interval = int(config["snapshot_interval"])
    circumference = float(config["circumference"])
    momentum_compaction = float(config["momentum_compaction"])
    lattice = config["ring_lattice"]

    out_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = out_dir / "snapshots"

    rows: list[dict[str, float | int]] = [compute_metrics(state, alive, 0)]
    write_snapshot(snapshots_dir / "turn_000000.npz", state, alive, 0)

    previous_alive_count = int(np.count_nonzero(alive))
    alive_count_never_increases = True

    for turn in range(1, turns + 1):
        for element in lattice:
            apply_element(state, alive, element, circumference)
        advance_turn_longitudinal(state, alive, circumference, momentum_compaction)

        alive_count = int(np.count_nonzero(alive))
        if alive_count > previous_alive_count:
            alive_count_never_increases = False
        previous_alive_count = alive_count

        rows.append(compute_metrics(state, alive, turn))
        if snapshot_interval > 0 and turn % snapshot_interval == 0:
            write_snapshot(snapshots_dir / f"turn_{turn:06d}.npz", state, alive, turn)

    write_metrics_csv(out_dir / "turn_metrics.csv", rows)
    plots_written = maybe_write_plots(out_dir, rows)
    final_metrics = rows[-1]

    summary = {
        "config_name": config.get("name", ""),
        "seed": int(config["seed"]),
        "particles": int(config["particles"]),
        "turns": turns,
        "circumference": circumference,
        "momentum_compaction": momentum_compaction,
        "state_columns": list(STATE_COLUMNS),
        "output_dir": str(out_dir),
        "runtime_seconds": time.perf_counter() - start_time,
        "initial_alive_count": int(config["particles"]),
        "final_alive_count": int(final_metrics["alive_count"]),
        "lost_count": int(config["particles"]) - int(final_metrics["alive_count"]),
        "survival_fraction": float(final_metrics["survival_fraction"]),
        "alive_count_never_increases": alive_count_never_increases,
        "snapshot_interval": snapshot_interval,
        "snapshots_written": len(list(snapshots_dir.glob("*.npz"))),
        "plots_written": plots_written,
        "final_metrics": final_metrics,
        "model_limits": [
            "Reduced circular 6D map, not a production synchrotron/storage-ring code.",
            "No radiation damping, quantum excitation, space charge, wakefields, or field maps.",
            "Longitudinal coordinate is wrapped by circumference after each turn.",
            "Momentum compaction is a simple linear slip factor proxy.",
            "RF cavity applies a sinusoidal kick to delta only.",
            "Aperture loss is a simple circular transverse cut.",
        ],
    }
    write_summary_json(out_dir / "summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple vectorized circular 6D accelerator simulation.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/optiplex_ring_default.json"),
        help="Path to ring simulation config JSON.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/ring_default"),
        help="Output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run(load_config(args.config), args.out)
    print(f"output_dir={args.out}")
    print(f"final_alive_count={summary['final_alive_count']}")
    print(f"lost_count={summary['lost_count']}")
    print(f"survival_fraction={summary['survival_fraction']:.6f}")
    print(f"x_rms={summary['final_metrics']['x_rms']:.6e}")
    print(f"y_rms={summary['final_metrics']['y_rms']:.6e}")
    print(f"z_rms={summary['final_metrics']['z_rms']:.6e}")
    print(f"delta_rms={summary['final_metrics']['delta_rms']:.6e}")
    print(f"runtime_seconds={summary['runtime_seconds']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
