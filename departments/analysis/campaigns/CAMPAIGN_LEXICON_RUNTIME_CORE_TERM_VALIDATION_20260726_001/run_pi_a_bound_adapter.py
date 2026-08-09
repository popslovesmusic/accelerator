import json
from pathlib import Path

from pi_a_local_adapter import PiALocalAdapter


BASE = Path(__file__).resolve().parent
FIXTURES = BASE / "pi_a_deterministic_local_fixtures.json"
OUTPUT = BASE / "pi_a_bound_adapter_execution.json"


def main():
    fixture_set = json.loads(FIXTURES.read_text(encoding="utf-8"))
    adapter = PiALocalAdapter()
    outcomes = []
    for fixture in fixture_set["fixtures"]:
        actual = adapter.evaluate(fixture)
        outcomes.append({
            "fixture_id": fixture["id"],
            "obligation": fixture["obligation"],
            "expected": fixture["expected"],
            "actual": actual,
            "match": actual == fixture["expected"]
        })
    result = {
        "execution_id": "PI_A_BOUND_ADAPTER_EXECUTION_20260726_001",
        "adapter_contract": adapter.contract_id,
        "scope": adapter.scope,
        "status": "PASS_NONCANONICAL_ADAPTER" if all(item["match"] for item in outcomes) else "FAIL",
        "passed": sum(item["match"] for item in outcomes),
        "total": len(outcomes),
        "outcomes": outcomes,
        "claim_boundary": "Noncanonical adapter agreement is not theorem proof, engine validation, or lexicon promotion."
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
