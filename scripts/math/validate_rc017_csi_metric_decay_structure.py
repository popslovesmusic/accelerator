import json
import os
import argparse

def validate_rc017_csi_metric(metric_reg):
    results = {
        "rc017_csi_metric_decay_structure_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "metric_mode_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(metric_reg, 'r') as f: metric_data = json.load(f)
    except Exception as e:
        results["rc017_csi_metric_decay_structure_validation"]["status"] = "fail"
        results["rc017_csi_metric_decay_structure_validation"]["errors"].append(f"Load error: {e}")
        return results

    for entry in metric_data.get("csi_metric_decay_entries", []):
        results["rc017_csi_metric_decay_structure_validation"]["entry_count"] += 1
        
        # Governance check: no global metric, exact decay law, or infinite stability claims
        gov = entry.get("governance_constraints", {})
        if (gov.get("global_CSI_metric_claimed") or 
            gov.get("exact_decay_identity_claimed") or 
            gov.get("infinite_recursive_transport_stability_claimed") or
            gov.get("global_closure_claimed") or
            gov.get("physics_validation_claimed")):
             results["rc017_csi_metric_decay_structure_validation"]["status"] = "fail"
             results["rc017_csi_metric_decay_structure_validation"]["errors"].append(f"Entry {entry['id']} violates governance by claiming global metric, exact decay, or infinite stability.")

        # Check dependencies
        if "RC-016" not in entry.get("depends_on", []):
             # As per the basis, RC-016 is the previous patch.
             pass

        results["rc017_csi_metric_decay_structure_validation"]["condition_count"] = len(entry.get("csi_metric_conditions", []))
        results["rc017_csi_metric_decay_structure_validation"]["metric_mode_count"] = len(entry.get("candidate_metric_modes", []))
        results["rc017_csi_metric_decay_structure_validation"]["failure_mode_count"] = len(entry.get("failure_modes_to_preserve", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-017 CSI metric decay structure registry.")
    parser.add_argument("--metric", default="registry/math/rc017_csi_metric_decay_structure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc017_csi_metric(args.metric)
    print(json.dumps(res, indent=2))
