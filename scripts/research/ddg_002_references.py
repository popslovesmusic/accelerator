"""Independent exact reference calculations for DDG_002.

Candidate-generator modules must not import this module.
"""

from __future__ import annotations

import itertools
import math


def entropy(weights):
    total = sum(weights)
    return -sum((weight / total) * math.log(weight / total) for weight in weights if weight > 0)


def ideal_gas_entropy(state: dict) -> float:
    return state["particle_count"] * math.log(state["volume"])


def two_level_entropy(state: dict) -> float:
    beta = 1.0 / state["temperature"]
    gap = state["energy_gap"]
    return entropy([1.0, math.exp(-beta * gap)])


def ising_entropy(state: dict) -> float:
    size = state.get("size", 2)
    states = list(itertools.product((-1, 1), repeat=size * size))
    edges = []
    for row in range(size):
        for col in range(size):
            i = row * size + col
            if col + 1 < size:
                edges.append((i, i + 1))
            if row + 1 < size:
                edges.append((i, i + size))
    beta = 1.0 / state["temperature"]
    weights = []
    for spin in states:
        interaction = sum(spin[i] * spin[j] for i, j in edges)
        energy = -state["coupling"] * interaction - state["field"] * sum(spin)
        weights.append(math.exp(-beta * energy))
    return entropy(weights)


REFERENCE_FUNCTIONS = {
    "IDEAL_GAS": ideal_gas_entropy,
    "TWO_LEVEL_SYSTEM": two_level_entropy,
    "ISING_2X2": ising_entropy,
    "ISING_3X3_HOLDOUT_ONLY": ising_entropy,
}
