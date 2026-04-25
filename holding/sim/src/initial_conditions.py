from __future__ import annotations


def build_initial_state(initial_conditions: dict) -> tuple[float, float, float]:
    return (
        float(initial_conditions["epsilon0"]),
        float(initial_conditions["rho0"]),
        float(initial_conditions["R0"]),
    )
