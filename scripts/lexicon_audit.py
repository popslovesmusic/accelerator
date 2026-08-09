import json
import os

def audit_lexicon():
    report = {
        "timestamp": "2026-05-08T02:40:00Z",
        "results": [],
        "errors": [],
        "warnings": []
    }
    
    try:
        with open("registry/lexicon_canonical.json", "r", encoding="utf-8") as f:
            canonical = json.load(f)
        with open("registry/lexicon_alias_map.json", "r", encoding="utf-8") as f:
            alias_map = json.load(f)
        with open("registry/lexicon_gap_queue.json", "r", encoding="utf-8") as f:
            gap_queue = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load registries: {str(e)}"}

    canonical_terms = {t["term"]: t for t in canonical["terms"]}
    
    # 1. Check alias targets
    missing_targets = []
    for alias, target in alias_map["aliases"].items():
        if target not in canonical_terms:
            missing_targets.append({"alias": alias, "target": target})
    
    if missing_targets:
        report["warnings"].append({
            "check": "alias_targets_exist",
            "status": "failed",
            "details": missing_targets
        })
    else:
        report["results"].append({"check": "alias_targets_exist", "status": "passed"})

    # 2. Check charter compliance for promoted terms
    promoted_buckets = ["canonical_term", "accepted_derived_action", "derived_shorthand", "surface_metaphor"]
    missing_compliance = []
    for t in canonical["terms"]:
        if t["bucket"] in promoted_buckets:
            if "charter_compliance" not in t:
                missing_compliance.append(t["term"])
            elif t["charter_compliance"].get("final_compliance_status") == "provisional":
                report["warnings"].append({
                    "term": t["term"],
                    "issue": "charter_compliance_is_provisional"
                })

    if missing_compliance:
        report["errors"].append({
            "check": "required_charter_compliance",
            "status": "failed",
            "missing_terms": missing_compliance
        })
    else:
        report["results"].append({"check": "required_charter_compliance", "status": "passed"})

    # 3. Check blocked primitives
    blocked_primitives = [
        "attractor", "container", "object", "substance", 
        "location", "space_as_substrate", "time_as_primitive_dimension", "field_as_primitive"
    ]
    landed_blocked = []
    for term in blocked_primitives:
        if term in canonical_terms:
            t = canonical_terms[term]
            # Only allowed as surface_metaphor or derived_shorthand with non-primitive definition
            if t["bucket"] == "canonical_term":
                 landed_blocked.append({"term": term, "bucket": t["bucket"]})
    
    if landed_blocked:
        report["errors"].append({
            "check": "check_blocked_primitives",
            "status": "failed",
            "details": landed_blocked
        })
    else:
        report["results"].append({"check": "check_blocked_primitives", "status": "passed"})

    return report

if __name__ == "__main__":
    report = audit_lexicon()
    print(json.dumps(report, indent=2))
