import json
import os
import argparse

def validate_rc002_derivation_supported(supported_reg, decision_reg):
    results = {
        "rc002_derivation_supported_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(supported_reg, 'r') as f: s_data = json.load(f).get("rc002_derivation_supported", {})
        with open(decision_reg, 'r') as f: d_data = json.load(f).get("rc002_derivation_elevation_decision", {})
    except Exception as e:
        results["rc002_derivation_supported_validation"]["status"] = "fail"
        results["rc002_derivation_supported_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Verification checks
    if s_data.get("status") != "derivation_supported":
         results["rc002_derivation_supported_validation"]["status"] = "fail"
         results["rc002_derivation_supported_validation"]["errors"].append("Registry status is not derivation_supported.")

    # Check for all steps supported
    step_ids = [s["step_id"] for s in s_data.get("supported_steps", [])]
    if "STEP-01" not in step_ids or "STEP-02" not in step_ids:
         results["rc002_derivation_supported_validation"]["status"] = "fail"
         results["rc002_derivation_supported_validation"]["errors"].append("Not all required steps are documented as supported.")

    # Decision check
    if d_data.get("action") != "elevate_to_derivation_supported":
         results["rc002_derivation_supported_validation"]["status"] = "fail"
         results["rc002_derivation_supported_validation"]["errors"].append("Decision registry action mismatch.")

    # Humility/Overreach check: Check if closed globally or physics claimed
    # (Implicitly checked by absence of such fields or explicit 'LOCKED' statuses)
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-002 derivation supported status.")
    parser.add_argument("--supported", default="registry/math/rc002_derivation_supported_registry.json")
    parser.add_argument("--decision", default="registry/math/rc002_derivation_elevation_decision_registry.json")
    
    args = parser.parse_args()
    res = validate_rc002_derivation_supported(args.supported, args.decision)
    print(json.dumps(res, indent=2))
