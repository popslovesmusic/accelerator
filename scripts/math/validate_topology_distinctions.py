import json
import os
from datetime import datetime

def validate_topology_distinctions():
    registry_path = "registry/math/topology_behavioral_distinction_registry.json"
    result_path = "validation/results/topology_distinctions_result.json"
    
    report = {
        "validation_id": "VAL-TOPO-DIST-001",
        "status": "pass",
        "distinctions_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("topology distinction registry missing")
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    required_distinction_ids = [
        "DIST-001",
        "DIST-002",
        "DIST-003",
        "DIST-004"
    ]
    
    # 1. Completeness and Mandatory Field Check
    registered_ids = [d["id"] for d in registry["required_distinctions"]]
    for d_id in required_distinction_ids:
        if d_id not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required distinction missing: {d_id}")
            
    for d in registry["required_distinctions"]:
        report["distinctions_verified"] += 1
        required_fields = [
            "id", "pair", "definitions", "fundamental_difference", "collapse_risk"
        ]
        for field in required_fields:
            if field not in d:
                report["status"] = "fail"
                report["governance_violations"].append(f"distinction {d.get('id', 'unknown')} missing field: {field}")
        
        # 2. Check for Pair Consistency
        if len(d.get("pair", [])) != 2:
            report["status"] = "fail"
            report["governance_violations"].append(f"distinction {d['id']} pair must have exactly two terms")
        else:
            for term in d["pair"]:
                if term not in d["definitions"]:
                    report["status"] = "fail"
                    report["governance_violations"].append(f"distinction {d['id']} missing definition for term: {term}")

    # 3. Mandatory Status Labels in Registry
    for label in ["NOT_PROVEN", "STRICTLY_LOCAL", "NON_PHYSICAL_ANALOG_MODEL"]:
        if label not in registry.get("mandatory_status_labels", []):
            report["status"] = "fail"
            report["governance_violations"].append(f"registry missing mandatory status label: {label}")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_distinctions()
    print(json.dumps(res, indent=2))
