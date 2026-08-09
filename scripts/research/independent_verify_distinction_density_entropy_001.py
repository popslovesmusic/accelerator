#!/usr/bin/env python3
"""Independently recompute and verify the bounded entropy campaign result.

This implementation intentionally does not import the campaign runner.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/distinction_density_entropy_001"
TOL = 1e-12


def shannon(weights: list[float]) -> float:
    total = sum(weights)
    return -sum((w / total) * math.log(w / total) for w in weights if w > 0)


def reference(regime: str, state: dict) -> float:
    if regime == "ideal_gas":
        return math.log(state["volume"])
    if regime == "two_level":
        beta = 1.0 / state["temperature"]
        return shannon([1.0, math.exp(-beta)])
    beta = 1.0 / state["temperature"]
    spins = list(itertools.product((-1, 1), repeat=4))
    edges = ((0, 1), (1, 3), (2, 3), (0, 2))
    weights = []
    for spin in spins:
        energy = -sum(spin[i] * spin[j] for i, j in edges) - state["field"] * sum(spin)
        weights.append(math.exp(-beta * energy))
    return shannon(weights)


def candidate(regime: str, state: dict) -> float:
    if regime == "ideal_gas":
        count = int(round(16.0 * state["volume"]))
    elif regime == "two_level":
        count = 2
    else:
        count = 16
    return math.log(count)


def recompute(regime: str, states: list[dict]) -> dict:
    records = []
    for first, second in zip(states, states[1:]):
        density_delta = candidate(regime, second) - candidate(regime, first)
        reference_delta = reference(regime, second) - reference(regime, first)
        records.append({"density_delta": density_delta, "reference_delta": reference_delta, "absolute_error": abs(density_delta - reference_delta), "sign_agrees": density_delta == 0 and reference_delta == 0 or density_delta * reference_delta > 0})
    first, last = states[0], states[-1]
    direct_density = candidate(regime, last) - candidate(regime, first)
    direct_reference = reference(regime, last) - reference(regime, first)
    direct = {"density_delta": direct_density, "reference_delta": direct_reference, "absolute_error": abs(direct_density - direct_reference), "sign_agrees": direct_density == 0 and direct_reference == 0 or direct_density * direct_reference > 0}
    return {"records": records, "direct": direct, "max_absolute_error": max(record["absolute_error"] for record in records + [direct]), "all_signs_agree": all(record["sign_agrees"] for record in records + [direct])}


def main() -> int:
    config = json.loads((OUT / "config.json").read_text(encoding="utf-8"))
    campaign = json.loads((OUT / "campaign_results.json").read_text(encoding="utf-8"))
    recomputed = {regime: recompute(regime, data["states"]) for regime, data in config["benchmarks"].items()}
    independent_matches = {}
    for regime, data in recomputed.items():
        recorded = campaign["regimes"][regime]
        independent_matches[regime] = {
            "max_error_match": abs(data["max_absolute_error"] - recorded["max_absolute_error"]) <= TOL,
            "sign_result_match": data["all_signs_agree"] == recorded["all_signs_agree"],
        }
    result = {
        "verification_id": "distinction_density_entropy_001_independent_verification",
        "status": "PASS" if all(all(item.values()) for item in independent_matches.values()) else "FAIL",
        "independent_implementation": True,
        "campaign_result_reproduced": all(all(item.values()) for item in independent_matches.values()),
        "recomputed": recomputed,
        "comparison_to_recorded_campaign": independent_matches,
        "independent_conclusion": "The recorded H1 failure is reproducible under an independent implementation; this verifies the campaign result, not the truth or falsity of all possible density models.",
        "source_hashes": {
            "config.json": hashlib.sha256((OUT / "config.json").read_bytes()).hexdigest(),
            "campaign_results.json": hashlib.sha256((OUT / "campaign_results.json").read_bytes()).hexdigest(),
        },
    }
    (OUT / "independent_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            manifest.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "manifest.json").write_text(json.dumps({"campaign_id": "distinction_density_entropy_001", "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
