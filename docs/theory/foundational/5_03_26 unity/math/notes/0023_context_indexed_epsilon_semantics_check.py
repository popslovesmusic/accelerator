import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0023_context_indexed_epsilon_semantics_fixtures.json").read_text(encoding="utf-8"))


def evaluate(case):
    values = case["admissible_positive_distinctions"]
    if not values:
        return "UNDEFINED_EMPTY_ADMISSIBLE_SET", None
    if case["exact_minimum_established"]:
        return "EXACT_MINIMUM", min(values)
    return "INFIMUM_CANDIDATE", case.get("infimum_candidate")


results = []
for case in fixtures["cases"]:
    observed_status, observed_epsilon = evaluate(case)
    passed = observed_status == case["expected_status"] and observed_epsilon == case["expected_epsilon"]
    results.append({"id": case["id"], "expected_status": case["expected_status"], "observed_status": observed_status, "expected_epsilon": case["expected_epsilon"], "observed_epsilon": observed_epsilon, "pass": passed})

out = {
    "check_id": "CONTEXT_INDEXED_EPSILON_SEMANTICS_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_BOUNDED_EPSILON_SEMANTICS" if all(r["pass"] for r in results) else "FAIL_BOUNDED_EPSILON_SEMANTICS",
    "fixture_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "context_indexed": True,
    "exact_minimum_distinguished_from_infimum": True,
    "zero_admitted": False,
    "results": results,
    "limitations": ["finite synthetic contexts", "infimum branch is retained as candidate, not derived", "no cross-context threshold law", "OBL-D-001E remains open"]
}
(ROOT / "0023_context_indexed_epsilon_semantics_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
