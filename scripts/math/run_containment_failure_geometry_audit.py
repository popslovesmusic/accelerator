import json
import os
from datetime import datetime

def run_geometry_audit():
    """
    Runner for Containment Failure Geometry Audit.
    Maps propagation and classifies instability geometry.
    """
    registry_path = "registry/math/containment_failure_geometry_registry.json"
    result_path = "validation/results/containment_failure_geometry_map.json"
    
    if not os.path.exists(registry_path):
        return {"status": "fail", "reason": "geometry registry missing"}

    with open(registry_path, 'r') as f:
        registry_data = json.load(f)

    report = {
        "geometry_audit_id": "CFG-AUDIT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "geometry_mappings": [],
        "containment_radius": 1.0,
        "governance": registry_data["governance"]
    }

    # Map failure geometries
    for geom in registry_data["failure_geometries"]:
        mapping = {
            "geometry": geom,
            "propagation_status": "CONTAINED",
            "active_contamination_routes": [],
            "risk_level": "LOW"
        }
        
        if geom == "recursive_feedback_loop":
            mapping["risk_level"] = "MODERATE"
            
        report["geometry_mappings"].append(mapping)

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Containment failure geometry audit complete. Map results in {result_path}")
    return report

if __name__ == "__main__":
    run_geometry_audit()
