import json
import os
from datetime import datetime

def validate_aspect_relation_trace_schema():
    registry_path = "registry/math/aspect_relation_trace_schema.json"
    result_path = "validation/results/aspect_relation_trace_schema_result.json"
    
    report = {
        "validation_id": "VAL-PALG-TRACE-VALID-001",
        "status": "pass",
        "examples_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("trace schema registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Schema Status Check
    if registry.get("schema_status") != "CANDIDATE_TRACE_SCHEMA":
        report["status"] = "fail"
        report["governance_violations"].append("illegal schema status in registry")
    
    # 2. Core Rule Check
    rule = registry.get("core_rule", {})
    if rule.get("name") != "aspect_traceability_rule":
        report["status"] = "fail"
        report["governance_violations"].append("missing core traceability rule")

    # 3. Trace Schema Completeness
    schema = registry.get("trace_schema", {})
    required_fields = ["source_relation", "non_separability_acknowledged", "primitive_status", "promotion_allowed"]
    for field in required_fields:
        if field not in schema:
            report["status"] = "fail"
            report["governance_violations"].append(f"required schema field missing: {field}")

    # 4. Mandatory Fixed Values
    if schema.get("primitive_status") is not False:
        report["status"] = "fail"
        report["governance_violations"].append("primitive_status must be fixed to false in trace schema")
    if schema.get("promotion_allowed") is not False:
        report["status"] = "fail"
        report["governance_violations"].append("promotion_allowed must be fixed to false in trace schema")

    # 5. Invalid Trace Conditions Presence
    if not registry.get("invalid_trace_conditions"):
        report["status"] = "fail"
        report["governance_violations"].append("missing invalid trace conditions")

    # 6. Forbidden Claims Check
    forbidden = registry.get("forbidden_uses", [])
    if "independent_primitive" not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden independent primitive check")

    # 7. Example Verification
    examples = registry.get("valid_trace_examples", [])
    for ex in examples:
        report["examples_verified"] += 1
        if "source_relation" not in ex or not ex["source_relation"]:
            report["status"] = "fail"
            report["governance_violations"].append(f"example {ex.get('trace_id')} missing source relation")
        if ex.get("non_separability_acknowledged") is not True:
            report["status"] = "fail"
            report["governance_violations"].append(f"example {ex.get('trace_id')} failed non-separability acknowledgment")

    # 8. Governance Status
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_aspect_relation_trace_schema()
    print(json.dumps(res, indent=2))
