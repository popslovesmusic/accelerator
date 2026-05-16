import json
import os
from datetime import datetime

def validate_topology_transition_mapping():
    registry_path = "registry/math/topology_transition_registry.json"
    boundary_registry_path = "registry/math/topology_boundary_condition_registry.json"
    primitive_registry_path = "registry/math/topology_primitive_registry.json"
    result_path = "validation/results/topology_transition_mapping_result.json"
    
    report = {
        "validation_id": "VAL-TOPO-TRANS-001",
        "status": "pass",
        "transitions_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology transition registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    if not os.path.exists(boundary_registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology boundary registry missing for dependency check")
        return report
    with open(boundary_registry_path, 'r') as f:
        bound_registry = json.load(f)
    valid_boundaries = [b["id"] for b in bound_registry["boundary_conditions"]]
    # Also include the primitives and specific constraints that might act as boundaries
    valid_boundaries.extend(["non_globalization_constraint", "admissibility_exhaustion_boundary"])

    if not os.path.exists(primitive_registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology primitive registry missing for dependency check")
        return report
    with open(primitive_registry_path, 'r') as f:
        prim_registry = json.load(f)
    valid_primitives = [p["term"] for p in prim_registry["primitives"]]

    required_transition_ids = [
        "local_region_expansion",
        "local_region_contraction",
        "boundary_reclassification",
        "corridor_activation",
        "corridor_deactivation",
        "orientation_realignment",
        "failure_containment_transition",
        "invalid_globalization_attempt"
    ]
    
    # 2. Completeness and Mandatory Field Check
    registered_ids = [t["id"] for t in registry["transition_types"]]
    for t_id in required_transition_ids:
        if t_id not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required transition type missing: {t_id}")
            
    for t in registry["transition_types"]:
        report["transitions_verified"] += 1
        required_fields = [
            "id", "definition", "source_condition", "target_condition",
            "admissibility_requirement", "boundary_dependencies",
            "allowed_effects", "prohibited_effects", "failure_mode", "status_labels"
        ]
        for field in required_fields:
            if field not in t:
                report["status"] = "fail"
                report["governance_violations"].append(f"transition {t.get('id', 'unknown')} missing field: {field}")
        
        # 3. Dependency Check
        if "boundary_dependencies" in t:
            for dep in t["boundary_dependencies"]:
                if dep not in valid_boundaries and dep not in valid_primitives:
                     report["status"] = "fail"
                     report["governance_violations"].append(f"transition {t['id']} depends on unknown boundary or primitive: {dep}")

        # 4. Mandatory Status Labels
        if "status_labels" in t:
            labels = t["status_labels"]
            for label in ["NOT_PROVEN", "STRICTLY_LOCAL", "NON_PHYSICAL_ANALOG_MODEL"]:
                if label not in labels:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"transition {t['id']} missing mandatory status label: {label}")

    # 5. Blocked Language Check
    blocked_language = registry["blocked_language"]
    content_str = json.dumps(registry).lower()
    for phrase in blocked_language:
        if phrase in content_str:
            if content_str.count(phrase) > 1:
                report["status"] = "fail"
                report["governance_violations"].append(f"blocked language detected in transition registry: '{phrase}'")

    # 6. Invalid Transition Conditions Check
    if not registry.get("invalid_transition_conditions"):
        report["status"] = "fail"
        report["governance_violations"].append("invalid transition conditions missing from registry")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_transition_mapping()
    print(json.dumps(res, indent=2))
