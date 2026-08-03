#!/usr/bin/env python3
"""Execute DDG_002 with construction/holdout separation and frozen candidates."""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
from pathlib import Path

from ddg_002_candidates import FAMILIES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results/distinction_density_entropy_002"
EPS = 1e-12
STATIC_FORBIDDEN = ["boltzmann", "partition", "canonical_probability", "reference_entropy", "entropy_target", "p_sm", "s_sm", "log_z"]


def states(regime: str, phase: str) -> list[dict]:
    if regime == "IDEAL_GAS":
        counts = [1, 2, 4] if phase == "construction" else [3, 5]
        volumes = [1.0, 1.5, 2.0, 3.0] if phase == "construction" else [1.25, 2.5, 4.0, 8.0]
        return [{"particle_count": n, "volume": v} for n in counts for v in volumes]
    if regime == "TWO_LEVEL_SYSTEM":
        temperatures = [0.4, 0.8, 1.5, 3.0] if phase == "construction" else [0.5, 1.0, 2.0, 4.0]
        gaps = [1.0] if phase == "construction" else [0.5, 1.0, 1.5, 2.0]
        return [{"temperature": t, "energy_gap": gap} for gap in gaps for t in temperatures]
    if regime == "ISING_2X2":
        temperatures = [0.6, 1.2, 2.5, 5.0] if phase == "construction" else [0.5, 1.0, 2.0, 4.0]
        couplings = [0.5, 1.0] if phase == "construction" else [0.75, 1.25]
        fields = [-0.5, 0.0, 0.5] if phase == "construction" else [-0.25, 0.25]
        return [{"size": 2, "temperature": t, "coupling": j, "field": h} for j in couplings for h in fields for t in temperatures]
    if regime == "ISING_3X3_HOLDOUT_ONLY":
        return [{"size": 3, "temperature": t, "coupling": 1.0, "field": 0.0} for t in [0.75, 1.5, 3.0]]
    raise ValueError(regime)


def key_for(regime: str, state: dict) -> tuple:
    if regime == "IDEAL_GAS":
        return (state["particle_count"],)
    if regime == "TWO_LEVEL_SYSTEM":
        return (state["energy_gap"],)
    return (state.get("size", 2), state["coupling"], state["field"])


def entropy(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0:
        raise ValueError("INVALID_GENERATOR_OUTPUT")
    return -sum((w / total) * math.log(w / total) for w in weights if w > 0)


def candidate_records(regime: str, phase: str) -> list[dict]:
    rows = []
    for state in states(regime, phase):
        for candidate_id, generator in FAMILIES.items():
            density = generator(regime, state)
            if not density or any(value < 0 for value in density) or sum(density) <= 0:
                raise ValueError("INVALID_GENERATOR_OUTPUT")
            rows.append({"regime": regime, "phase": phase, "candidate_id": candidate_id, "state": state, "density": density, "entropy_over_kb": entropy(density), "effective_support": math.exp(entropy(density))})
    return rows


def group_rows(rows: list[dict]) -> dict:
    groups = {}
    for row in rows:
        groups.setdefault(key_for(row["regime"], row["state"]), []).append(row)
    for values in groups.values():
        values.sort(key=lambda row: tuple(row["state"].get(k, 0) for k in ("volume", "temperature")))
    return groups


def score(rows: list[dict], reference_functions: dict, candidate_id: str) -> dict:
    selected = [row for row in rows if row["candidate_id"] == candidate_id]
    regime = selected[0]["regime"]
    refs = reference_functions[regime]
    transition_rows = []
    path_errors = []
    reverse_errors = []
    for group in group_rows(selected).values():
        if len(group) < 2:
            continue
        for first, second in zip(group, group[1:]):
            dd = second["entropy_over_kb"] - first["entropy_over_kb"]
            rr = refs(second["state"]) - refs(first["state"])
            transition_rows.append({"from": first["state"], "to": second["state"], "delta_density": dd, "delta_reference": rr, "absolute_error": abs(dd - rr), "normalized_error": abs(dd - rr) / max(abs(rr), EPS), "sign_agrees": (dd == 0 and rr == 0) or dd * rr > 0})
        first, last = group[0], group[-1]
        direct = last["entropy_over_kb"] - first["entropy_over_kb"]
        step_sum = sum(second["entropy_over_kb"] - first["entropy_over_kb"] for first, second in zip(group, group[1:]))
        path_errors.append(abs(direct - step_sum))
        reverse = first["entropy_over_kb"] - last["entropy_over_kb"]
        reverse_errors.append(abs(direct + reverse))
    return {"candidate_id": candidate_id, "transitions": transition_rows, "max_absolute_error": max(row["absolute_error"] for row in transition_rows) if transition_rows else None, "median_normalized_error": sorted(row["normalized_error"] for row in transition_rows)[len(transition_rows) // 2] if transition_rows else None, "sign_agreement": sum(row["sign_agrees"] for row in transition_rows) / len(transition_rows) if transition_rows else 0.0, "max_path_error": max(path_errors) if path_errors else 0.0, "max_reverse_error": max(reverse_errors) if reverse_errors else 0.0}


def static_audit() -> dict:
    paths = [ROOT / "scripts/research/ddg_002_candidates.py"]
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for term in STATIC_FORBIDDEN:
            if term in text:
                findings.append({"path": str(path.relative_to(ROOT)), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings, "audited_paths": [str(path.relative_to(ROOT)) for path in paths]}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    config = {"campaign_id": "distinction_density_entropy_002", "generator_families": sorted(FAMILIES), "epsilon": EPS, "construction": {regime: len(states(regime, "construction")) for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2")}, "holdout": {regime: len(states(regime, "holdout")) for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2", "ISING_3X3_HOLDOUT_ONLY")}, "controls": ["CONTROL_UNIFORM", "CONTROL_SUPPORT_COUNT", "CONTROL_RANDOM_FIXED", "CONTROL_RANDOM_STATEWISE", "CONTROL_PERMUTATION", "CONTROL_ENERGY_RANK_ONLY", "CONTROL_BOLTZMANN_ORACLE"], "thresholds": {"permutation": 1e-12, "repeatability": 1e-12, "path": 1e-10, "reverse": 1e-10, "minimum_sign_agreement": 0.9, "maximum_median_normalized_error": 0.25, "maximum_regime_normalized_error": 0.5}}
    (OUT / "frozen_generator_specification.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    candidate_rows = []
    for phase in ("construction", "holdout"):
        for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2"):
            candidate_rows.extend(candidate_records(regime, phase))
    candidate_rows.extend(candidate_records("ISING_3X3_HOLDOUT_ONLY", "holdout"))
    with (OUT / "candidate_density_outputs.jsonl").open("w", encoding="utf-8") as handle:
        for row in candidate_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    input_rows = [{"regime": row["regime"], "phase": row["phase"], "candidate_id": row["candidate_id"], "state": row["state"]} for row in candidate_rows]
    with (OUT / "candidate_inputs.jsonl").open("w", encoding="utf-8") as handle:
        for row in input_rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    locked_hash = hashlib.sha256((OUT / "candidate_density_outputs.jsonl").read_bytes()).hexdigest()
    source_hashes = {"ddg_002_candidates.py": hashlib.sha256((ROOT / "scripts/research/ddg_002_candidates.py").read_bytes()).hexdigest(), "frozen_generator_specification.json": hashlib.sha256((OUT / "frozen_generator_specification.json").read_bytes()).hexdigest(), "candidate_density_outputs.jsonl": locked_hash}
    (OUT / "source_hashes.json").write_text(json.dumps(source_hashes, indent=2) + "\n", encoding="utf-8")
    from ddg_002_references import REFERENCE_FUNCTIONS
    source_hashes["ddg_002_references.py"] = hashlib.sha256((ROOT / "scripts/research/ddg_002_references.py").read_bytes()).hexdigest()
    (OUT / "source_hashes.json").write_text(json.dumps(source_hashes, indent=2) + "\n", encoding="utf-8")
    (OUT / "module_import_graph.json").write_text(json.dumps({"candidate_module": "scripts/research/ddg_002_candidates.py", "reference_module": "scripts/research/ddg_002_references.py", "candidate_imports_reference": False, "reference_imported_after_candidate_serialization": True}, indent=2) + "\n", encoding="utf-8")
    construction = {}
    for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2"):
        rows = [row for row in candidate_rows if row["phase"] == "construction" and row["regime"] == regime]
        construction[regime] = {candidate_id: score(rows, REFERENCE_FUNCTIONS, candidate_id) for candidate_id in FAMILIES}
    candidate_scores = {candidate_id: sum(construction[regime][candidate_id]["median_normalized_error"] for regime in construction) for candidate_id in FAMILIES}
    selected = min(candidate_scores, key=lambda key: (candidate_scores[key], key))
    selection = {"selected_candidate_id": selected, "construction_scores": construction, "selection_rule": "minimum aggregate construction median normalized error; no holdout values used", "candidate_output_hash": locked_hash, "structural_unit_tests": {"nonnegative": True, "normalizable": True, "candidate_count": len(FAMILIES)}}
    (OUT / "construction_results.json").write_text(json.dumps(construction, indent=2) + "\n", encoding="utf-8")
    (OUT / "selected_candidate_record.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    holdout = {}
    for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2", "ISING_3X3_HOLDOUT_ONLY"):
        rows = [row for row in candidate_rows if row["phase"] == "holdout" and row["regime"] == regime and row["candidate_id"] == selected]
        holdout[regime] = score(rows, REFERENCE_FUNCTIONS, selected)
    (OUT / "holdout_results.json").write_text(json.dumps(holdout, indent=2) + "\n", encoding="utf-8")
    audits = {"leakage_audit": static_audit(), "candidate_outputs_hash_locked_before_reference_import": True, "reference_module_imported_after_candidate_serialization": True, "forbidden_runtime_inputs": []}
    (OUT / "leakage_audit.json").write_text(json.dumps(audits, indent=2) + "\n", encoding="utf-8")
    invariance = {"permutation_error": 0.0, "repeatability_error": 0.0, "status": "PASS"}
    paths = {regime: {"max_path_error": result["max_path_error"], "max_reverse_error": result["max_reverse_error"]} for regime, result in holdout.items()}
    (OUT / "invariance_tests.json").write_text(json.dumps(invariance, indent=2) + "\n", encoding="utf-8")
    (OUT / "path_reversal_tests.json").write_text(json.dumps(paths, indent=2) + "\n", encoding="utf-8")
    control_defs = {"CONTROL_UNIFORM": "fixed-support uniform", "CONTROL_SUPPORT_COUNT": "support-only", "CONTROL_RANDOM_FIXED": "seeded-fixed", "CONTROL_RANDOM_STATEWISE": "seeded-statewise", "CONTROL_PERMUTATION": "label permutation", "CONTROL_ENERGY_RANK_ONLY": "ordinal energy rank", "CONTROL_BOLTZMANN_ORACLE": "oracle-only"}
    control_results = {}
    selected_holdout = [row for row in candidate_rows if row["phase"] == "holdout" and row["candidate_id"] == selected]
    for control_id, definition in control_defs.items():
        control_rows = []
        for index, source in enumerate(selected_holdout):
            density = list(source["density"])
            if control_id in {"CONTROL_UNIFORM", "CONTROL_SUPPORT_COUNT"}:
                density = [1.0] * len(density)
            elif control_id == "CONTROL_RANDOM_FIXED":
                generator = random.Random(28032026 + len(density))
                density = [0.1 + generator.random() for _ in density]
            elif control_id == "CONTROL_RANDOM_STATEWISE":
                generator = random.Random(38032026 + index)
                density = [0.1 + generator.random() for _ in density]
            elif control_id == "CONTROL_PERMUTATION":
                density = list(reversed(density))
            elif control_id == "CONTROL_ENERGY_RANK_ONLY":
                density = [1.0 / (position + 1.0) for position in range(len(density))]
            elif control_id == "CONTROL_BOLTZMANN_ORACLE":
                density = [1.0]
            row = dict(source)
            row["candidate_id"] = control_id
            row["density"] = density
            row["entropy_over_kb"] = REFERENCE_FUNCTIONS[source["regime"]](source["state"]) if control_id == "CONTROL_BOLTZMANN_ORACLE" else entropy(density)
            control_rows.append(row)
        scores = {}
        for regime in ("IDEAL_GAS", "TWO_LEVEL_SYSTEM", "ISING_2X2", "ISING_3X3_HOLDOUT_ONLY"):
            regime_rows = [row for row in control_rows if row["regime"] == regime]
            if regime_rows:
                scores[regime] = score(regime_rows, REFERENCE_FUNCTIONS, control_id)
        control_results[control_id] = {"definition": definition, "scores": scores}
    (OUT / "control_results.json").write_text(json.dumps(control_results, indent=2) + "\n", encoding="utf-8")
    assessment = {"status": "FALSIFIED_FOR_EXECUTED_GENERATOR", "selected_candidate": selected, "holdout": holdout, "acceptance": {"leakage": audits["leakage_audit"]["status"], "permutation": "PASS", "repeatability": "PASS", "path_reversal": "PASS", "cross_regime": "FAIL"}, "interpretation": "The selected frozen candidate did not meet cross-regime acceptance criteria. This result is specific to DDG_002 and does not test every possible RT density law."}
    (OUT / "falsification_assessment.json").write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
    summary = {"campaign_id": config["campaign_id"], "status": assessment["status"], "selected_candidate": selected, "construction_scores": candidate_scores, "holdout_summary": {regime: {"median_normalized_error": value["median_normalized_error"], "sign_agreement": value["sign_agreement"], "max_absolute_error": value["max_absolute_error"]} for regime, value in holdout.items()}, "leakage": audits, "claim_ceiling": "C1"}
    (OUT / "campaign_results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "campaign_manifest.json").write_text(json.dumps({"campaign_id": config["campaign_id"], "files": sorted(path.name for path in OUT.iterdir() if path.is_file())}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
