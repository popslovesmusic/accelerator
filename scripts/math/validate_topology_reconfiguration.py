import json
import os
from datetime import datetime

def validate_topology_reconfiguration():
    registry_path = "registry/math/topology_reconfiguration_registry.json"
    transition_registry_path = "registry/math/topology_transition_registry.json"
    boundary_registry_path = "registry/math/topology_boundary_condition_registry.json"
    primitive_registry_path = "registry/math/topology_primitive_registry.json"
    result_path = "validation/results/topology_reconfiguration_validation_result.json"
    
    report = {
        "validation_id": "VAL-TOPO-RECONFIG-001",
        "status": "pass",
        "modes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology reconfiguration registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    def load_valid_ids(path, key, sub_key="id"):
        if not os.path.exists(path): return []
        with open(path, 'r') as f:
            data = json.load(f)
            return [item[sub_key] for item in data.get(key, [])]

    valid_transitions = load_valid_ids(transition_registry_path, "transition_types")
    valid_boundaries = load_valid_ids(boundary_registry_path, "boundary_conditions")
    
    if not os.path.exists(primitive_registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology primitive registry missing for dependency check")
        return report
    with open(primitive_registry_path, 'r') as f:
        prim_registry = json.load(f)
    valid_primitives = [p["term"] for p in prim_registry["primitives"]]

    required_mode_ids = [
        "local_neighbor_rebinding",
        "bounded_path_rerouting",
        "boundary_induced_reconfiguration",
        "corridor_relinking",
        "orientation_neighbor_reassignment",
        "failure_driven_reconfiguration",
        "admissibility_budget_reallocation",
        "invalid_global_reconfiguration"
    ]
    
    # 2. Completeness and Mandatory Field Check
    registered_ids = [m["id"] for m in registry["reconfiguration_modes"]]
    for m_id in required_mode_ids:
        if m_id not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required reconfiguration mode missing: {m_id}")
            
    for m in registry["reconfiguration_modes"]:
        report["modes_verified"] += 1
        required_fields = [
            "id", "definition", "trigger_condition", "allowed_internal_change",
            "prohibited_externalization", "boundary_dependencies",
            "transition_dependencies", "admissibility_effect",
            "failure_containment_behavior", "status_labels"
        ]
        for field in required_fields:
            if field not in m:
                report["status"] = "fail"
                report["governance_violations"].append(f"reconfiguration mode {m.get('id', 'unknown')} missing field: {field}")
        
        # 3. Dependency Check
        if "boundary_dependencies" in m:
            for dep in m["boundary_dependencies"]:
                if dep not in valid_boundaries and dep not in ["non_globalization_constraint", "admissibility_exhaustion_boundary"]:
                     report["status"] = "fail"
                     report["governance_violations"].append(f"mode {m['id']} depends on unknown boundary: {dep}")

        if "transition_dependencies" in m:
            for dep in m["transition_dependencies"]:
                if dep not in valid_transitions:
                     report["status"] = "fail"
                     report["governance_violations"].append(f"mode {m['id']} depends on unknown transition: {dep}")

        # 4. Mandatory Status Labels
        if "status_labels" in m:
            labels = m["status_labels"]
            for label in ["NOT_PROVEN", "STRICTLY_LOCAL", "NON_PHYSICAL_ANALOG_MODEL"]:
                if label not in labels:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"mode {m['id']} missing mandatory status label: {label}")

    # 5. Blocked Language Check
    blocked_language = registry["blocked_language"]
    content_str = json.dumps(registry).lower()
    for phrase in blocked_language:
        if phrase in content_str:
            if content_str.count(phrase) > 1:
                report["status"] = "fail"
                report["governance_violations"].append(f"blocked language detected in reconfiguration registry: '{phrase}'")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_reconfiguration()
    print(json.dumps(res, indent=2))
