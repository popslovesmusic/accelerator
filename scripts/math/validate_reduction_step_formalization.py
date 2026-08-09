import json
import os
import argparse

def validate_reduction_step_formalization(formal_reg, chain_reg, gap_reg):
    results = {
        "reduction_step_formalization_validation": {
            "status": "pass",
            "entry_count": 0,
            "formalized_count": 0,
            "symbolic_supported_count": 0,
            "scaffolded_count": 0,
            "nonformal_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(formal_reg, 'r') as f: formal_data = json.load(f)
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
        with open(gap_reg, 'r') as f: gap_data = json.load(f)
    except Exception as e:
        results["reduction_step_formalization_validation"]["status"] = "fail"
        results["reduction_step_formalization_validation"]["errors"].append(f"Load error: {e}")
        return results

    status_classes = formal_data.get("reduction_step_status_classes", [])
    chain_ids = [c["entry_id"] for c in chain_data.get("entries", [])]
    
    # Validate Entries
    for entry in formal_data.get("formalization_entries", []):
        results["reduction_step_formalization_validation"]["entry_count"] += 1
        
        # Check chain_id
        if entry.get("chain_id") not in chain_ids:
             results["reduction_step_formalization_validation"]["status"] = "warning"
             results["reduction_step_formalization_validation"]["warnings"].append(f"Formalization entry references unknown chain: {entry['chain_id']}")
        
        # Check status
        status = entry.get("status")
        if status not in status_classes:
             results["reduction_step_formalization_validation"]["status"] = "warning"
             results["reduction_step_formalization_validation"]["warnings"].append(f"Entry {entry['chain_id']}/{entry['step_id']} has unknown status: {status}")

        if status == "formal": results["reduction_step_formalization_validation"]["formalized_count"] += 1
        elif status == "symbolic_supported": results["reduction_step_formalization_validation"]["symbolic_supported_count"] += 1
        elif status == "scaffolded": results["reduction_step_formalization_validation"]["scaffolded_count"] += 1
        elif status == "nonformal": results["reduction_step_formalization_validation"]["nonformal_count"] += 1

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate reduction-step formalization registry.")
    parser.add_argument("--formal", default="registry/math/reduction_step_formalization_registry.json")
    parser.add_argument("--chains", default="registry/math/reduction_chain_registry.json")
    parser.add_argument("--gaps", default="registry/math/reduction_gap_registry.json")
    
    args = parser.parse_args()
    res = validate_reduction_step_formalization(args.formal, args.chains, args.gaps)
    print(json.dumps(res, indent=2))
