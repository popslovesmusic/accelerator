import json
import os
import argparse

def validate_transition_flux_convergence(convergence_reg, failure_reg, law_regs, dsr_reg):
    results = {
        "transition_flux_convergence_validation": {
            "status": "pass",
            "entry_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(convergence_reg, 'r') as f: conv_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(dsr_reg, 'r') as f: dsr_data = json.load(f)
        
        law_ids = []
        for lfile in law_regs:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])
    except Exception as e:
        results["transition_flux_convergence_validation"]["status"] = "fail"
        results["transition_flux_convergence_validation"]["warnings"].append(f"Load error: {e}")
        return results

    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    dsr_ids = [r["selection_id"] for r in dsr_data.get("selection_rules", [])]
    conv_classes = conv_data.get("convergence_classes", [])

    # Validate Entries
    for entry in conv_data.get("convergence_entries", []):
        results["transition_flux_convergence_validation"]["entry_count"] += 1
        
        # Check target law
        if entry.get("target_law") not in law_ids:
             results["transition_flux_convergence_validation"]["status"] = "warning"
             results["transition_flux_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown law: {entry['target_law']}")
        
        # Check convergence class
        if entry.get("convergence_class") not in conv_classes:
             results["transition_flux_convergence_validation"]["status"] = "warning"
             results["transition_flux_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown class: {entry['convergence_class']}")

        # Check selection rule dependencies
        for dsr in entry.get("selection_rule_dependencies", []):
            if dsr not in dsr_ids:
                results["transition_flux_convergence_validation"]["status"] = "warning"
                results["transition_flux_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown selection rule: {dsr}")
        
        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["transition_flux_convergence_validation"]["status"] = "warning"
                results["transition_flux_convergence_validation"]["warnings"].append(f"Convergence entry {entry['entry_id']} references unknown failure mode: {fm}")

        results["transition_flux_convergence_validation"]["open_questions"].extend(entry.get("open_questions", []))

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate transition_flux convergence registries.")
    parser.add_argument("--convergence", default="registry/math/transition_flux_convergence_registry.json")
    parser.add_argument("--failures", default="registry/math/convergence_failure_mode_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    parser.add_argument("--dsr", default="registry/math/delta_selection_registry.json")
    
    args = parser.parse_args()
    res = validate_transition_flux_convergence(args.convergence, args.failures, args.laws, args.dsr)
    print(json.dumps(res, indent=2))
