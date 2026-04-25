"""Simulation orchestration and relativistic stepping."""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .analysis import (
    particle_summary,
    write_gap_phases_csv,
    write_history_csv,
    write_json,
    write_particles_csv,
    write_plots,
)
from .components import Component, RFGAP, make_periodic_lattice
from .constants import EV_TO_JOULE, JOULE_TO_EV, PARTICLE_SPECIES
from .particles import Particle, make_beam


@dataclass(frozen=True)
class SimulationConfig:
    species: str = "proton"
    particle_count: int = 500
    seed: int = 12345
    initial_energy_ev: float = 1_000_000.0
    energy_spread_fraction: float = 0.01
    bunch_length_m: float = 0.002
    transverse_size_m: float = 0.001
    transverse_divergence_rad: float = 0.001
    z_transverse_size_m: float = 0.001
    z_transverse_divergence_rad: float = 0.001
    aperture_radius_m: float = 0.01
    gap_count: int = 20
    drift_length_m: float = 0.04
    gap_length_m: float = 0.01
    peak_field_v_per_m: float = 2.0e6
    frequency_hz: float = 200.0e6
    phase_rad: float = 1.5707963267948966
    focusing_strength_1_per_m2: float = 25.0
    z_focusing_strength_1_per_m2: float = 25.0
    lens_length_m: float = 0.005
    dt_s: float = 2.0e-12
    max_time_s: float = 1.0e-7
    history_interval_steps: int = 25


@dataclass
class SimulationResult:
    config: SimulationConfig
    particles: list[Particle]
    history: list[dict[str, float | int]]
    gap_phases: list[dict[str, float | int | str]]
    final_summary: dict[str, float | int]
    lattice: list[Component]


def run_simulation(config: SimulationConfig) -> SimulationResult:
    species = PARTICLE_SPECIES[config.species]
    lattice = make_periodic_lattice(
        gap_count=config.gap_count,
        drift_length_m=config.drift_length_m,
        gap_length_m=config.gap_length_m,
        peak_field_v_per_m=config.peak_field_v_per_m,
        frequency_hz=config.frequency_hz,
        phase_rad=config.phase_rad,
        focusing_strength_1_per_m2=config.focusing_strength_1_per_m2,
        z_focusing_strength_1_per_m2=config.z_focusing_strength_1_per_m2,
        lens_length_m=config.lens_length_m,
    )
    particles = make_beam(
        count=config.particle_count,
        mass_kg=species["mass_kg"],
        charge_c=species["charge_c"],
        initial_energy_j=config.initial_energy_ev * EV_TO_JOULE,
        energy_spread_fraction=config.energy_spread_fraction,
        bunch_length_m=config.bunch_length_m,
        transverse_size_m=config.transverse_size_m,
        transverse_divergence_rad=config.transverse_divergence_rad,
        z_transverse_size_m=config.z_transverse_size_m,
        z_transverse_divergence_rad=config.z_transverse_divergence_rad,
        seed=config.seed,
    )

    accelerator_end_m = lattice[-1].end_m if lattice else 0.0
    component_starts = [component.start_m for component in lattice]
    rf_gaps = [component for component in lattice if isinstance(component, RFGAP)]
    history: list[dict[str, float | int]] = []
    gap_phases: list[dict[str, float | int | str]] = []
    next_gap_by_particle = {particle.id: 0 for particle in particles}

    time_s = 0.0
    step_index = 0
    max_steps = int(config.max_time_s / config.dt_s)

    while step_index <= max_steps:
        active_particles = [particle for particle in particles if particle.active]
        if not active_particles:
            break
        if all(particle.x_m >= accelerator_end_m for particle in active_particles):
            break

        if step_index % config.history_interval_steps == 0:
            row = {"step": step_index, "time_s": time_s}
            row.update(particle_summary(particles))
            history.append(row)

        for particle in active_particles:
            previous_x = particle.x_m
            component = component_at(lattice, particle.x_m, component_starts)
            field = component.electric_field_v_per_m(time_s) if component else 0.0
            particle.momentum_kg_m_s += particle.charge_c * field * config.dt_s
            if component is not None:
                focusing_k = component.transverse_kick_1_per_m2()
                z_focusing_k = component.z_transverse_kick_1_per_m2()
                particle.transverse_momentum_kg_m_s += (
                    -focusing_k
                    * particle.momentum_kg_m_s
                    * particle.velocity_m_s
                    * particle.y_m
                    * config.dt_s
                )
                particle.z_transverse_momentum_kg_m_s += (
                    -z_focusing_k
                    * particle.momentum_kg_m_s
                    * particle.velocity_m_s
                    * particle.z_m
                    * config.dt_s
                )
            particle.x_m += particle.velocity_m_s * config.dt_s
            particle.y_m += particle.transverse_velocity_m_s * config.dt_s
            particle.z_m += particle.z_transverse_velocity_m_s * config.dt_s

            next_gap_index = next_gap_by_particle[particle.id]
            while next_gap_index < len(rf_gaps):
                gap = rf_gaps[next_gap_index]
                if gap.start_m > particle.x_m:
                    break
                if previous_x < gap.start_m <= particle.x_m:
                    gap_phases.append(
                        {
                            "particle_id": particle.id,
                            "gap": gap.name,
                            "time_s": time_s,
                            "phase_rad": gap.phase_at(time_s),
                            "energy_ev": particle.kinetic_energy_j * JOULE_TO_EV,
                        }
                    )
                next_gap_index += 1
            next_gap_by_particle[particle.id] = next_gap_index

            if particle.x_m < -0.1:
                particle.active = False
                particle.lost_reason = "backward_loss"
            elif (particle.y_m**2 + particle.z_m**2) ** 0.5 > config.aperture_radius_m:
                particle.active = False
                particle.lost_reason = "aperture_loss"

        time_s += config.dt_s
        step_index += 1

    row = {"step": step_index, "time_s": time_s}
    row.update(particle_summary(particles))
    history.append(row)

    return SimulationResult(
        config=config,
        particles=particles,
        history=history,
        gap_phases=gap_phases,
        final_summary=particle_summary(particles),
        lattice=lattice,
    )


def field_at(
    lattice: list[Component],
    x_m: float,
    time_s: float,
    component_starts: list[float] | None = None,
) -> float:
    component = component_at(lattice, x_m, component_starts)
    return component.electric_field_v_per_m(time_s) if component else 0.0


def component_at(
    lattice: list[Component],
    x_m: float,
    component_starts: list[float] | None = None,
) -> Component | None:
    if component_starts is None:
        component_starts = [component.start_m for component in lattice]
    component_index = bisect_right(component_starts, x_m) - 1
    if 0 <= component_index < len(lattice):
        component = lattice[component_index]
        if component.contains(x_m):
            return component
    return None


def write_result(result: SimulationResult, output_dir: Path) -> bool:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        output_dir / "metadata.json",
        {
            "config": result.config,
            "final_summary": result.final_summary,
            "lattice": result.lattice,
        },
    )
    write_history_csv(output_dir / "history.csv", result.history)
    write_particles_csv(output_dir / "particles_final.csv", result.particles)
    write_gap_phases_csv(output_dir / "gap_phases.csv", result.gap_phases)
    return write_plots(output_dir, result.history, result.particles)


def config_from_args(args: Any) -> SimulationConfig:
    return SimulationConfig(
        species=args.species,
        particle_count=args.particles,
        seed=args.seed,
        initial_energy_ev=args.initial_energy_ev,
        energy_spread_fraction=args.energy_spread_fraction,
        bunch_length_m=args.bunch_length_m,
        transverse_size_m=args.transverse_size_m,
        transverse_divergence_rad=args.transverse_divergence_rad,
        z_transverse_size_m=args.z_transverse_size_m,
        z_transverse_divergence_rad=args.z_transverse_divergence_rad,
        aperture_radius_m=args.aperture_radius_m,
        gap_count=args.gaps,
        drift_length_m=args.drift_length_m,
        gap_length_m=args.gap_length_m,
        peak_field_v_per_m=args.peak_field,
        frequency_hz=args.frequency,
        phase_rad=args.phase,
        focusing_strength_1_per_m2=args.focusing_strength,
        z_focusing_strength_1_per_m2=args.z_focusing_strength,
        lens_length_m=args.lens_length_m,
        dt_s=args.dt,
        max_time_s=args.max_time,
        history_interval_steps=args.history_interval,
    )
