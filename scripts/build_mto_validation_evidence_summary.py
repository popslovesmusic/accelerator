"""Build a provenance-gated summary of bounded MTO validation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "departments/research/reports"
FILES = {
    "fixture_specification": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_set.json",
    "bounded_evaluation": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_result.json",
    "independent_cross_validation": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_cross_validation_result.json",
    "consistency_audit": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_cross_consistency_audit.json",
    "fail_closed": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_fail_closed_result.json",
    "fail_closed_cross_validation": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_fail_closed_cross_validation.json",
    "mutation_matrix": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_mutation_matrix_result.json",
    "mutation_matrix_cross_validation": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_mutation_matrix_cross_validation.json",
    "property_matrix": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_property_matrix_result.json",
    "property_matrix_cross_validation": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_property_matrix_cross_validation.json",
    "witness_evidence": BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_witness_evidence.json",
}
OUT = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_validation_evidence_summary.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    data = {name: read(path) for name, path in FILES.items()}
    statuses = {
        name: value.get("status")
        for name, value in data.items()
        if name != "fixture_specification" and name != "witness_evidence"
    }
    pass_statuses = all(status.startswith("PASS") for status in statuses.values())
    evidence = data["witness_evidence"]
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_VALIDATION_EVIDENCE_SUMMARY_001",
        "status": "PASS_PROVENANCE_GATED_VALIDATION_SUMMARY" if pass_statuses else "FAIL_PROVENANCE_GATED_VALIDATION_SUMMARY",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "artifact_hashes": {name: digest(path) for name, path in FILES.items()},
        "artifact_statuses": statuses,
        "validated_bounded_behavior": {
            "fixture_count": 8,
            "property_case_count": data["property_matrix"].get("case_count"),
            "property_active_case_count": data["property_matrix"].get("active_case_count"),
            "mutation_case_count": data["mutation_matrix"].get("case_count"),
            "fail_closed_case_count": len(data["fail_closed"].get("tests", [])),
        },
        "provisional_unresolved_semantics": {
            "witness_count": len(evidence.get("witness_bindings", [])),
            "active_witnesses": evidence.get("disposition", {}).get("active_witnesses"),
            "unresolved_witnesses": evidence.get("disposition", {}).get("unresolved_witnesses"),
            "mto_selection_enabled": evidence.get("disposition", {}).get("mto_selection_enabled"),
        },
        "remaining_requirements": evidence.get("remaining_requirements", []),
        "canonical_math_modified": False,
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "claim_boundary": "bounded fixture behavior is validated; canonical orientation semantics and witness validity remain unresolved",
        "nonclaims": [
            "The summary does not activate witnesses.",
            "The summary does not enable MTO selection.",
            "The summary does not establish canonical mathematical semantics.",
        ],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if pass_statuses else 2


if __name__ == "__main__":
    raise SystemExit(main())
