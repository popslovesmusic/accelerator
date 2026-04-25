"""Analysis and output helpers."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .constants import JOULE_TO_EV
from .particles import Particle


def particle_summary(particles: list[Particle]) -> dict[str, float | int]:
    active = [particle for particle in particles if particle.active]
    energies_ev = [particle.kinetic_energy_j * JOULE_TO_EV for particle in active]
    positions_m = [particle.x_m for particle in active]
    transverse_positions_m = [particle.y_m for particle in active]
    transverse_angles_rad = [particle.y_prime_rad for particle in active]
    z_transverse_positions_m = [particle.z_m for particle in active]
    z_transverse_angles_rad = [particle.z_prime_rad for particle in active]

    if not active:
        return {
            "active_count": 0,
            "lost_count": len(particles),
            "transmission_fraction": 0.0,
            "mean_energy_ev": 0.0,
            "rms_energy_spread_ev": 0.0,
            "mean_position_m": 0.0,
            "rms_bunch_length_m": 0.0,
            "mean_y_m": 0.0,
            "rms_beam_size_m": 0.0,
            "rms_divergence_rad": 0.0,
            "geometric_emittance_m_rad": 0.0,
            "normalized_emittance_m_rad": 0.0,
            "mean_z_m": 0.0,
            "rms_z_beam_size_m": 0.0,
            "rms_z_divergence_rad": 0.0,
            "z_geometric_emittance_m_rad": 0.0,
            "z_normalized_emittance_m_rad": 0.0,
            "rms_radial_beam_size_m": 0.0,
        }

    emittance = rms_emittance(transverse_positions_m, transverse_angles_rad)
    z_emittance = rms_emittance(z_transverse_positions_m, z_transverse_angles_rad)
    mean_beta_gamma = mean([particle.beta * particle.gamma for particle in active])
    radial_positions_m = [
        (particle.y_m**2 + particle.z_m**2) ** 0.5 for particle in active
    ]
    return {
        "active_count": len(active),
        "lost_count": len(particles) - len(active),
        "transmission_fraction": len(active) / len(particles),
        "mean_energy_ev": mean(energies_ev),
        "rms_energy_spread_ev": pstdev(energies_ev) if len(energies_ev) > 1 else 0.0,
        "mean_position_m": mean(positions_m),
        "rms_bunch_length_m": pstdev(positions_m) if len(positions_m) > 1 else 0.0,
        "mean_y_m": mean(transverse_positions_m),
        "rms_beam_size_m": pstdev(transverse_positions_m) if len(transverse_positions_m) > 1 else 0.0,
        "rms_divergence_rad": pstdev(transverse_angles_rad) if len(transverse_angles_rad) > 1 else 0.0,
        "geometric_emittance_m_rad": emittance,
        "normalized_emittance_m_rad": mean_beta_gamma * emittance,
        "mean_z_m": mean(z_transverse_positions_m),
        "rms_z_beam_size_m": pstdev(z_transverse_positions_m) if len(z_transverse_positions_m) > 1 else 0.0,
        "rms_z_divergence_rad": pstdev(z_transverse_angles_rad) if len(z_transverse_angles_rad) > 1 else 0.0,
        "z_geometric_emittance_m_rad": z_emittance,
        "z_normalized_emittance_m_rad": mean_beta_gamma * z_emittance,
        "rms_radial_beam_size_m": mean([radius * radius for radius in radial_positions_m]) ** 0.5,
    }


def rms_emittance(positions_m: list[float], angles_rad: list[float]) -> float:
    """Return RMS geometric emittance for one transverse phase-space plane."""

    if len(positions_m) < 2 or len(positions_m) != len(angles_rad):
        return 0.0

    mean_position = mean(positions_m)
    mean_angle = mean(angles_rad)
    centered_positions = [position - mean_position for position in positions_m]
    centered_angles = [angle - mean_angle for angle in angles_rad]
    yy = mean([position * position for position in centered_positions])
    aa = mean([angle * angle for angle in centered_angles])
    ya = mean(
        [
            position * angle
            for position, angle in zip(centered_positions, centered_angles)
        ]
    )
    determinant = yy * aa - ya * ya
    return determinant**0.5 if determinant > 0.0 else 0.0


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(_jsonable(data), handle, indent=2)
        handle.write("\n")


def write_history_csv(path: Path, history: list[dict[str, float | int]]) -> None:
    if not history:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0].keys()))
        writer.writeheader()
        writer.writerows(history)


def write_particles_csv(path: Path, particles: list[Particle]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "id",
            "active",
            "lost_reason",
            "x_m",
            "y_m",
            "y_prime_rad",
            "z_m",
            "z_prime_rad",
            "beta",
            "velocity_m_s",
            "transverse_velocity_m_s",
            "z_transverse_velocity_m_s",
            "momentum_kg_m_s",
            "transverse_momentum_kg_m_s",
            "z_transverse_momentum_kg_m_s",
            "kinetic_energy_ev",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for particle in particles:
            writer.writerow(
                {
                    "id": particle.id,
                    "active": particle.active,
                    "lost_reason": particle.lost_reason,
                    "x_m": particle.x_m,
                    "y_m": particle.y_m,
                    "y_prime_rad": particle.y_prime_rad,
                    "z_m": particle.z_m,
                    "z_prime_rad": particle.z_prime_rad,
                    "beta": particle.beta,
                    "velocity_m_s": particle.velocity_m_s,
                    "transverse_velocity_m_s": particle.transverse_velocity_m_s,
                    "z_transverse_velocity_m_s": particle.z_transverse_velocity_m_s,
                    "momentum_kg_m_s": particle.momentum_kg_m_s,
                    "transverse_momentum_kg_m_s": particle.transverse_momentum_kg_m_s,
                    "z_transverse_momentum_kg_m_s": particle.z_transverse_momentum_kg_m_s,
                    "kinetic_energy_ev": particle.kinetic_energy_j * JOULE_TO_EV,
                }
            )


def write_gap_phases_csv(path: Path, gap_phases: list[dict[str, float | int | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["particle_id", "gap", "time_s", "phase_rad", "energy_ev"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gap_phases)


def write_plots(output_dir: Path, history: list[dict[str, float | int]], particles: list[Particle]) -> bool:
    """Write optional Matplotlib figures. Returns False if Matplotlib is unavailable."""

    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    times = [row["time_s"] for row in history]
    mean_energy = [row["mean_energy_ev"] for row in history]
    spread = [row["rms_energy_spread_ev"] for row in history]
    emittance = [row["normalized_emittance_m_rad"] for row in history]
    z_emittance = [row["z_normalized_emittance_m_rad"] for row in history]
    beam_size = [row["rms_beam_size_m"] for row in history]
    z_beam_size = [row["rms_z_beam_size_m"] for row in history]

    plt.figure(figsize=(8, 5))
    plt.plot(times, mean_energy)
    plt.xlabel("Time (s)")
    plt.ylabel("Mean kinetic energy (eV)")
    plt.title("Mean Beam Energy")
    plt.tight_layout()
    plt.savefig(figures_dir / "mean_energy.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(times, spread)
    plt.xlabel("Time (s)")
    plt.ylabel("RMS energy spread (eV)")
    plt.title("Beam Energy Spread")
    plt.tight_layout()
    plt.savefig(figures_dir / "energy_spread.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(times, emittance)
    plt.plot(times, z_emittance)
    plt.xlabel("Time (s)")
    plt.ylabel("Normalized RMS emittance (m rad)")
    plt.title("Transverse Emittance")
    plt.legend(["y plane", "z plane"])
    plt.tight_layout()
    plt.savefig(figures_dir / "normalized_emittance.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(times, beam_size)
    plt.plot(times, z_beam_size)
    plt.xlabel("Time (s)")
    plt.ylabel("RMS beam size (m)")
    plt.title("Transverse Beam Size")
    plt.legend(["y plane", "z plane"])
    plt.tight_layout()
    plt.savefig(figures_dir / "beam_size.png", dpi=180)
    plt.close()

    energies = [particle.kinetic_energy_j * JOULE_TO_EV for particle in particles if particle.active]
    plt.figure(figsize=(8, 5))
    plt.hist(energies, bins=40)
    plt.xlabel("Final kinetic energy (eV)")
    plt.ylabel("Particle count")
    plt.title("Final Energy Distribution")
    plt.tight_layout()
    plt.savefig(figures_dir / "final_energy_histogram.png", dpi=180)
    plt.close()

    phase_space_particles = [particle for particle in particles if particle.active]
    plt.figure(figsize=(8, 5))
    plt.scatter(
        [particle.y_m for particle in phase_space_particles],
        [particle.y_prime_rad for particle in phase_space_particles],
        s=8,
        alpha=0.6,
    )
    plt.xlabel("y (m)")
    plt.ylabel("y' (rad)")
    plt.title("Final Transverse Phase Space")
    plt.tight_layout()
    plt.savefig(figures_dir / "transverse_phase_space.png", dpi=180)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(
        [particle.z_m for particle in phase_space_particles],
        [particle.z_prime_rad for particle in phase_space_particles],
        s=8,
        alpha=0.6,
    )
    plt.xlabel("z (m)")
    plt.ylabel("z' (rad)")
    plt.title("Final Z Transverse Phase Space")
    plt.tight_layout()
    plt.savefig(figures_dir / "z_transverse_phase_space.png", dpi=180)
    plt.close()

    plt.figure(figsize=(6, 6))
    plt.scatter(
        [particle.y_m for particle in phase_space_particles],
        [particle.z_m for particle in phase_space_particles],
        s=8,
        alpha=0.6,
    )
    plt.xlabel("y (m)")
    plt.ylabel("z (m)")
    plt.title("Final Transverse Beam Cross Section")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(figures_dir / "transverse_cross_section.png", dpi=180)
    plt.close()

    return True


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value
