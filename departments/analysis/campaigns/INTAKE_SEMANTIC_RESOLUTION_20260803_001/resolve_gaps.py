import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def evaluate(name, candidate_a, candidate_b, commitments, observations):
    a_pass = all(candidate_a.get(k) == v for k, v in commitments.items() if k in candidate_a)
    b_pass = all(candidate_b.get(k) == v for k, v in commitments.items() if k in candidate_b)
    return {
        "question": name,
        "candidate_a": candidate_a,
        "candidate_b": candidate_b,
        "commitments_tested": commitments,
        "observations": observations,
        "candidate_a_satisfies_declared_commitments": a_pass,
        "candidate_b_satisfies_declared_commitments": b_pass,
        "selects_unique_candidate": a_pass != b_pass,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    results = [
        evaluate(
            "DIV-01 boundary exclusion semantics",
            {"boundary_conditioned": True, "source_family_unchanged": True, "typed_empty_failure": True, "rule": "exclude_opposing"},
            {"boundary_conditioned": True, "source_family_unchanged": True, "typed_empty_failure": True, "rule": "retain_aligned"},
            {"boundary_conditioned": True, "source_family_unchanged": True, "typed_empty_failure": True},
            "Both candidates satisfy the currently declared commitments; their admissible families differ.",
        ),
        evaluate(
            "DIV-03 MTO selection",
            {"deterministic": True, "history_retained": True, "selector": "lexicographic"},
            {"deterministic": True, "history_retained": True, "selector": "frequency_ranked"},
            {"deterministic": True, "history_retained": True},
            "Both selectors satisfy determinism and provenance retention but produce different RT outputs.",
        ),
        evaluate(
            "DIV-04 recursive termination",
            {"termination_declared": True, "finite_guard": True, "policy": "depth_limit"},
            {"termination_declared": True, "finite_guard": True, "policy": "cycle_detection"},
            {"termination_declared": True, "finite_guard": True},
            "Both policies prevent the tested finite runaway, but produce different continuation traces; neither is derived by a well-founded measure.",
        ),
    ]
    unresolved = [r for r in results if not r["selects_unique_candidate"]]
    payload = {
        "campaign_id": "INTAKE_SEMANTIC_RESOLUTION_20260803_001",
        "status": "UNRESOLVED_SEMANTIC_GAPS" if unresolved else "SEMANTIC_CANDIDATE_SELECTED",
        "results": results,
        "unresolved_questions": [r["question"] for r in unresolved],
        "new_campaign_required": bool(unresolved),
        "claim_ceiling": "C1",
        "canonicality": "NON_CANONICAL",
        "promotion_status": "HOLD_C1",
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT)), "status": payload["status"], "unresolved": len(unresolved)}, indent=2))


if __name__ == "__main__":
    main()
