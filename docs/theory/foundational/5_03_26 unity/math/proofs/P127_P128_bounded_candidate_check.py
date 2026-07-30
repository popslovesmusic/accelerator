import json
from pathlib import Path

FIXTURES = Path(__file__).with_name("P127_P128_bounded_candidate_fixtures.json")

def evaluate(case):
    if case["proof"] == "P127":
        return "DERIVATION_ADMITTED" if case["premises_complete"] and case["same_context"] else "DERIVATION_BLOCKED"
    return "DERIVATION_ADMITTED" if case["epsilon"] > 0 and case["distinction"] >= case["epsilon"] and case["context_nonempty"] and case["distinct"] else "DERIVATION_BLOCKED"

def main():
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    results = []
    for case in payload["cases"]:
        observed = evaluate(case)
        results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})
    report = {
        "check_id": "D_P127_P128_BOUNDED_CANDIDATE_CHECK_20260730",
        "status": "PASS_BOUNDED_PROOF_CANDIDATE_CHECK" if all(r["pass"] for r in results) else "FAIL",
        "fixture_count": len(results),
        "passed": sum(r["pass"] for r in results),
        "claim_ceiling": payload["claim_ceiling"],
        "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
        "limitations": ["conditional premises", "finite fixtures", "human review pending", "no universal theorem"],
        "results": results
    }
    out = FIXTURES.with_name("P127_P128_bounded_candidate_check_report.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
