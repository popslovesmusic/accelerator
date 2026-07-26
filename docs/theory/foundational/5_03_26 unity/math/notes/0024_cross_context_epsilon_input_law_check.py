import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0024_cross_context_epsilon_input_law_fixtures.json").read_text(encoding="utf-8"))


def threshold(context):
    inputs = fixtures["contexts"][context]["inputs"]
    if inputs["a"] is None or inputs["a"] <= 0 or inputs["m"] not in {"EXACT_MINIMUM", "INFIMUM_CANDIDATE"}:
        return None
    return inputs["a"]


def compare(case):
    left, right = threshold(case["left"]), threshold(case["right"])
    if left is None or right is None:
        return "UNDEFINED_PARTICIPANT" if case["right"] == "C_EMPTY" else "REJECTED_PARTICIPANT"
    if fixtures["contexts"][case["left"]]["inputs"] == fixtures["contexts"][case["right"]]["inputs"]:
        return "EQUAL_THRESHOLDS" if left == right else "FAILED_EQUAL_INPUT_LAW"
    return "NO_EQUALITY_ASSERTED"


results = []
for case in fixtures["comparisons"]:
    observed = compare(case)
    results.append({"id": case["id"], "expected": case["expected"], "observed": observed, "pass": observed == case["expected"]})

out = {
    "check_id": "CROSS_CONTEXT_EPSILON_INPUT_LAW_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_BOUNDED_CROSS_CONTEXT_INPUT_LAW" if all(r["pass"] for r in results) else "FAIL_BOUNDED_CROSS_CONTEXT_INPUT_LAW",
    "context_count": len(fixtures["contexts"]),
    "comparison_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "universal_constant_rejected": threshold("C_ALPHA") != threshold("C_GAMMA"),
    "conditional_equal_input_law_checked": True,
    "results": results,
    "limitations": ["declared synthetic input profiles", "conditional bounded law only", "no universal derivation", "OBL-D-001E remains open"]
}
(ROOT / "0024_cross_context_epsilon_input_law_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
