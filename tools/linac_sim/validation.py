"""Validation checks for the 1D linac simulation."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from .analysis import rms_emittance
from .components import Drift, RFGAP
from .constants import ELEMENTARY_CHARGE, EV_TO_JOULE, PROTON_MASS, SPEED_OF_LIGHT
from .particles import Particle, momentum_from_kinetic_energy
from .simulation import SimulationConfig, field_at, run_simulation


@dataclass(frozen=True)
class ValidationCheck:
    name: str
    passed: bool
    detail: str


def run_validation() -> list[ValidationCheck]:
    return [
        validate_zero_field_energy_conservation(),
        validate_constant_field_nonrelativistic_limit(),
        validate_relativistic_speed_limit(),
        validate_rf_field_phase(),
        validate_time_step_convergence(),
        validate_aperture_loss(),
        validate_emittance_calculation(),
    ]


def validate_zero_field_energy_conservation() -> ValidationCheck:
    config = SimulationConfig(
        particle_count=5,
        gap_count=1,
        peak_field_v_per_m=0.0,
        initial_energy_ev=10_000.0,
        energy_spread_fraction=0.0,
        transverse_size_m=0.0,
        transverse_divergence_rad=0.0,
        z_transverse_size_m=0.0,
        z_transverse_divergence_rad=0.0,
        focusing_strength_1_per_m2=0.0,
        z_focusing_strength_1_per_m2=0.0,
        max_time_s=8.0e-9,
        dt_s=2.0e-12,
    )
    result = run_simulation(config)
    initial = config.initial_energy_ev
    final = result.final_summary["mean_energy_ev"]
    rel_error = abs(final - initial) / initial
    return ValidationCheck(
        name="zero_field_energy_conservation",
        passed=rel_error < 5.0e-3,
        detail=f"relative error={rel_error:.3e}",
    )


def validate_constant_field_nonrelativistic_limit() -> ValidationCheck:
    particle = Particle(
        id=0,
        x_m=0.0,
        momentum_kg_m_s=0.0,
        mass_kg=PROTON_MASS,
        charge_c=ELEMENTARY_CHARGE,
    )
    electric_field = 1.0e3
    dt = 1.0e-10
    steps = 100
    for _ in range(steps):
        particle.momentum_kg_m_s += particle.charge_c * electric_field * dt
        particle.x_m += particle.velocity_m_s * dt

    t = dt * steps
    expected_v = particle.charge_c * electric_field * t / particle.mass_kg
    rel_error = abs(particle.velocity_m_s - expected_v) / expected_v
    return ValidationCheck(
        name="constant_field_nonrelativistic_limit",
        passed=rel_error < 1.0e-5,
        detail=f"velocity relative error={rel_error:.3e}",
    )


def validate_relativistic_speed_limit() -> ValidationCheck:
    energy_j = 1.0e12 * EV_TO_JOULE
    particle = Particle(
        id=0,
        x_m=0.0,
        momentum_kg_m_s=momentum_from_kinetic_energy(energy_j, PROTON_MASS),
        mass_kg=PROTON_MASS,
        charge_c=ELEMENTARY_CHARGE,
    )
    return ValidationCheck(
        name="relativistic_speed_limit",
        passed=particle.velocity_m_s < SPEED_OF_LIGHT,
        detail=f"beta={particle.beta:.12f}",
    )


def validate_rf_field_phase() -> ValidationCheck:
    gap = RFGAP(
        name="test_gap",
        start_m=0.0,
        length_m=0.01,
        peak_field_v_per_m=5.0,
        frequency_hz=10.0,
        phase_rad=0.0,
    )
    quarter_period = 1.0 / (4.0 * gap.frequency_hz)
    field = gap.electric_field_v_per_m(quarter_period)
    return ValidationCheck(
        name="rf_field_phase",
        passed=isclose(field, 5.0, rel_tol=1.0e-12, abs_tol=1.0e-12),
        detail=f"quarter-period field={field:.6g} V/m",
    )


def validate_time_step_convergence() -> ValidationCheck:
    base = SimulationConfig(
        particle_count=50,
        gap_count=3,
        initial_energy_ev=25_000.0,
        max_time_s=1.5e-8,
        dt_s=4.0e-12,
        seed=99,
    )
    fine = SimulationConfig(
        particle_count=50,
        gap_count=3,
        initial_energy_ev=25_000.0,
        max_time_s=1.5e-8,
        dt_s=2.0e-12,
        seed=99,
    )
    coarse_result = run_simulation(base)
    fine_result = run_simulation(fine)
    coarse_energy = coarse_result.final_summary["mean_energy_ev"]
    fine_energy = fine_result.final_summary["mean_energy_ev"]
    rel_delta = abs(coarse_energy - fine_energy) / max(abs(fine_energy), 1.0)
    return ValidationCheck(
        name="time_step_convergence",
        passed=rel_delta < 0.05,
        detail=f"mean energy relative delta={rel_delta:.3e}",
    )


def validate_aperture_loss() -> ValidationCheck:
    config = SimulationConfig(
        particle_count=10,
        gap_count=1,
        initial_energy_ev=100_000.0,
        transverse_size_m=0.01,
        transverse_divergence_rad=0.0,
        z_transverse_size_m=0.01,
        z_transverse_divergence_rad=0.0,
        aperture_radius_m=0.001,
        focusing_strength_1_per_m2=0.0,
        z_focusing_strength_1_per_m2=0.0,
        max_time_s=1.0e-9,
        dt_s=2.0e-12,
        seed=7,
    )
    result = run_simulation(config)
    lost_count = result.final_summary["lost_count"]
    return ValidationCheck(
        name="aperture_loss",
        passed=lost_count > 0,
        detail=f"lost_count={lost_count}",
    )


def validate_emittance_calculation() -> ValidationCheck:
    positions = [-1.0e-3, 1.0e-3, -1.0e-3, 1.0e-3]
    angles = [-2.0e-3, -2.0e-3, 2.0e-3, 2.0e-3]
    emittance = rms_emittance(positions, angles)
    expected = 2.0e-6
    rel_error = abs(emittance - expected) / expected
    return ValidationCheck(
        name="emittance_calculation",
        passed=rel_error < 1.0e-12,
        detail=f"emittance={emittance:.6e} m rad",
    )


def validate_field_lookup() -> ValidationCheck:
    drift = Drift(name="drift", start_m=0.0, length_m=1.0)
    field = field_at([drift], 0.5, 0.0)
    return ValidationCheck(
        name="field_lookup",
        passed=field == 0.0,
        detail=f"field={field}",
    )
