#!/usr/bin/env python3
"""Independently verify DDG_002 from serialized candidate outputs."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/distinction_density_entropy_002"
TOL = 1e-12


def entropy(values):
    total = sum(values)
    return -sum((value / total) * math.log(value / total) for value in values if value > 0)


def reference(regime: str, state: dict) -> float:
    if regime == "IDEAL_GAS":
        return state["particle_count"] * math.log(state["volume"])
    if regime == "TWO_LEVEL_SYSTEM":
        beta = 1.0 / state["temperature"]
        return entropy([1.0, math.exp(-beta * state["energy_gap"])])
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
        energy = -state["coupling"] * sum(spin[i] * spin[j] for i, j in edges) - state["field"] * sum(spin)
        weights.append(math.exp(-beta * energy))
    return entropy(weights)


def key_for(regime: str, state: dict) -> tuple:
    if regime == "IDEAL_GAS":
        return (state["particle_count"],)
    if regime == "TWO_LEVEL_SYSTEM":
        return (state["energy_gap"],)
    return (state.get("size", 2), state["coupling"], state["field"])


def main() -> int:
    rows = [json.loads(line) for line in (OUT / "candidate_density_outputs.jsonl").read_text(encoding="utf-8").splitlines()]
    selected = json.loads((OUT / "selected_candidate_record.json").read_text(encoding="utf-8"))["selected_candidate_id"]
    selected_rows = [row for row in rows if row["candidate_id"] == selected and row["phase"] == "holdout"]
    grouped = {}
    for row in selected_rows:
        grouped.setdefault((row["regime"], key_for(row["regime"], row["state"])), []).append(row)
    recomputed = {}
    for (regime, group_key), group in grouped.items():
        group.sort(key=lambda row: tuple(row["state"].get(k, 0) for k in ("volume", "temperature")))
        transitions = []
        for first, second in zip(group, group[1:]):
            density_delta = entropy(second["density"]) - entropy(first["density"])
            reference_delta = reference(regime, second["state"]) - reference(regime, first["state"])
            transitions.append({"absolute_error": abs(density_delta - reference_delta), "sign_agrees": density_delta == 0 and reference_delta == 0 or density_delta * reference_delta > 0})
        recomputed.setdefault(regime, []).extend(transitions)
    summary = {regime: {"max_absolute_error": max(item["absolute_error"] for item in values), "sign_agreement": sum(item["sign_agrees"] for item in values) / len(values)} for regime, values in recomputed.items()}
    recorded = json.loads((OUT / "holdout_results.json").read_text(encoding="utf-8"))
    matches = {regime: abs(summary[regime]["max_absolute_error"] - recorded[regime]["max_absolute_error"]) <= TOL and abs(summary[regime]["sign_agreement"] - recorded[regime]["sign_agreement"]) <= TOL for regime in summary}
    result = {"verification_id": "distinction_density_entropy_002_independent_verification", "status": "PASS" if all(matches.values()) else "FAIL", "selected_candidate": selected, "serialized_output_hash": hashlib.sha256((OUT / "candidate_density_outputs.jsonl").read_bytes()).hexdigest(), "recomputed": summary, "comparison_to_recorded_holdout": matches, "conclusion": "Independent recomputation reproduces the DDG_002 holdout findings; it verifies the executed result, not the universal validity or impossibility of distinction-density models."}
    (OUT / "independent_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (OUT / "campaign_manifest.json").write_text(json.dumps({"campaign_id": "distinction_density_entropy_002", "files": sorted(path.name for path in OUT.iterdir() if path.is_file())}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
