import json
import os
import argparse

def validate_symbolic_derivation_closure(closure_reg, evidence_reg, failure_reg, chain_reg):
    results = {
        "symbolic_derivation_closure_validation": {
            "status": "pass",
            "closure_entry_count": 0,
            "evidence_entry_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
    except Exception as e:
        results["symbolic_derivation_closure_validation"]["status"] = "fail"
        results["symbolic_derivation_closure_validation"]["errors"].append(f"Load error: {e}")
        return results

    chain_ids = [c["entry_id"] for c in chain_data.get("entries", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    closure_classes = [c["class"] for c in closure_data.get("derivation_closure_classes", [])]

    # Validate Closure Entries
    for entry in closure_data.get("closure_entries", []):
        results["symbolic_derivation_closure_validation"]["closure_entry_count"] += 1
        if entry.get("target_chain") not in chain_ids:
             results["symbolic_derivation_closure_validation"]["status"] = "warning"
             results["symbolic_derivation_closure_validation"]["warnings"].append(f"Closure entry {entry['entry_id']} references unknown chain: {entry['target_chain']}")
        
        if entry.get("closure_status") not in closure_classes:
             results["symbolic_derivation_closure_validation"]["status"] = "warning"
             results["symbolic_derivation_closure_validation"]["warnings"].append(f"Entry {entry['entry_id']} has unknown status: {entry['closure_status']}")

    # Validate Evidence Entries
    for entry in evidence_data.get("evidence_entries", []):
        results["symbolic_derivation_closure_validation"]["evidence_entry_count"] += 1
        if entry.get("chain_id") not in chain_ids:
             results["symbolic_derivation_closure_validation"]["status"] = "warning"
             results["symbolic_derivation_closure_validation"]["warnings"].append(f"Evidence entry {entry['evidence_id']} references unknown chain: {entry['chain_id']}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate symbolic derivation closure registries.")
    parser.add_argument("--closure", default="registry/math/symbolic_derivation_closure_registry.json")
    parser.add_argument("--evidence", default="registry/math/derivation_step_evidence_registry.json")
    parser.add_argument("--failures", default="registry/math/derivation_closure_failure_modes.json")
    parser.add_argument("--chains", default="registry/math/reduction_chain_registry.json")
    
    args = parser.parse_args()
    res = validate_symbolic_derivation_closure(args.closure, args.evidence, args.failures, args.chains)
    print(json.dumps(res, indent=2))
