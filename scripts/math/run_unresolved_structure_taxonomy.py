import json
import os
from datetime import datetime

def run_taxonomy():
    """
    Runner for Unresolved Structure Taxonomy.
    Classifies initial unresolved targets and identifies resolution paths.
    """
    registry_path = "registry/math/unresolved_structure_taxonomy_registry.json"
    result_path = "validation/results/unresolved_structure_taxonomy_result.json"
    
    if not os.path.exists(registry_path):
        return {"status": "fail", "reason": "taxonomy registry missing"}

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry_data = json.load(f)

    report = {
        "taxonomy_summary_id": "URS-TAX-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "classifications": [],
        "governance": registry_data["governance"]
    }

    # Map initial targets to taxonomy classes and resolution outputs
    target_mapping = {
        "URS-T001": ("URS-SCOPE-LIMITED", "RES-BOUNDED"),
        "URS-T002": ("URS-INCOMPLETE", "RES-REPAIRABLE"),
        "URS-T003": ("URS-SYMBOLIC", "RES-OPERATIONALIZABLE"),
        "URS-T004": ("URS-DECEPTIVE", "RES-STRESS-TESTABLE"),
        "URS-T005": ("URS-IRREDUCIBLE", "RES-PERMANENTLY-OPEN"),
        "URS-T006": ("URS-METASTABLE", "RES-STRESS-TESTABLE"),
        "URS-T007": ("URS-QUARANTINED", "RES-QUARANTINE-REQUIRED")
    }

    for target in registry_data["initial_unresolved_targets"]:
        tid = target["target_id"]
        tax_class, res_output = target_mapping.get(tid, ("URS-INCOMPLETE", "RES-REPAIRABLE"))
        
        classification = {
            "target_id": tid,
            "name": target["name"],
            "taxonomy_class": tax_class,
            "resolution_output": res_output,
            "risk": target["risk"]
        }
        report["classifications"].append(classification)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Unresolved structure taxonomy summary saved to {result_path}")
    return report

if __name__ == "__main__":
    run_taxonomy()
