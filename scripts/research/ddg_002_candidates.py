"""Candidate distinction-density families for DDG_002.

This module contains no statistical-mechanics reference implementation.
"""

from __future__ import annotations

import itertools
import math


def _ising_states():
    return list(itertools.product((-1, 1), repeat=9))


def _ising_edges(size: int):
    edges = []
    for row in range(size):
        for col in range(size):
            i = row * size + col
            if col + 1 < size:
                edges.append((i, i + 1))
            if row + 1 < size:
                edges.append((i, i + size))
    return edges


def _features(regime: str, state: dict):
    if regime == "IDEAL_GAS":
        return [1.0 + 0.05 * state["volume"] * (1.0 + math.cos(2.0 * math.pi * i / 16.0)) for i in range(16)]
    if regime == "TWO_LEVEL_SYSTEM":
        gap = state["energy_gap"]
        temp = state["temperature"]
        return [1.0 + (0.2 if i == 0 else 0.0) + 0.1 * temp * (i + 1) + 0.05 * gap * i for i in range(2)]
    size = state.get("size", 2)
    states = list(itertools.product((-1, 1), repeat=size * size))
    edges = _ising_edges(size)
    values = []
    for spin in states:
        agreement = sum(spin[i] == spin[j] for i, j in edges)
        magnetization = abs(sum(spin)) / len(spin)
        energy_alignment = state["coupling"] * agreement + state["field"] * sum(spin)
        values.append(0.5 + 0.05 * agreement + 0.02 * magnetization * (abs(state["field"]) + 1.0) + 0.01 * state["temperature"] * (1.0 + energy_alignment / max(1, len(edges))))
    return values


def graph_constraint(regime: str, state: dict) -> list[float]:
    """DDG_GRAPH_CONSTRAINT_001: compatibility, participation, boundary, orientation."""
    return [max(0.0, value) for value in _features(regime, state)]


def transition_accessibility(regime: str, state: dict) -> list[float]:
    """DDG_TRANSITION_ACCESSIBILITY_001: structural transition accessibility."""
    if regime == "IDEAL_GAS":
        return [0.1 + (i + 1) / 16.0 * (1.0 + 0.1 * state["volume"]) for i in range(16)]
    if regime == "TWO_LEVEL_SYSTEM":
        return [0.1 + (i + 1) * (1.0 + 0.05 * state["temperature"]) + 0.02 * state["energy_gap"] * (1 - i) for i in range(2)]
    size = state.get("size", 2)
    states = list(itertools.product((-1, 1), repeat=size * size))
    edges = _ising_edges(size)
    output = []
    for spin in states:
        transitions = sum(sum(1 for j in range(len(spin)) if j != i and spin[j] != spin[i]) for i in range(len(spin)))
        agreement = sum(spin[i] == spin[j] for i, j in edges)
        output.append(0.1 + transitions / len(spin) + 0.02 * agreement * abs(state["coupling"]) + 0.01 * abs(state["field"]))
    return output


FAMILIES = {
    "DDG_GRAPH_CONSTRAINT_001": graph_constraint,
    "DDG_TRANSITION_ACCESSIBILITY_001": transition_accessibility,
}
