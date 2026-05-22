import os
import glob
import json
import sys

def validate_core_expression():
    results = {
        "core_expression_validation": {
            "status": "pass",
            "warnings": [],
            "errors": [],
            "checks": []
        }
    }
    
    required_strings = [
        "(ℰ≠0) ⇔_x δ(ℰ>0)",
        "recursive aspect-binding",
        "derived structure doctrine",
        "core_expression_dependency",
        "organization-mode"
    ]
    blocked_readings = [
        "ordinary equation",
        "ordinary biconditional",
        "static identity claim",
        "physics master equation",
        "dualistic relation between two substances",
        "operator-first ontology",
        "geometry-first ontology",
        "topology-first ontology"
    ]
    
    excluded_files = [
        'guardrails',
        'canonical_statement',
        'GEMINI.md',
        'AGENTS.md',
        'core_expression_orientation_note.md',
        'codex_master_index.md',
        'codex_volume_1_foundations.md',
        'core_meaning_preservation_checklist.json'
    ]

    docs_to_check = glob.glob("docs/**/*.md", recursive=True) + glob.glob("registry/**/*.json", recursive=True)
    
    # Track required string presence
    found_required = {s: False for s in required_strings}
    
    for filepath in docs_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                content_lower = content.lower()
                
            # Check for required strings (case-insensitive)
            for s in required_strings:
                if s.lower() in content_lower:
                    found_required[s] = True

            # Check for blocked readings
            for blocked in blocked_readings:
                # Exclude the string "forbidden_reading": "Logical equivalence or ordinary biconditional."
                safe_content = content.replace('"forbidden_reading": "Logical equivalence or ordinary biconditional."', '')
                
                is_excluded = any(ex in filepath for ex in excluded_files)
                
                if blocked in safe_content and not is_excluded:
                    results["core_expression_validation"]["errors"].append(f"Blocked reading '{blocked}' found in {filepath}")
                    results["core_expression_validation"]["status"] = "fail"
        except Exception as e:
            results["core_expression_validation"]["warnings"].append(f"Error reading {filepath}: {e}")

    for s, found in found_required.items():
        if not found:
            results["core_expression_validation"]["errors"].append(f"Required string '{s}' not found in any foundational document.")
            results["core_expression_validation"]["status"] = "fail"
        else:
            results["core_expression_validation"]["checks"].append(f"Required string '{s}' presence verified.")

    return results

if __name__ == '__main__':
    res = validate_core_expression()
    print(json.dumps(res, indent=2))
    if res["core_expression_validation"]["status"] == "fail":
        sys.exit(1)
    else:
        sys.exit(0)
