import json
import os
import argparse

def validate_rc001_step02_derivation_supported(supported_reg, decision_reg, closure_reg):
    results = {
        "rc001_step02_derivation_supported_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(supported_reg, 'r') as f: s_data = json.load(f).get("rc001_step02_derivation_supported", {})
        with open(decision_reg, 'r') as f: d_data = json.load(f).get("rc001_step02_elevation_decision", {})
        with open(closure_reg, 'r') as f: c_data = json.load(f)
    except Exception as e:
        results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
        results["rc001_step02_derivation_supported_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Check supported registry
    if s_data.get("status") != "derivation_supported":
         results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
         results["rc001_step02_derivation_supported_validation"]["errors"].append("Supported registry status mismatch.")

    # Check decision registry
    if d_data.get("action") != "elevate_to_derivation_supported":
         results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
         results["rc001_step02_derivation_supported_validation"]["errors"].append("Decision registry action mismatch.")

    # Check closure registry for STEP-02
    steps = c_data.get("step_resolutions", [])
    step02 = next((s for s in steps if s["step_id"] == "STEP-02"), None)
    if not step02:
        results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
        results["rc001_step02_derivation_supported_validation"]["errors"].append("STEP-02 not found in closure registry.")
    elif step02.get("status") != "derivation_supported":
        results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
        results["rc001_step02_derivation_supported_validation"]["errors"].append("STEP-02 status in closure registry is not derivation_supported.")
    elif len(step02.get("blockers", [])) > 0:
        results["rc001_step02_derivation_supported_validation"]["status"] = "fail"
        results["rc001_step02_derivation_supported_validation"]["errors"].append("STEP-02 still has blockers.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-001 STEP-02 derivation supported status.")
    parser.add_argument("--supported", default="registry/math/rc001_step02_derivation_supported_registry.json")
    parser.add_argument("--decision", default="registry/math/rc001_step02_elevation_decision_registry.json")
    parser.add_argument("--closure", default="registry/math/rc001_derivation_closure_registry.json")
    
    args = parser.parse_args()
    res = validate_rc001_step02_derivation_supported(args.supported, args.decision, args.closure)
    print(json.dumps(res, indent=2))
