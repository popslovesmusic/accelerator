import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixtures = json.loads((ROOT / "0025_epsilon_input_profile_independent_validation_fixtures.json").read_text(encoding="utf-8"))


def validate(profile):
    values = profile["admissible_positive_distinctions"]
    if profile["m"] == "INFIMUM_CANDIDATE":
        return "RETAINED_INFIMUM_CANDIDATE"
    if not values:
        return "REJECTED_EMPTY"
    if profile["a"] is None or profile["a"] <= 0:
        return "REJECTED_NONPOSITIVE"
    if profile["m"] == "EXACT_MINIMUM" and profile["a"] != min(values):
        return "REJECTED_EXACT_MISMATCH"
    return "VALID_EXACT_PROFILE"


results = []
for profile in fixtures["profiles"]:
    observed = validate(profile)
    results.append({"id": profile["id"], "expected": profile["expected"], "observed": observed, "pass": observed == profile["expected"]})

left = next(p for p in fixtures["profiles"] if p["id"] == fixtures["equal_profile_pair"]["left"])
right = next(p for p in fixtures["profiles"] if p["id"] == fixtures["equal_profile_pair"]["right"])
equal_profile_inputs = (left["a"], left["d"], left["m"]) == (right["a"], right["d"], right["m"])

out = {
    "check_id": "EPSILON_INPUT_PROFILE_INDEPENDENT_VALIDATION_CHECK_20260726",
    "obligation_id": "OBL-D-001E",
    "status": "PASS_INDEPENDENT_EPSILON_PROFILE_VALIDATION" if all(r["pass"] for r in results) and equal_profile_inputs else "FAIL_INDEPENDENT_EPSILON_PROFILE_VALIDATION",
    "profile_count": len(results),
    "passed": sum(r["pass"] for r in results),
    "failed": sum(not r["pass"] for r in results),
    "equal_profile_inputs_checked": equal_profile_inputs,
    "results": results,
    "limitations": ["finite supplied distinction sets", "profile classes are declared", "no universal admissibility derivation", "OBL-D-001E remains open"]
}
(ROOT / "0025_epsilon_input_profile_independent_validation_check_report.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, sort_keys=True))
