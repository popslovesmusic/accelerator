"""Independent reference entropy calculations for campaign 003."""

from __future__ import annotations

import itertools
import math


def entropy(weights):
    total = sum(weights)
    return -sum((w / total) * math.log(w / total) for w in weights if w > 0)


def ideal(state):
    return state["particle_count"] * math.log(state["volume"])


def two_level(state):
    beta = 1.0 / state["temperature"]
    return entropy([1.0, math.exp(-beta * state["energy_gap"])])


def ising(state):
    rows, cols = state["rows"], state["cols"]
    configurations = list(itertools.product((-1, 1), repeat=rows * cols))
    links = []
    for row in range(rows):
        for col in range(cols):
            i = row * cols + col
            if col + 1 < cols:
                links.append((i, i + 1))
            elif state["boundary"] == "periodic":
                links.append((i, row * cols))
            if row + 1 < rows:
                links.append((i, i + cols))
            elif state["boundary"] == "periodic":
                links.append((i, col))
    beta = 1.0 / state["temperature"]
    weights = []
    for spin in configurations:
        energy = -state["coupling"] * sum(spin[i] * spin[j] for i, j in links) - state["field"] * sum(spin)
        weights.append(math.exp(-beta * energy))
    return entropy(weights)


REFERENCE = {"IDEAL_GAS_BOUNDARY": ideal, "TWO_LEVEL_RESERVOIR": two_level, "ISING_RESERVOIR": ising}
