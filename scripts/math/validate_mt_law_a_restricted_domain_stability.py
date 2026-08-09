import json
import os
from datetime import datetime

def validate_mt_law_a_stability_consolidation():
    results = {
        "mt_law_a_restricted_domain_stability_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_restricted_domain_stability_validation"]
    
    registry_path = "registry/math/mt_law_a_restricted_domain_stability_registry.json"
    doc_path = "docs/math/mt_law_a_restricted_domain_stability_consolidation.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A stability registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check for all 4 stability regions
                regions = data.get("stability_regions", [])
                if len(regions) < 4:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient stability regions: {len(regions)}/4")
                
                # Check required fields
                required_fields = ["stability_region_id", "required_conditions", "linked_excluded_domains", "linked_reentry_conditions", "linked_counterexamples", "known_instabilities", "scope_limitations", "status"]
                for r in regions:
                    for field in required_fields:
                        if field not in r:
                            report["errors"].append(f"Stability region {r.get('stability_region_id')} missing field: {field}")

                # Verify instabilities are preserved
                if len(data.get("preserved_instabilities", [])) < 6:
                    report["errors"].append("Insufficient preserved instabilities in registry.")

                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("proof_status") != "TS3_stability_consolidation_only":
                    report["status"] = "fail"
                    report["errors"].append(f"Incorrect proof status: {gov.get('proof_status')}. Must be 'TS3_stability_consolidation_only'.")

                report["checks"].append("MT-LAW-A stability consolidation registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A stability consolidation document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted stability region summary", "validated stability conditions",
                "excluded domain boundaries", "reentry boundary summary", "counterexample pressure summary",
                "cross-mechanism consistency limits", "failure boundary preservation",
                "known divergence hotspots", "open proof obligations",
                "non-universality reinforcement", "governance status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for region IDs in document
            for i in range(1, 5):
                if f"sr-a00{i}" not in content:
                    report["errors"].append(f"Stability Region SR-A00{i} missing in document.")

            # Status footer check
            if "ts3_stability_consolidation_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A stability consolidation document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_restricted_domain_stability_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "stability_regions_consolidated": len(regions) if 'regions' in locals() else 0,
        "instabilities_preserved": True if len(data.get("preserved_instabilities", [])) >= 6 else False,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_stability_consolidation()
    print(json.dumps(res, indent=2))
