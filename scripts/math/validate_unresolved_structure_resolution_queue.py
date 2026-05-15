import json
import os
from datetime import datetime

def validate_resolution_queue():
    registry_path = "registry/math/unresolved_structure_resolution_queue_registry.json"
    doc_path = "docs/math/unresolved_structure_resolution_queue.md"
    result_path = "validation/results/unresolved_structure_resolution_queue_result.json"
    val_out_path = "validation/results/unresolved_structure_resolution_queue_validation_result.json"
    
    report = {
        "validation_id": "VAL-URS-RES-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "entries_routed": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. Existence Checks
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing resolution queue registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing resolution queue documentation")

    # 2. Result Verification
    if not os.path.exists(result_path):
         report["status"] = "warning"
         report["governance_violations"].append("resolution queue results not yet generated")
    else:
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Governance checks
            if data["governance"]["theorem_status"] != "NOT_PROVEN":
                 report["status"] = "fail"
                 report["governance_violations"].append("forbidden theorem status promotion in results")

            # Routing Enforcement Checks
            for entry in data["routed_entries"]:
                tax_class = entry["taxonomy_class"]
                track = entry["assigned_track"]
                
                # Rule: Scope-limited must go to bounded preservation
                if tax_class == "URS-SCOPE-LIMITED" and track != "URS-TRACK-BOUNDED":
                     report["status"] = "fail"
                     report["governance_violations"].append(f"routing breach for {entry['target_id']}: scope-limited improperly routed to {track}")
                
                # Rule: Irreducible must go to irreducible boundary
                if tax_class == "URS-IRREDUCIBLE" and track != "URS-TRACK-IRREDUCIBLE":
                     report["status"] = "fail"
                     report["governance_violations"].append(f"routing breach for {entry['target_id']}: irreducible improperly routed to {track}")

                report["entries_routed"] += 1

    # 3. Documentation Verification
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        mandatory_terms = ["not_proven", "strictly_local_restricted_domain", "routing tracks", "core principle"]
        for term in mandatory_terms:
            if term not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory governance term '{term}' in documentation")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_resolution_queue()
    print(json.dumps(res, indent=2))
