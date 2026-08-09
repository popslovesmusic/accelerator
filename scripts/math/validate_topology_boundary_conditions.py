import json
import os
from datetime import datetime

def validate_topology_boundary_conditions():
    registry_path = "registry/math/topology_boundary_condition_registry.json"
    primitive_registry_path = "registry/math/topology_primitive_registry.json"
    result_path = "validation/results/topology_boundary_conditions_result.json"
    
    report = {
        "validation_id": "VAL-TOPO-BOUND-001",
        "status": "pass",
        "boundaries_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology boundary condition registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Load primitive registry to check dependencies
    if not os.path.exists(primitive_registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology primitive registry missing for dependency check")
        return report
        
    with open(primitive_registry_path, 'r') as f:
        prim_registry = json.load(f)
    frozen_primitives = [p["term"] for p in prim_registry["primitives"]]

    required_types = [
        "hard_boundary",
        "soft_boundary",
        "orientation_boundary",
        "admissibility_exhaustion_boundary",
        "corridor_exit_boundary",
        "failure_containment_boundary"
    ]
    
    # 2. Completeness and Mandatory Field Check
    registered_ids = [b["id"] for b in registry["boundary_conditions"]]
    for b_type in required_types:
        if b_type not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required boundary type missing: {b_type}")
            
    for b in registry["boundary_conditions"]:
        report["boundaries_verified"] += 1
        required_fields = [
            "id", "definition", "allowed_crossing_behavior", 
            "prohibited_crossing_behavior", "locality_constraint", 
            "failure_behavior", "depends_on_primitives", "status_labels"
        ]
        for field in required_fields:
            if field not in b:
                report["status"] = "fail"
                report["governance_violations"].append(f"boundary {b.get('id', 'unknown')} missing field: {field}")
        
        # 3. Primitive Dependency Check (Must point only to frozen primitives)
        if "depends_on_primitives" in b:
            for dep in b["depends_on_primitives"]:
                if dep not in frozen_primitives:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"boundary {b['id']} depends on non-frozen primitive: {dep}")

        # 4. Mandatory Status Labels
        if "status_labels" in b:
            labels = b["status_labels"]
            for label in ["NOT_PROVEN", "STRICTLY_LOCAL", "NON_PHYSICAL_ANALOG_MODEL"]:
                if label not in labels:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"boundary {b['id']} missing mandatory status label: {label}")

    # 5. Blocked Language Check
    blocked_language = registry["blocked_language"]
    content_str = json.dumps(registry).lower()
    for phrase in blocked_language:
        if phrase in content_str:
            # occurrences count > count in blocked_language list itself
            if content_str.count(phrase) > 1:
                report["status"] = "fail"
                report["governance_violations"].append(f"blocked language detected in registry: '{phrase}'")

    # 6. Leakage Detection Section Check
    if not registry.get("topology_leakage_detection") or not registry["topology_leakage_detection"].get("detects"):
        report["status"] = "fail"
        report["governance_violations"].append("topology leakage detection section missing or incomplete")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_boundary_conditions()
    print(json.dumps(res, indent=2))
