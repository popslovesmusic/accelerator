"""Reservoir-conditioned distinction redistribution candidates for campaign 003."""

from __future__ import annotations

import itertools
import math


def edges(rows: int, cols: int, boundary: str):
    out = []
    for row in range(rows):
        for col in range(cols):
            i = row * cols + col
            if col + 1 < cols:
                out.append((i, i + 1))
            elif boundary == "periodic":
                out.append((i, row * cols))
            if row + 1 < rows:
                out.append((i, i + cols))
            elif boundary == "periodic":
                out.append((i, col))
    return out


def field(regime: str, state: dict) -> list[float]:
    if regime == "IDEAL_GAS_BOUNDARY":
        return [0.5 + state["boundary_accessibility"] * (1.0 + 0.2 * math.sin(i)) + 0.01 * state["particle_count"] * state["volume"] for i in range(8)]
    if regime == "TWO_LEVEL_RESERVOIR":
        return [0.5 + state["reservoir_coupling"] * (1.0 + 0.1 * state["temperature"]) + 0.1 * state["energy_gap"], 0.5 + 0.25 * state["reservoir_coupling"] + 0.05 * state["temperature"] + 0.2 * state["energy_gap"]]
    states = list(itertools.product((-1, 1), repeat=state["rows"] * state["cols"]))
    relation_edges = edges(state["rows"], state["cols"], state["boundary"])
    values = []
    for spin in states:
        agreement = sum(spin[i] == spin[j] for i, j in relation_edges)
        magnetization = abs(sum(spin)) / len(spin)
        values.append(0.25 + 0.03 * agreement + 0.02 * magnetization + 0.01 * state["reservoir_coupling"] * (1.0 + state["temperature"]) + 0.01 * abs(state["field"]))
    return values


def accessibility(regime: str, state: dict, values: list[float]) -> float:
    if regime == "IDEAL_GAS_BOUNDARY":
        return sum(values) * state["boundary_accessibility"]
    if regime == "TWO_LEVEL_RESERVOIR":
        return sum(values) * state["reservoir_coupling"] / (1.0 + state["temperature"])
    return sum(values) / len(values) * (1.0 + state["reservoir_coupling"])


def orientation(values: list[float]) -> float:
    total = sum(values)
    return sum(index * value for index, value in enumerate(values)) / max(total, 1e-12)


def transition_flow(values: list[float]) -> float:
    return sum(abs(values[i + 1] - values[i]) for i in range(len(values) - 1))


def features(regime: str, before: dict, after: dict) -> dict:
    a = field(regime, before)
    b = field(regime, after)
    return {
        "rho_before": a,
        "rho_after": b,
        "capacity_before": sum(a),
        "capacity_after": sum(b),
        "delta_capacity": sum(b) - sum(a),
        "l1_relocation": sum(abs(x - y) for x, y in zip(a, b)),
        "delta_accessibility": accessibility(regime, after, b) - accessibility(regime, before, a),
        "delta_orientation": orientation(b) - orientation(a),
        "topological_redistribution": transition_flow(b) - transition_flow(a),
        "coupling_change": after["reservoir_coupling"] - before["reservoir_coupling"],
    }


def capacity_transport(regime: str, before: dict, after: dict) -> tuple[float, dict]:
    f = features(regime, before, after)
    return f["delta_capacity"] + 0.5 * f["topological_redistribution"] + 0.25 * f["delta_accessibility"] + 0.2 * f["coupling_change"], f


def boundary_accessibility(regime: str, before: dict, after: dict) -> tuple[float, dict]:
    f = features(regime, before, after)
    return f["delta_accessibility"] + 0.3 * f["delta_capacity"] + 0.2 * f["delta_orientation"] + 0.2 * f["coupling_change"], f


def admissible_transition_flow(regime: str, before: dict, after: dict) -> tuple[float, dict]:
    f = features(regime, before, after)
    return f["topological_redistribution"] + 0.2 * f["delta_accessibility"] + 0.2 * f["coupling_change"], f


FAMILIES = {
    "RDC_CAPACITY_TRANSPORT_001": capacity_transport,
    "RDC_BOUNDARY_ACCESSIBILITY_001": boundary_accessibility,
    "RDC_ADMISSIBLE_TRANSITION_FLOW_001": admissible_transition_flow,
}
