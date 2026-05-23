import os
import json
from datetime import datetime

def validate_audit():
    audit_registry_path = "registry/math/mt_law_a_foundations_dependency_audit_registry.json"
    audit_document_path = "docs/math/mt_law_a_foundations_dependency_audit.md"
    result_path = "validation/results/mt_law_a_foundations_dependency_audit_result.json"

    report = {
        "audit_id": "AUDIT-MT-LAW-A-FOUNDATIONS-001",
        "validation_status": "pass",
        "law_dependencies_verified": 0,
        "meta_dependencies_verified": 0,
        "mt_law_a_patch_chain_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }

    if not os.path.exists(audit_registry_path):
        report["validation_status"] = "fail"
        report["governance_violations"].append("missing foundations audit registry")
        return report

    if not os.path.exists(audit_document_path):
        report["validation_status"] = "fail"
        report["governance_violations"].append("missing foundations audit document")

    with open(audit_registry_path, 'r') as f:
        registry = json.load(f)

    # Validate Dependencies (Theorems/Lemmas)
    deps = registry["dependencies_audited"]["law_dependencies"]
    math_registry_path = "registry/math_registry.json"
    if not os.path.exists(math_registry_path):
        report["validation_status"] = "fail"
        report["governance_violations"].append("missing math registry (SSOT)")
        return report
        
    with open(math_registry_path, 'r', encoding='utf-8') as mf:
        math_reg = json.load(mf)
    
    all_math_items = math_reg.get('theorems', []) + math_reg.get('lemmas', []) + math_reg.get('proofs', [])
    registered_ids = [item['item_id'] for item in all_math_items]

    for dep in deps:
        if dep not in registered_ids:
             report["governance_violations"].append(f"missing registry entry for {dep}")
        else:
             report["law_dependencies_verified"] += 1

    # Validate Meta Dependencies
    meta_deps = registry["dependencies_audited"]["meta_dependencies"]
    for meta in meta_deps:
        found_reg = any(f.startswith(meta.lower()) and f.endswith("_registry.json") for f in os.listdir("registry/math/"))
        if not found_reg:
            report["governance_violations"].append(f"missing registry for {meta}")
        else:
            report["meta_dependencies_verified"] += 1

    # Validate MT-LAW-A Patch Chain
    patch_chain = registry["dependencies_audited"]["mt_law_a_patch_chain"]
    patch_mapping = {
        "MT-LAW-A020": "RA-MT-LAW-A-001",
        "MT-LAW-A021": "GATE-MT-LAW-A-TS4-001",
        "MT-LAW-A022": "REV-MT-LAW-A-TS4-001",
        "MT-LAW-A023": "REC-MT-LAW-A-TS4-001",
        "MT-LAW-A024": "HD-MT-LAW-A-TS4-001"
    }

    for patch in patch_chain:
        # Check for presence in registry/math/ by searching file content for ID
        found_patch = False
        target_id = patch_mapping.get(patch, patch)
        for filename in os.listdir("registry/math/"):
            if filename.endswith(".json"):
                with open(os.path.join("registry/math/", filename), 'r') as rf:
                    try:
                        data = json.load(rf)
                        if data.get("id") == target_id or \
                           data.get("audit_id") == target_id or \
                           data.get("hardening_id") == target_id or \
                           data.get("gate_id") == target_id or \
                           data.get("review_id") == target_id or \
                           data.get("reconciliation_id") == target_id:
                            found_patch = True
                            break
                    except:
                        continue
        if not found_patch:
            report["governance_violations"].append(f"missing registry entry for patch {patch} (target_id: {target_id})")
        else:
            report["mt_law_a_patch_chain_verified"] += 1

    # Check for forbidden outcomes
    forbidden_outcomes = [
        "THEOREM_PROVEN",
        "TS5_READY",
        "GLOBAL_CLOSURE_COMPLETE",
        "COUNTEREXAMPLES_DISCHARGED",
        "PHYSICS_MAPPING_CONFIRMED"
    ]
    for outcome in forbidden_outcomes:
        with open(audit_document_path, 'r') as f:
            if outcome in f.read():
                report["validation_status"] = "fail"
                report["governance_violations"].append(f"forbidden outcome '{outcome}' detected in document")

    # Check for mandatory open blockers
    mandatory_blockers = registry["mandatory_open_blockers_preserved"]
    with open(audit_document_path, 'r') as f:
        doc_content = f.read()
        for blocker in mandatory_blockers:
            if blocker not in doc_content:
                report["validation_status"] = "fail"
                report["governance_violations"].append(f"mandatory open blocker '{blocker}' missing from document")

    # Final result
    if report["governance_violations"]:
        report["validation_status"] = "fail"
    else:
        report["validation_status"] = "pass"

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report

if __name__ == "__main__":
    result = validate_audit()
    print(json.dumps(result, indent=2))
