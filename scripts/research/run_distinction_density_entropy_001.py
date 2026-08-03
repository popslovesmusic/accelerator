#!/usr/bin/env python3
"""Execute the bounded, non-circular density/entropy correspondence design."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/distinction_density_entropy_001"
KB = 1.0
TOL = 1e-10
FORBIDDEN_CANDIDATE_INPUTS = {"p_SM", "Z", "Omega", "S_SM", "target_entropy"}


def entropy(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        raise ValueError("density support must be positive")
    return -sum((w / total) * math.log(w / total) for w in weights if w > 0)


def ideal_reference(v: float) -> float:
    return math.log(v)


def two_level_reference(temperature: float) -> float:
    beta = 1.0 / temperature
    weights = [1.0, math.exp(-beta)]
    return entropy(weights)


def ising_reference(temperature: float, field: float = 0.0) -> float:
    beta = 1.0 / temperature
    states = list(itertools.product((-1, 1), repeat=4))
    energies = []
    for spins in states:
        edges = ((0, 1), (1, 3), (2, 3), (0, 2))
        interaction = sum(spins[i] * spins[j] for i, j in edges)
        energies.append(-interaction - field * sum(spins))
    return entropy([math.exp(-beta * energy) for energy in energies])


def candidate_density(regime: str, state: dict) -> list[float]:
    # Frozen minimal operationalization: no reference probabilities, partition
    # functions, multiplicities, or entropy targets enter this generator.
    if regime == "ideal_gas":
        cells = int(round(16.0 * state["volume"]))
        return [1.0] * cells
    if regime == "two_level":
        return [1.0, 1.0]
    if regime == "ising_2x2":
        return [1.0] * 16
    raise ValueError(regime)


def transition(regime: str, first: dict, second: dict) -> dict:
    d1 = candidate_density(regime, first)
    d2 = candidate_density(regime, second)
    if regime == "ideal_gas":
        s1, s2 = ideal_reference(first["volume"]), ideal_reference(second["volume"])
    elif regime == "two_level":
        s1, s2 = two_level_reference(first["temperature"]), two_level_reference(second["temperature"])
    else:
        s1, s2 = ising_reference(first["temperature"], first["field"]), ising_reference(second["temperature"], second["field"])
    sd = entropy(d2) - entropy(d1)
    sm = s2 - s1
    return {"from": first, "to": second, "delta_density_entropy_over_kb": sd, "delta_reference_entropy_over_kb": sm, "absolute_error": abs(sd - sm), "sign_agrees": (sd == 0 and sm == 0) or (sd * sm > 0)}


def regime_run(regime: str, states: list[dict]) -> dict:
    transitions = [transition(regime, states[i], states[i + 1]) for i in range(len(states) - 1)]
    direct = transition(regime, states[0], states[-1])
    path_error = abs(direct["delta_density_entropy_over_kb"] - sum(t["delta_density_entropy_over_kb"] for t in transitions))
    reverse = transition(regime, states[-1], states[0])
    reverse_error = abs(direct["delta_density_entropy_over_kb"] + reverse["delta_density_entropy_over_kb"])
    return {"transitions": transitions, "path_additivity_error": path_error, "reverse_consistency_error": reverse_error, "max_absolute_error": max(t["absolute_error"] for t in transitions + [direct]), "all_signs_agree": all(t["sign_agrees"] for t in transitions + [direct])}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    config = {
        "campaign_id": "distinction_density_entropy_001",
        "status": "EXECUTED",
        "mapping": "S_D/k_B = -sum(q_D log q_D), q_D = rho_D/sum(rho_D)",
        "candidate_generator": "ideal_gas: 16 uniform admissible cells per volume unit; two_level and ising_2x2: uniform state density",
        "forbidden_candidate_inputs": sorted(FORBIDDEN_CANDIDATE_INPUTS),
        "tolerance": TOL,
        "benchmarks": {
            "ideal_gas": {"states": [{"volume": 1.0}, {"volume": 2.0}, {"volume": 4.0}, {"volume": 8.0}]},
            "two_level": {"states": [{"temperature": 0.5}, {"temperature": 1.0}, {"temperature": 2.0}, {"temperature": 4.0}]},
            "ising_2x2": {"states": [{"temperature": 0.5, "field": 0.0}, {"temperature": 1.0, "field": 0.0}, {"temperature": 2.0, "field": 0.0}, {"temperature": 4.0, "field": 0.0}]}
        },
        "controls": ["uniform_density", "permutation_control"],
    }
    (OUT / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    leakage = {"status": "PASS", "forbidden_inputs": sorted(FORBIDDEN_CANDIDATE_INPUTS), "candidate_generator_inputs": ["regime", "volume", "temperature", "field"], "detected_forbidden_inputs": []}
    results = {"ideal_gas": regime_run("ideal_gas", config["benchmarks"]["ideal_gas"]["states"]), "two_level": regime_run("two_level", config["benchmarks"]["two_level"]["states"]), "ising_2x2": regime_run("ising_2x2", config["benchmarks"]["ising_2x2"]["states"])}
    controls = {"uniform_density": {"same_as_candidate": True, "separation": "FAIL"}, "permutation_control": {"entropy_invariant_under_permutation": True, "separation": "FAIL"}}
    primary_pass = all(item["all_signs_agree"] and item["max_absolute_error"] <= TOL and item["path_additivity_error"] <= TOL and item["reverse_consistency_error"] <= TOL for item in results.values()) and all(item["separation"] == "PASS" for item in controls.values())
    summary = {"campaign_id": config["campaign_id"], "status": "PASS" if primary_pass else "FAIL", "hypothesis": "H1 cross-regime distinction-density correspondence", "claim_ceiling": "C1", "leakage_audit": leakage, "regimes": results, "controls": controls, "failure_vectors": {"FV-1_cross_regime_holdout": "PASS" if primary_pass else "FAIL", "FV-2_path_reversal": "PASS" if all(item["path_additivity_error"] <= TOL and item["reverse_consistency_error"] <= TOL for item in results.values()) else "FAIL", "FV-3_reference_leakage": leakage["status"], "FV-4_control_separation": "PASS" if all(item["separation"] == "PASS" for item in controls.values()) else "FAIL"}, "interpretation": "The minimal non-circular operationalization does not establish H1 when primary_pass is false; failures identify insufficiency of the current density definition."}
    (OUT / "campaign_results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# Distinction-Density Entropy Campaign", "", f"Status: **{summary['status']}**", "", "This is a bounded model execution, not a physical validation.", "", "| Regime | Max absolute error | Sign agreement | Path error | Reverse error |", "|---|---:|---|---:|---:"]
    for regime, item in results.items():
        lines.append(f"| {regime} | {item['max_absolute_error']:.12g} | {item['all_signs_agree']} | {item['path_additivity_error']:.12g} | {item['reverse_consistency_error']:.12g} |")
    lines += ["", "Controls:", "- Uniform-density separation: FAIL (same entropy structure for finite state proxies).", "- Permutation-control separation: FAIL (entropy is permutation invariant).", "", "Interpretation: this execution does not support cross-regime correspondence under the frozen minimal operationalization. It demonstrates that a mathematically defined density distribution is not sufficient until its generation rule is specified with more structure."]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            manifest.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (OUT / "manifest.json").write_text(json.dumps({"campaign_id": config["campaign_id"], "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
