import json
from pathlib import Path

FIXTURES = Path(__file__).with_name("0031_d_independent_adversarial_review_fixtures.json")

def evaluate(case):
    if case["class"] == "representability":
        if case["type_p"] != "TYPE_PROJECTION_C" or case["type_q"] != "TYPE_PROJECTION_C":
            return "REJECT_TYPE"
        if case["witness_context"] != case["context"]:
            return "REJECT_CONTEXT"
        if not case["witness"]:
            return "REJECT_WITNESS"
        if not case["history"]:
            return "REJECT_HISTORY"
        return "REPRESENTABLE"
    if case["class"] == "noncollapse":
        if case["epsilon"] <= 0 or not case["context_nonempty"]:
            return "REJECT_PROFILE"
        if not case["distinct"] or case["distinction"] < case["epsilon"]:
            return "REJECT_DISTINCTION"
        return "ADMIT"
    route = case["route"]
    return "CONDITIONAL_TERMINATION" if all(route[i] > route[i + 1] for i in range(len(route) - 1)) else "BLOCK_CYCLE"

def main():
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    results = []
    for case in payload["cases"]:
        observed = evaluate(case)
        results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})
    report = {
        "review_id": "D_INDEPENDENT_ADVERSARIAL_REVIEW_20260730",
        "status": "PASS_BOUNDED_REVIEW_OPEN_OBLIGATIONS" if all(r["pass"] for r in results) else "FAIL",
        "fixture_count": len(results),
        "passed": sum(r["pass"] for r in results),
        "claim_ceiling": "C1_DEFINED_PROVISIONAL",
        "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
        "limitations": ["independent finite fixtures", "conditional normalization only", "no universal preservation", "no injectivity or reversibility"],
        "results": results
    }
    out = FIXTURES.with_name("0031_d_independent_adversarial_review_report.json")
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
