"""Particle and beam state containers."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from random import Random

from .constants import SPEED_OF_LIGHT


@dataclass
class Particle:
    """Single-particle state for longitudinal plus two transverse planes tracking."""

    id: int
    x_m: float
    momentum_kg_m_s: float
    mass_kg: float
    charge_c: float
    y_m: float = 0.0
    transverse_momentum_kg_m_s: float = 0.0
    z_m: float = 0.0
    z_transverse_momentum_kg_m_s: float = 0.0
    active: bool = True
    lost_reason: str = ""

    @property
    def total_momentum_kg_m_s(self) -> float:
        return sqrt(
            self.momentum_kg_m_s**2
            + self.transverse_momentum_kg_m_s**2
            + self.z_transverse_momentum_kg_m_s**2
        )

    @property
    def gamma(self) -> float:
        mc = self.mass_kg * SPEED_OF_LIGHT
        return sqrt(1.0 + (self.total_momentum_kg_m_s / mc) ** 2)

    @property
    def velocity_m_s(self) -> float:
        return self.momentum_kg_m_s / (self.gamma * self.mass_kg)

    @property
    def transverse_velocity_m_s(self) -> float:
        return self.transverse_momentum_kg_m_s / (self.gamma * self.mass_kg)

    @property
    def z_transverse_velocity_m_s(self) -> float:
        return self.z_transverse_momentum_kg_m_s / (self.gamma * self.mass_kg)

    @property
    def beta(self) -> float:
        return self.total_speed_m_s / SPEED_OF_LIGHT

    @property
    def total_speed_m_s(self) -> float:
        return self.total_momentum_kg_m_s / (self.gamma * self.mass_kg)

    @property
    def y_prime_rad(self) -> float:
        if self.momentum_kg_m_s == 0.0:
            return 0.0
        return self.transverse_momentum_kg_m_s / self.momentum_kg_m_s

    @property
    def z_prime_rad(self) -> float:
        if self.momentum_kg_m_s == 0.0:
            return 0.0
        return self.z_transverse_momentum_kg_m_s / self.momentum_kg_m_s

    @property
    def kinetic_energy_j(self) -> float:
        return (self.gamma - 1.0) * self.mass_kg * SPEED_OF_LIGHT**2


def momentum_from_kinetic_energy(kinetic_energy_j: float, mass_kg: float) -> float:
    """Return relativistic momentum from kinetic energy."""

    gamma = kinetic_energy_j / (mass_kg * SPEED_OF_LIGHT**2) + 1.0
    beta_sq = 1.0 - 1.0 / (gamma * gamma)
    return gamma * mass_kg * SPEED_OF_LIGHT * sqrt(max(beta_sq, 0.0))


def make_beam(
    count: int,
    mass_kg: float,
    charge_c: float,
    initial_energy_j: float,
    energy_spread_fraction: float,
    bunch_length_m: float,
    transverse_size_m: float,
    transverse_divergence_rad: float,
    z_transverse_size_m: float,
    z_transverse_divergence_rad: float,
    seed: int,
) -> list[Particle]:
    """Create a reproducible beam with longitudinal and transverse Gaussian spreads."""

    rng = Random(seed)
    particles: list[Particle] = []
    sigma_energy = abs(initial_energy_j * energy_spread_fraction)
    sigma_x = abs(bunch_length_m)
    sigma_y = abs(transverse_size_m)
    sigma_y_prime = abs(transverse_divergence_rad)
    sigma_z = abs(z_transverse_size_m)
    sigma_z_prime = abs(z_transverse_divergence_rad)

    for particle_id in range(count):
        energy_j = max(initial_energy_j + rng.gauss(0.0, sigma_energy), 0.0)
        longitudinal_momentum = momentum_from_kinetic_energy(energy_j, mass_kg)
        y_prime = rng.gauss(0.0, sigma_y_prime)
        z_prime = rng.gauss(0.0, sigma_z_prime)
        x_m = rng.gauss(0.0, sigma_x)
        y_m = rng.gauss(0.0, sigma_y)
        z_m = rng.gauss(0.0, sigma_z)
        particles.append(
            Particle(
                id=particle_id,
                x_m=x_m,
                momentum_kg_m_s=longitudinal_momentum,
                mass_kg=mass_kg,
                charge_c=charge_c,
                y_m=y_m,
                transverse_momentum_kg_m_s=longitudinal_momentum * y_prime,
                z_m=z_m,
                z_transverse_momentum_kg_m_s=longitudinal_momentum * z_prime,
            )
        )

    return particles
