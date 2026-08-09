import sys
import json
import glob
import os

def validate_ontology():
    print("Validating for Process-First Ontological Consistency...")
    
    with open('registry/governance/non_reification_rules.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)['rules']

    docs_to_check = glob.glob("docs/math/**/*.md", recursive=True) + glob.glob("docs/reviewer_notes/**/*.md", recursive=True)

    # Exclude the documents that are defining the standards
    exclusion_list = [
        "docs/math/projection_vs_primitive_standard.md",
        "docs/math/identity_as_process_continuity.md",
        "docs/math/observer_as_local_projection.md",
        "docs/math/operator_non_substance_clarification.md",
        "docs/governance/hidden_substance_drift_taxonomy.md",
        "docs/math/geometry_as_process_projection.md",
        "docs/math/topology_as_accessibility_projection.md"
    ]
    
    docs_to_check = [os.path.normpath(p) for p in docs_to_check]
    exclusion_list = [os.path.normpath(p) for p in exclusion_list]
    docs_to_check = [p for p in docs_to_check if p not in exclusion_list]

    issues_found = False

    for filepath in docs_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().lower() # case-insensitive check
            
            for rule in rules:
                for phrase in rule['forbidden_phrases']:
                    if phrase in content:
                        print(f"ONTOLOGY VIOLATION ({rule['rule_id']}): Forbidden phrase '{phrase}' found in {filepath}")
                        issues_found = True
        except Exception:
            pass # Ignore files that can't be read

    if issues_found:
        print("Ontological Consistency Validation FAILED.")
        sys.exit(1)
    else:
        print("Ontological Consistency Validation PASSED.")

if __name__ == '__main__':
    validate_ontology()
