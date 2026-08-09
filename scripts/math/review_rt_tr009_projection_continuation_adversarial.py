#!/usr/bin/env python3
"""Run finite negative tests against the TR-009 pipeline contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0034_rt_tr009_projection_continuation_adversarial_review_report.json"

CASES = [
    ("ADV-TR009-STAGE-001", "stage substitution is rejected", "stages", {"stages": ["condition", "projection", "organization", "rt", "rt"], "required": ["condition", "projection", "organization", "continuation", "rt"]}),
    ("ADV-TR009-STAGE-002", "duplicate stage is rejected", "stages", {"stages": ["condition", "projection", "organization", "continuation", "continuation"], "required": ["condition", "projection", "organization", "continuation", "rt"]}),
    ("ADV-TR009-PROV-001", "provenance drift is rejected", "provenance", {"values": ["src-1", "src-1", "src-2", "src-1", "src-1"]}),
    ("ADV-TR009-CTX-001", "proposition drift is rejected", "context", {"values": ["P-health", "P-health", "P-network", "P-health", "P-health"]}),
    ("ADV-TR009-ID-001", "condition and RT identity collapse is rejected", "identity", {"condition_id": "X", "rt_id": "X"}),
    ("ADV-TR009-CONT-001", "non-finite continuation is rejected", "finite", {"organization_nonempty": True, "continuation_finite": False}),
    ("ADV-TR009-ORG-001", "empty organization is rejected", "organization", {"organization_nonempty": False, "continuation_finite": True}),
    ("ADV-TR009-ORDER-001", "stage order mutation is rejected", "stages", {"stages": ["condition", "projection", "continuation", "organization", "rt"], "required": ["condition", "projection", "organization", "continuation", "rt"]}),
]


def rejects(contract: str, value: dict) -> bool:
    if contract == "stages":
        return value["stages"] != value["required"]
    if contract in {"provenance", "context"}:
        return len(set(value["values"])) != 1
    if contract == "identity":
        return value["condition_id"] == value["rt_id"]
    if contract == "finite":
        return not value["continuation_finite"]
    if contract == "organization":
        return not value["organization_nonempty"]
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    results = []
    for case_id, name, contract, value in CASES:
        rejected = rejects(contract, value)
        results.append({"case_id": case_id, "name": name, "status": "REJECTED" if rejected else "ESCAPED", "detail": "REJECTED" if rejected else "invalid case escaped contract"})
    escaped = [item for item in results if item["status"] == "ESCAPED"]
    report = {"report_id": "0034_rt_tr009_projection_continuation_adversarial_review_report", "fixture_set_id": "0034_rt_tr009_projection_continuation_fixtures", "review_type": "finite_negative_contract_review", "status": "PASS" if not escaped else "FAIL", "claim_ceiling": "C1", "case_count": len(results), "rejected_count": len(results) - len(escaped), "escaped_count": len(escaped), "results": results, "limitations": ["Finite negative tests only; no external ontology or physical projection is tested.", "The review does not establish internal mathematics for lawful projection or continuation."]}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if escaped else 0


if __name__ == "__main__":
    raise SystemExit(main())
