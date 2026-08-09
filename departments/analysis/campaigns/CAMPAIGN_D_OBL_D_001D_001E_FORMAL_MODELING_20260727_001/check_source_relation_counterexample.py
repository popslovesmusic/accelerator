import json
from pathlib import Path


ROOT = Path(__file__).parent
spec = json.loads((ROOT / "projection_spec.json").read_text(encoding="utf-8"))
evidence = json.loads((ROOT / "source_relation_counterexample.json").read_text(encoding="utf-8"))
prefix = spec["contexts"][evidence["context"]]["projection_prefix"]

projected = []
for case in evidence["source_cases"]:
    projected.append({
        "case_id": case["case_id"],
        "projected_source": prefix + case["source"]["value"],
        "projected_target": prefix + case["target"]["value"],
    })

assert projected == evidence["projected_cases"]
assert evidence["source_cases"][0]["relation_id"] != evidence["source_cases"][1]["relation_id"]
assert evidence["source_cases"][0]["source"]["id"] != evidence["source_cases"][1]["source"]["id"]
assert projected[0]["projected_source"] == projected[1]["projected_source"]
assert projected[0]["projected_target"] == projected[1]["projected_target"]

print(json.dumps({
    "status": "PASS_BOUNDED_COUNTEREXAMPLE",
    "cases_checked": len(projected),
    "projected_collision": True,
    "source_identity_distinct": True,
    "relation_identity_distinct": True,
    "claim_ceiling": evidence["claim_ceiling"],
    "universal_claim": False,
}, indent=2))
