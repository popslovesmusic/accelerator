import json
import os
from datetime import datetime

def validate_topology_primitives():
    registry_path = "registry/math/topology_primitive_registry.json"
    result_path = "validation/results/topology_primitives_result.json"
    
    report = {
        "validation_id": "VAL-TOPO-PRIM-001",
        "status": "pass",
        "primitives_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology primitive registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    required_terms = [
        "local_topology_region",
        "finite_admissibility_boundary",
        "topology_variation",
        "local_continuation_path",
        "orientation_neighbor_relation",
        "bounded_traversal_corridor",
        "topology_failure_boundary",
        "non_globalization_constraint"
    ]
    
    # 1. Completeness and Mandatory Field Check
    registered_terms = [p["term"] for p in registry["primitives"]]
    for term in required_terms:
        if term not in registered_terms:
            report["status"] = "fail"
            report["governance_violations"].append(f"required primitive missing: {term}")
            
    for p in registry["primitives"]:
        report["primitives_verified"] += 1
        for field in ["id", "term", "definition", "scope", "status", "allowed_use", "prohibited_use"]:
            if field not in p:
                report["status"] = "fail"
                report["governance_violations"].append(f"primitive {p.get('term', 'unknown')} missing field: {field}")
        
        # 2. Mandatory Status Labels
        if p.get("scope") != "STRICTLY_LOCAL":
            report["status"] = "fail"
            report["governance_violations"].append(f"primitive {p['term']} scope must be STRICTLY_LOCAL")
        if p.get("status") != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append(f"primitive {p['term']} status must be NOT_PROVEN")

    # 3. Blocked Language Check
    blocked_language = registry["blocked_language"]
    content_str = json.dumps(registry).lower()
    for phrase in blocked_language:
        if phrase in content_str:
            # Note: The phrase IS in the blocked_language list itself, so we must be careful.
            # We check if it occurs MORE THAN once (once in the list, once in a field).
            if content_str.count(phrase) > 1:
                report["status"] = "fail"
                report["governance_violations"].append(f"blocked language detected: '{phrase}'")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_primitives()
    print(json.dumps(res, indent=2))
