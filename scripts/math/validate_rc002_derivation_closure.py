import json
import os
import argparse

def validate_rc002_derivation_closure(rc002_reg, chain_reg):
    results = {
        "rc002_derivation_closure_validation": {
            "status": "pass",
            "step_count": 0,
            "condition_count": 0,
            "failure_mode_preservation_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(rc002_reg, 'r') as f: rc002_data = json.load(f)
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
    except Exception as e:
        results["rc002_derivation_closure_validation"]["status"] = "fail"
        results["rc002_derivation_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    if rc002_data["meta"]["target_chain"] != "RC-002":
        results["rc002_derivation_closure_validation"]["status"] = "fail"
        results["rc002_derivation_closure_validation"]["errors"].append(f"Registry target mismatch: expected RC-002, found {rc002_data['meta']['target_chain']}")

    # Check dependencies
    required_deps = ["operator_composition", "symbolic_reduction_chains", "reduction_step_formalization"]
    for dep in required_deps:
        if dep not in rc002_data.get("depends_on", []):
             results["rc002_derivation_closure_validation"]["status"] = "warning"
             results["rc002_derivation_closure_validation"]["warnings"].append(f"Missing recommended dependency: {dep}")

    # Check steps
    for step in rc002_data.get("step_resolutions", []):
        results["rc002_derivation_closure_validation"]["step_count"] += 1
        if not step.get("satisfied_conditions"):
             results["rc002_derivation_closure_validation"]["status"] = "warning"
             results["rc002_derivation_closure_validation"]["warnings"].append(f"Step {step['step_id']} has no satisfied legality conditions.")

    results["rc002_derivation_closure_validation"]["condition_count"] = len(rc002_data.get("preservation_conditions", []))
    results["rc002_derivation_closure_validation"]["failure_mode_preservation_count"] = len(rc002_data.get("failure_modes_to_preserve", []))

    # Governance safety: check for deterministic or global claims
    if rc002_data["closure_criteria_check"].get("is_global_closure_claim") or rc002_data["closure_criteria_check"].get("is_physics_validation_claim"):
         results["rc002_derivation_closure_validation"]["status"] = "fail"
         results["rc002_derivation_closure_validation"]["errors"].append("RC-002 registry violates governance by asserting global closure or physics validation.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-002 derivation closure refinement.")
    parser.add_argument("--rc002", default="registry/math/rc002_derivation_closure_registry.json")
    parser.add_argument("--chains", default="registry/math/reduction_chain_registry.json")
    
    args = parser.parse_args()
    res = validate_rc002_derivation_closure(args.rc002, args.chains)
    print(json.dumps(res, indent=2))
