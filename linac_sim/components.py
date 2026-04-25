"""Accelerator lattice components."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin


@dataclass(frozen=True)
class Component:
    """Base 1D accelerator component."""

    name: str
    start_m: float
    length_m: float

    @property
    def end_m(self) -> float:
        return self.start_m + self.length_m

    def contains(self, x_m: float) -> bool:
        return self.start_m <= x_m < self.end_m

    def electric_field_v_per_m(self, t_s: float) -> float:
        return 0.0

    def transverse_kick_1_per_m2(self) -> float:
        return 0.0

    def z_transverse_kick_1_per_m2(self) -> float:
        return 0.0


@dataclass(frozen=True)
class Drift(Component):
    """Field-free drift region."""


@dataclass(frozen=True)
class FocusingLens(Component):
    """Linear paraxial focusing element for two transverse planes.

    The simulation applies the continuous approximation:

    dp_y / ds = -k_y * p_s * y
    dp_z / ds = -k_z * p_s * z

    where `k_y` and `k_z` are focusing strengths.
    """

    strength_1_per_m2: float
    z_strength_1_per_m2: float

    def transverse_kick_1_per_m2(self) -> float:
        return self.strength_1_per_m2

    def z_transverse_kick_1_per_m2(self) -> float:
        return self.z_strength_1_per_m2


@dataclass(frozen=True)
class RFGAP(Component):
    """Longitudinal RF accelerating gap."""

    peak_field_v_per_m: float
    frequency_hz: float
    phase_rad: float = 0.0

    def electric_field_v_per_m(self, t_s: float) -> float:
        omega = 2.0 * pi * self.frequency_hz
        return self.peak_field_v_per_m * sin(omega * t_s + self.phase_rad)

    def phase_at(self, t_s: float) -> float:
        omega = 2.0 * pi * self.frequency_hz
        return (omega * t_s + self.phase_rad) % (2.0 * pi)


def make_periodic_lattice(
    gap_count: int = 20,
    drift_length_m: float = 0.04,
    gap_length_m: float = 0.01,
    peak_field_v_per_m: float = 2.0e6,
    frequency_hz: float = 200.0e6,
    phase_rad: float = pi / 2.0,
    focusing_strength_1_per_m2: float = 25.0,
    z_focusing_strength_1_per_m2: float = 25.0,
    lens_length_m: float = 0.005,
) -> list[Component]:
    """Create a periodic drift, focusing lens, and RF gap lattice."""

    components: list[Component] = []
    position = 0.0
    for index in range(gap_count):
        first_drift_length = max((drift_length_m - lens_length_m) / 2.0, 0.0)
        second_drift_length = max(drift_length_m - lens_length_m - first_drift_length, 0.0)

        first_drift = Drift(
            name=f"drift_{index + 1:02d}a",
            start_m=position,
            length_m=first_drift_length,
        )
        components.append(first_drift)
        position = first_drift.end_m

        if (
            lens_length_m > 0.0
            and (focusing_strength_1_per_m2 != 0.0 or z_focusing_strength_1_per_m2 != 0.0)
        ):
            lens = FocusingLens(
                name=f"focus_{index + 1:02d}",
                start_m=position,
                length_m=lens_length_m,
                strength_1_per_m2=focusing_strength_1_per_m2,
                z_strength_1_per_m2=z_focusing_strength_1_per_m2,
            )
            components.append(lens)
            position = lens.end_m

        second_drift = Drift(
            name=f"drift_{index + 1:02d}b",
            start_m=position,
            length_m=second_drift_length,
        )
        components.append(second_drift)
        position = second_drift.end_m

        gap = RFGAP(
            name=f"rf_gap_{index + 1:02d}",
            start_m=position,
            length_m=gap_length_m,
            peak_field_v_per_m=peak_field_v_per_m,
            frequency_hz=frequency_hz,
            phase_rad=phase_rad,
        )
        components.append(gap)
        position = gap.end_m

    return components
