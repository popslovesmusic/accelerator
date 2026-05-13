import json
import os
import argparse

def validate_mt001_theorem_consolidation(consolidation_reg):
    results = {
        "mt001_theorem_consolidation_validation": {
            "status": "pass",
            "entry_count": 0,
            "condition_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(consolidation_reg, 'r') as f: con_data = json.load(f)
    except Exception as e:
        results["mt001_theorem_consolidation_validation"]["status"] = "fail"
        results["mt001_theorem_consolidation_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Basic entry tracking
    results["mt001_theorem_consolidation_validation"]["entry_count"] = 1
    
    # Check dependencies
    required_deps = ["MT-001", "RC-001", "RC-002", "minimal_theorems"]
    for dep in required_deps:
        if dep not in con_data.get("depends_on", []):
             results["mt001_theorem_consolidation_validation"]["status"] = "warning"
             results["mt001_theorem_consolidation_validation"]["warnings"].append(f"Missing recommended dependency: {dep}")

    # Governance check: no global closure or physics validation
    for condition in con_data.get("theorem_consolidation_conditions", []):
        results["mt001_theorem_consolidation_validation"]["condition_count"] += 1
        
    # Failure mode preservation
    results["mt001_theorem_consolidation_validation"]["failure_mode_count"] = len(con_data.get("failure_modes_to_preserve", []))

    # Strict check: no global closure claim
    if "global_closure_claims_blocked" not in [c["name"] for c in con_data["theorem_consolidation_conditions"] if c["status"] == "satisfied"]:
         results["mt001_theorem_consolidation_validation"]["status"] = "fail"
         results["mt001_theorem_consolidation_validation"]["errors"].append("MT-001 consolidation fails to explicitly block global closure claims.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate MT-001 local theorem consolidation registry.")
    parser.add_argument("--consolidation", default="registry/math/mt001_theorem_consolidation_registry.json")
    
    args = parser.parse_args()
    res = validate_mt001_theorem_consolidation(args.consolidation)
    print(json.dumps(res, indent=2))
