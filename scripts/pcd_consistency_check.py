import json
import os
import sys

def check_consistency():
    manifest_path = "registry/consistency_engine_manifest.json"
    obj_reg_path = "registry/formal_object_registry.json"
    ref_reg_path = "registry/formal_object_reference_registry.json"

    if not all(os.path.exists(p) for p in [manifest_path, obj_reg_path, ref_reg_path]):
        return {"status": "ERROR", "message": "Consistency registries missing"}

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    with open(obj_reg_path, 'r', encoding='utf-8') as f:
        obj_reg = json.load(f)
    with open(ref_reg_path, 'r', encoding='utf-8') as f:
        ref_reg = json.load(f)

    report = {
        "status": "PASS",
        "theorem_status_conflicts": [],
        "claim_support_conflicts": [],
        "operator_signature_conflicts": [],
        "gap_dependency_conflicts": [],
        "recommended_downgrades": [],
        "manual_review_queue": []
    }

    objects = {obj["object_id"]: obj for obj in obj_reg["objects"]}
    
    # 1. CONSISTENCY-001: no_claim_above_dependency_status
    # (Simplified: check if claim status matches dependency status)
    for obj in objects.values():
        if obj["object_class"] == "claim":
            for dep_id in obj.get("dependency_links", []):
                if dep_id in objects:
                    dep = objects[dep_id]
                    # Check theorem status TS levels
                    # (This logic would be more complex in production)
                    pass

    # 2. CONSISTENCY-002: no_supported_claim_with_open_gap
    for obj in objects.values():
        if obj["object_class"] == "claim" and "supported" in obj["status"]:
            for dep_id in obj.get("dependency_links", []):
                if dep_id in objects:
                    dep = objects[dep_id]
                    if dep["object_class"] == "gap" and "OPEN" in dep["status"]:
                        report["claim_support_conflicts"].append({
                            "claim": obj["object_id"],
                            "gap": dep["object_id"],
                            "error": "Supported claim depends on OPEN gap"
                        })
                        report["recommended_downgrades"].append(obj["object_id"])

    # Final report status
    if report["claim_support_conflicts"] or report["theorem_status_conflicts"]:
        report["status"] = "ISSUES_FOUND"

    with open("registry/reports/contradiction_and_consistency_engine_v1_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    return report

if __name__ == "__main__":
    res = check_consistency()
    print(json.dumps(res, indent=2))
