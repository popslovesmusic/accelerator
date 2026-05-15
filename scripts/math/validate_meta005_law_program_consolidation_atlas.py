import json
import os

def validate_meta005():
    results = {
        "meta005_law_program_consolidation_atlas_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["meta005_law_program_consolidation_atlas_validation"]
    
    registry_path = "registry/math/meta005_law_program_consolidation_atlas_registry.json"
    doc_path = "docs/math/law_program_consolidation_atlas.md"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("META-005 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check law count
                scope = data.get("scope", {})
                if scope.get("total_laws") != 34:
                    report["status"] = "fail"
                    report["errors"].append(f"Incorrect law count in registry: {scope.get('total_laws')}/34")
                
                # Check modules
                modules = data.get("functional_modules", {})
                if len(modules) < 6:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient functional modules: {len(modules)}/6")
                
                # Check governance
                gov = data.get("governance", {})
                if not gov.get("pause_new_law_expansion"):
                    report["status"] = "fail"
                    report["errors"].append("Governance failed to pause new law expansion.")
                
                report["checks"].append("META-005 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Atlas document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("META-005 atlas document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "executive summary", "functional modules", "dependency graph summary",
                "strongest law clusters", "weakest law clusters",
                "candidate theorem targets", "simulation targets", "risks",
                "next-phase roadmap"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from atlas document.")
            
            # Check for LAW-001 through LAW-034
            for i in range(1, 35):
                law_str = f"law-{i:03d}"
                if law_str not in content.replace("_", "-"):
                    report["status"] = "warning"
                    report["warnings"].append(f"Law {law_str} potentially missing or misformatted in atlas.")

        report["checks"].append("META-005 atlas document presence and content scanned.")

    output_path = "outputs/audits/meta005_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_meta005()
    print(json.dumps(res, indent=2))
