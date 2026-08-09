import json
import os
import argparse

def validate_rc001_derivation_closure(rc001_reg, evidence_reg, chain_reg):
    results = {
        "rc001_derivation_closure_validation": {
            "status": "pass",
            "step_count": 0,
            "evidence_link_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(rc001_reg, 'r') as f: rc001_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
    except Exception as e:
        results["rc001_derivation_closure_validation"]["status"] = "fail"
        results["rc001_derivation_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Verify target chain
    if rc001_data["meta"]["target_chain"] != "RC-001":
        results["rc001_derivation_closure_validation"]["status"] = "fail"
        results["rc001_derivation_closure_validation"]["errors"].append(f"Registry target mismatch: expected RC-001, found {rc001_data['meta']['target_chain']}")

    # Check steps against canonical chain
    chain_entry = next((c for c in chain_data.get("entries", []) if c["entry_id"] == "RC-001"), None)
    if not chain_entry:
         results["rc001_derivation_closure_validation"]["status"] = "fail"
         results["rc001_derivation_closure_validation"]["errors"].append("Chain RC-001 not found in canonical registry.")
         return results

    canonical_steps = [s["step_id"] for s in chain_entry.get("reduction_steps", [])]
    for step in rc001_data.get("step_resolutions", []):
        results["rc001_derivation_closure_validation"]["step_count"] += 1
        if step["step_id"] not in canonical_steps:
             results["rc001_derivation_closure_validation"]["status"] = "warning"
             results["rc001_derivation_closure_validation"]["warnings"].append(f"Step {step['step_id']} not found in canonical RC-001.")
        
        results["rc001_derivation_closure_validation"]["evidence_link_count"] += len(step.get("evidence_links", []))

    # Safety check: closure status
    if rc001_data["closure_criteria_check"]["ready_for_closure"]:
         # Check if GAP-001 is still present in steps
         has_blockers = any(step.get("blockers") for step in rc001_data["step_resolutions"])
         if has_blockers:
              results["rc001_derivation_closure_validation"]["status"] = "fail"
              results["rc001_derivation_closure_validation"]["errors"].append("RC-001 marked ready_for_closure while blockers still active.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-001 derivation closure attempt.")
    parser.add_argument("--rc001", default="registry/math/rc001_derivation_closure_registry.json")
    parser.add_argument("--evidence", default="registry/math/rc001_step_evidence_registry.json")
    parser.add_argument("--chains", default="registry/math/reduction_chain_registry.json")
    
    args = parser.parse_args()
    res = validate_rc001_derivation_closure(args.rc001, args.evidence, args.chains)
    print(json.dumps(res, indent=2))
