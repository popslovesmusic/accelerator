import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def record(name, invariant, observed, implication):
    return {"test": name, "invariant": invariant, "observed": observed, "implication": implication}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results = []

    # 056: repaired exclusion removes one orientation; alternate semantics retain only boundary-aligned orientation.
    orientations = {"north", "east", "south", "west"}
    repaired = tuple(sorted(orientations - {"south"}))
    alternate = tuple(sorted({"north"}))
    results.append(record("056_exclusion_rule", repaired == alternate, {"repaired": repaired, "alternate": alternate}, "Boundary-conditioned admissibility is specification-dependent unless the operator semantics are frozen."))

    # 057: full typed equality versus relation-only equality.
    forward = ("D_A", "P_A", "D_B", "P_B", "r", "ctx-1")
    same_relation_different_context = ("D_A", "P_A", "D_B", "P_B", "r", "ctx-2")
    full_equal = forward == same_relation_different_context
    relation_only_equal = forward[4] == same_relation_different_context[4]
    results.append(record("057_identity_equivalence_rule", full_equal == relation_only_equal, {"full_typed_equal": full_equal, "relation_only_equal": relation_only_equal}, "Orientation identity depends on whether context and endpoint typing are part of equality."))

    # 060: lexicographic output versus frequency-ranked output.
    sequence = ("p2", "p1", "p2", "p0")
    lexicographic = tuple(sorted(sequence))
    frequency_ranked = tuple(item for item, _ in Counter(sequence).most_common())
    results.append(record("060_mto_selector", lexicographic == frequency_ranked, {"lexicographic": lexicographic, "frequency_ranked": frequency_ranked}, "MTO output depends on the declared selector when ordering and multiplicity interact."))

    # 060: depth termination versus cycle-detection termination.
    path = ("RT_A", "RT_B", "RT_A", "RT_B", "RT_A")
    depth_stop = path[:3]
    cycle_stop = path[:2]
    results.append(record("060_termination_policy", depth_stop == cycle_stop, {"depth_stop": depth_stop, "cycle_stop": cycle_stop}, "Termination policy changes the finite continuation trace."))

    divergences = sum(not r["invariant"] for r in results)
    payload = {
        "campaign_id": "INTAKE_SPECIFICATION_INDEPENDENCE_20260803_001",
        "status": "SPECIFICATION_DEPENDENCE_FOUND" if divergences else "SPECIFICATION_INDEPENDENCE_SUPPORTED",
        "tests": results,
        "divergence_count": divergences,
        "claim_ceiling": "C1",
        "conclusion": "The tested bounded results depend materially on semantic choices for exclusion, identity equivalence, MTO selection, and termination.",
        "required_action": "Freeze these semantics as explicit model parameters before any broader claim.",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "status": payload["status"], "divergence_count": divergences, "tests": len(results)}, indent=2))


if __name__ == "__main__":
    main()
