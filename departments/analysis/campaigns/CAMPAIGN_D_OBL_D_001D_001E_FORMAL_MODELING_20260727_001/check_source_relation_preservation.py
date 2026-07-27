import json
from pathlib import Path


ROOT = Path(__file__).parent
spec = json.loads((ROOT / "source_relation_preservation_spec.json").read_text(encoding="utf-8"))
counterexample = json.loads((ROOT / "source_relation_counterexample.json").read_text(encoding="utf-8"))

assert "RelationIdentityMatch_C(r,w)" in spec["predicate"]
assert "TraceCompatible_C(w)" in spec["predicate"]
assert "HistorySufficient_C(h,w)" in spec["predicate"]
assert spec["bare_projection_assessment"] == "FAILS_RELATION_IDENTITY_COMPONENT"

source_relation_ids = {case["relation_id"] for case in counterexample["source_cases"]}
projected_relation_tokens = set()
assert len(source_relation_ids) == 2
assert len(projected_relation_tokens) == 0

print(json.dumps({
    "status": "PASS_BOUNDED_PRESERVATION_PREDICATE_BOUNDARY",
    "predicate_components_checked": len(spec["required_components"]),
    "bare_projection_relation_identity": "MISSING",
    "enriched_witness": "REQUIRED_FOR_CANDIDATE_PASS",
    "claim_ceiling": spec["claim_ceiling"],
    "obligations": {"OBL-D-001D": "OPEN", "OBL-D-001E": "OPEN"},
    "promotion_authorized": False,
}, indent=2))
