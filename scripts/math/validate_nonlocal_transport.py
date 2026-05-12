import json
import os
import argparse

def validate_nonlocal_transport(transport_reg, closure_reg, failure_reg, op_reg, law_regs):
    results = {
        "nonlocal_transport_validation": {
            "status": "pass",
            "transport_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(transport_reg, 'r') as f: transport_data = json.load(f)
        with open(closure_reg, 'r') as f: closure_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["nonlocal_transport_validation"]["status"] = "fail"
        results["nonlocal_transport_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    transport_classes = [tc["class"] for tc in transport_data.get("transport_classes", [])]
    closure_classes = [cc["class"] for cc in closure_data.get("closure_classes", [])]
    reconstruction_implications = ["invertible", "partially_reconstructable", "ambiguous", "non_invertible", "undefined"]
    stability_implications = ["stabilizing", "destabilizing", "neutral", "conditional", "undefined"]
    convergence_implications = ["supports_convergence", "permits_divergence", "requires_bound", "undefined"]

    # Validate Transport Entries
    for entry in transport_data.get("transport_entries", []):
        results["nonlocal_transport_validation"]["transport_count"] += 1
        
        # Check target operator
        if entry.get("target_operator") not in op_symbols:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown operator: {entry['target_operator']}")
        
        # Check target law
        if entry.get("target_law") not in law_ids:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown law: {entry['target_law']}")

        # Check transport class
        if entry.get("transport_class") not in transport_classes:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown transport class: {entry['transport_class']}")

        # Check closure class
        if entry.get("closure_class") not in closure_classes:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown closure class: {entry['closure_class']}")

        # Check implications
        if entry.get("reconstruction_implication") not in reconstruction_implications:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown reconstruction implication: {entry['reconstruction_implication']}")
        
        if entry.get("stability_implication") not in stability_implications:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown stability implication: {entry['stability_implication']}")

        if entry.get("convergence_implication") not in convergence_implications:
             results["nonlocal_transport_validation"]["status"] = "warning"
             results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown convergence implication: {entry['convergence_implication']}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["nonlocal_transport_validation"]["status"] = "warning"
                results["nonlocal_transport_validation"]["warnings"].append(f"Transport entry {entry['entry_id']} references unknown failure mode: {fm}")

        results["nonlocal_transport_validation"]["open_questions"].extend(entry.get("open_questions", []))

    results["nonlocal_transport_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate non-local transport registries.")
    parser.add_argument("--transport", default="registry/math/nonlocal_transport_registry.json")
    parser.add_argument("--closure", default="registry/math/transport_closure_registry.json")
    parser.add_argument("--failures", default="registry/math/nonlocal_transport_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_nonlocal_transport(args.transport, args.closure, args.failures, args.operators, args.laws)
    print(json.dumps(res, indent=2))
