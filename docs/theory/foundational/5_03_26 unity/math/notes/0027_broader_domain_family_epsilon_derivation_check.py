import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0027_broader_domain_family_epsilon_derivation_fixtures.json").read_text(encoding="utf-8"))


def derive(case):
    supported = {
        ("TYPE_AFFECT_EFFECT", "positive_nonzero"),
        ("TYPE_INDEXED_CLOSURE", "positive_integer"),
        ("TYPE_CONTINUATION", "positive_resolution")
    }
    if (case["type"], case["rule"]) not in supported:
        return "REJECTED_UNSUPPORTED_RULE", None
    if case["rule"] == "positive_integer":
        filtered = [x for x in case["raw"] if x >= 1 and float(x).is_integer()]
    else:
        filtered = [x for x in case["raw"] if x > 0]
    if not filtered:
        return "UNDEFINED_EMPTY_FILTERED_SET", None
    return "DERIVED_EXACT", min(filtered)


results = []
for case in fixtures["families"]:
    status, epsilon = derive(case)
    passed = status == case["expected"] and epsilon == case["epsilon"]
    results.append({"id": case["id"], "expected_status": case["expected"], "observed_status": status, "expected_epsilon": case["epsilon"], "observed_epsilon": epsilon, "pass": passed})

out = {
    "check_id": "BROADER_DOMAIN_FAMILY_EPSILON_DERIVATION_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_BOUNDED_DOMAIN_FAMILY_DERIVATION" if all(r["pass"] for r in results) else "FAIL_BOUNDED_DOMAIN_FAMILY_DERIVATION",
    "family_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "supported_rule_count": 3,
    "unsupported_rules_rejected": any(r["observed_status"] == "REJECTED_UNSUPPORTED_RULE" for r in results),
    "results": results,
    "limitations": ["finite supplied family descriptors", "three declared admissibility rules", "no universal family taxonomy", "OBL-D-001E remains open"]
}
(ROOT / "0027_broader_domain_family_epsilon_derivation_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
