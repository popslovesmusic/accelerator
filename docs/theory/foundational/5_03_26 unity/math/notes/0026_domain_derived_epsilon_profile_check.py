import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0026_domain_derived_epsilon_profile_fixtures.json").read_text(encoding="utf-8"))


def derive(context):
    if context["type"] != fixtures["required_type"]:
        return "REJECTED_TYPE", None, None
    if context["relation"] != fixtures["required_relation"]:
        return "REJECTED_RELATION", None, None
    positive = [value for value in context["raw_distinctions"] if value > 0]
    if not positive:
        return "UNDEFINED_EMPTY_POSITIVE_SET", None, None
    epsilon = min(positive)
    return "DERIVED_EXACT", epsilon, [epsilon, context["relation"], "EXACT_MINIMUM"]


results = []
for context in fixtures["contexts"]:
    status, epsilon, profile = derive(context)
    passed = status == context["expected_status"] and epsilon == context["expected_epsilon"] and profile == context["expected_profile"]
    results.append({"id": context["id"], "expected_status": context["expected_status"], "observed_status": status, "expected_epsilon": context["expected_epsilon"], "observed_epsilon": epsilon, "expected_profile": context["expected_profile"], "observed_profile": profile, "pass": passed})

derived = {context["id"]: derive(context) for context in fixtures["contexts"]}
left, right = fixtures["equal_derived_profile_pair"]
equal_derived_profile = derived[left][2] == derived[right][2] and derived[left][0] == "DERIVED_EXACT" and derived[right][0] == "DERIVED_EXACT"

out = {
    "check_id": "DOMAIN_DERIVED_EPSILON_PROFILE_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_DOMAIN_DERIVED_EPSILON_PROFILE" if all(r["pass"] for r in results) and equal_derived_profile else "FAIL_DOMAIN_DERIVED_EPSILON_PROFILE",
    "context_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "derived_from_raw_admissibility": True,
    "equal_derived_profile_checked": equal_derived_profile,
    "zero_admitted": False,
    "results": results,
    "limitations": ["finite declared raw candidates", "fixed positive_nonzero rule", "domain descriptors remain supplied inputs", "OBL-D-001E remains open"]
}
(ROOT / "0026_domain_derived_epsilon_profile_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
