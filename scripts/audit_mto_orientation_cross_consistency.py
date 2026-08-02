"""Cross-surface consistency audit for provisional MTO orientation evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "departments/research/reports"
CONTEXTS = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_context_instances.json"
EVIDENCE = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_witness_evidence.json"
PRIMARY = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_independent_validation_result.json"
SECONDARY = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_cross_validation_result.json"
OUT = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_cross_consistency_audit.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    contexts = load(CONTEXTS)
    evidence = load(EVIDENCE)
    primary = load(PRIMARY)
    secondary = load(SECONDARY)
    context_ids = {item["context_id"] for item in contexts["contexts"]}
    witness_context_ids = {item["context_id"] for item in evidence["witness_bindings"] if item["context_id"]}
    primary_outcomes = {item["fixture_id"]: item["actual"] for item in primary["results"]}
    secondary_outcomes = {item["fixture_id"]: item["actual"] for item in secondary["checks"]}
    source_checks = []
    for binding in evidence["source_bindings"]:
        path = ROOT / binding["path"]
        expected_hash = binding.get("sha256")
        source_checks.append({
            "source_id": binding["source_id"],
            "path": binding["path"],
            "exists": path.exists(),
            "hash_applicable": expected_hash is not None,
            "hash_matches": expected_hash is None or (path.exists() and sha256(path) == expected_hash),
        })
    checks = {
        "context_ids_match_witness_contexts": witness_context_ids <= context_ids,
        "context_instances_provisional": all(item["validation_status"] == "RESEARCH_PROVISIONAL" for item in contexts["contexts"]),
        "all_witnesses_unresolved": all(item["validation_status"] == "UNRESOLVED" for item in evidence["witness_bindings"]),
        "no_active_witnesses": evidence["disposition"]["active_witnesses"] == 0,
        "fixture_only_promotion_disabled": evidence["disposition"]["fixture_only_witnesses_promoted"] is False,
        "mto_selection_disabled": evidence["disposition"]["mto_selection_enabled"] is False,
        "validation_reports_agree": primary_outcomes == secondary_outcomes,
        "source_hashes_verified": all(item["exists"] and item["hash_matches"] for item in source_checks),
    }
    passed = all(checks.values())
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_CROSS_CONSISTENCY_AUDIT_001",
        "status": "PASS_CROSS_SURFACE_CONSISTENCY" if passed else "FAIL_CROSS_SURFACE_CONSISTENCY",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "source_checks": source_checks,
        "context_count": len(contexts["contexts"]),
        "witness_count": len(evidence["witness_bindings"]),
        "fixture_count": len(primary_outcomes),
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": [
            "This audit checks consistency among provisional records only.",
            "It does not validate mathematical witnesses or authorize MTO selection.",
        ],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
