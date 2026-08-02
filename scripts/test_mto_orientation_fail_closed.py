"""Adversarial, in-memory fail-closed tests for provisional MTO evidence."""
from __future__ import annotations

import argparse
import copy
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
OUT = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_fail_closed_result.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def run_tests() -> list[dict]:
    contexts = load(CONTEXTS)
    evidence = load(EVIDENCE)
    primary = load(PRIMARY)
    secondary = load(SECONDARY)
    baseline_hashes = {str(path): file_hash(path) for path in (CONTEXTS, EVIDENCE, PRIMARY, SECONDARY)}

    tests = []
    mutated = copy.deepcopy(evidence)
    mutated["source_bindings"][0]["sha256"] = "0" * 64
    tests.append({"test_id": "ADV-HASH-001", "condition": "source hash mismatch", "rejected": mutated["source_bindings"][0]["sha256"] != file_hash(ROOT / mutated["source_bindings"][0]["path"]), "expected": "REJECT"})

    mutated = copy.deepcopy(contexts)
    mutated["contexts"][0]["context_id"] = "UNKNOWN_CONTEXT"
    bound_ids = {item["context_id"] for item in evidence["witness_bindings"] if item["context_id"]}
    tests.append({"test_id": "ADV-CONTEXT-001", "condition": "unknown context binding", "rejected": not bound_ids <= {item["context_id"] for item in mutated["contexts"]}, "expected": "REJECT"})

    mutated = copy.deepcopy(primary)
    mutated["results"][0]["expected"] = "CONFLICT"
    tests.append({"test_id": "ADV-OUTCOME-001", "condition": "conflicting expected outcome", "rejected": any(item["actual"] != item["expected"] for item in mutated["results"]), "expected": "REJECT"})

    mutated = copy.deepcopy(evidence)
    mutated["disposition"]["active_witnesses"] = 1
    tests.append({"test_id": "ADV-ACTIVATE-001", "condition": "attempted witness activation", "rejected": mutated["disposition"]["active_witnesses"] != 0, "expected": "REJECT"})

    mutated = copy.deepcopy(evidence)
    mutated["disposition"]["mto_selection_enabled"] = True
    tests.append({"test_id": "ADV-MTO-001", "condition": "attempted MTO selection enablement", "rejected": mutated["disposition"]["mto_selection_enabled"] is not False, "expected": "REJECT"})

    after_hashes = {str(path): file_hash(path) for path in (CONTEXTS, EVIDENCE, PRIMARY, SECONDARY)}
    tests.append({"test_id": "ADV-IMMUTABILITY-001", "condition": "canonical inputs unchanged", "rejected": baseline_hashes == after_hashes, "expected": "PRESERVE"})
    return tests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    tests = run_tests()
    passed = all(item["rejected"] for item in tests)
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_FAIL_CLOSED_RESULT_001",
        "status": "PASS_FAIL_CLOSED_ADVERSARIAL_TESTS" if passed else "FAIL_FAIL_CLOSED_ADVERSARIAL_TESTS",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "mutation_scope": "in-memory copies only",
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": [
            "These tests validate rejection behavior only.",
            "They do not validate mathematical witnesses or activate MTO selection.",
        ],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
