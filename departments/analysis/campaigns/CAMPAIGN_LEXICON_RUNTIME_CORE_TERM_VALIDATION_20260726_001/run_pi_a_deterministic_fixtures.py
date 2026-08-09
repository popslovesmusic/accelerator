import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
FIXTURES = Path(__file__).with_name("pi_a_deterministic_local_fixtures.json")
OUTPUT = Path(__file__).with_name("pi_a_deterministic_fixture_execution.json")


def evaluate(fixture):
    values = fixture["input"]
    if fixture["obligation"] == "PO-010-001":
        return "MEMBERSHIP_CONDITION_SATISFIED" if all(values.values()) else "MEMBERSHIP_NOT_ESTABLISHED"
    if fixture["obligation"] == "PO-010-002":
        return "LOCAL_COMPOSITION_CONDITION_SATISFIED" if all(values.values()) else "COMPOSITION_BLOCKED"
    if fixture["obligation"] == "PO-010-003":
        return "FAILURE_BOUNDARY_RETAINED" if all(values.values()) else "EXCLUSION_BLOCKED"
    raise ValueError(f"Unsupported obligation: {fixture['obligation']}")


def main():
    fixture_set = json.loads(FIXTURES.read_text(encoding="utf-8"))
    outcomes = []
    for fixture in fixture_set["fixtures"]:
        actual = evaluate(fixture)
        outcomes.append({
            "fixture_id": fixture["id"],
            "obligation": fixture["obligation"],
            "expected": fixture["expected"],
            "actual": actual,
            "match": actual == fixture["expected"]
        })
    result = {
        "execution_id": "PI_A_DETERMINISTIC_FIXTURE_EXECUTION_20260726_001",
        "fixture_set_id": fixture_set["fixture_set_id"],
        "execution_mode": fixture_set["execution_mode"],
        "scope": fixture_set["scope"],
        "status": "PASS_FIXTURE_EXECUTION_ONLY" if all(item["match"] for item in outcomes) else "FAIL",
        "passed": sum(item["match"] for item in outcomes),
        "total": len(outcomes),
        "outcomes": outcomes,
        "claim_boundary": "Fixture agreement is not proof discharge and does not authorize lexicon promotion."
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
