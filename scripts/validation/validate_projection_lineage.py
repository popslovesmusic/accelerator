import os
import glob
import json

def validate_projection_lineage():
    print("Validating projection lineage and checking for reification drift...")
    issues_found = False

    # Check for missing core_expression_dependency in major objects
    files_to_check = [
        "registry/math/theorem_dependency_graph.json",
        "registry/math/law_program_registry.json",
        "registry/campaigns/campaign_design_schema.json"
    ]
    for filepath in files_to_check:
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # This is a schema check, so it's a bit different
            if "schema_requirements" in data and "core_expression_dependency" not in data["schema_requirements"]:
                print(f"ERROR: Missing 'core_expression_dependency' in schema of {filepath}")
                issues_found = True
            if "required_fields" in data and "core_expression_dependency" not in data["required_fields"]:
                print(f"ERROR: Missing 'core_expression_dependency' in required_fields of {filepath}")
                issues_found = True

    # Check for lexicon terms missing projection_role
    with open('registry/lexicon_canonical.json', 'r', encoding='utf-8') as f:
        lex = json.load(f)
        for item in lex.get('terms', []):
            if 'projection_role' not in item:
                print(f"ERROR: Term '{item.get('term')}' is missing projection_role metadata.")
                issues_found = True

    if issues_found:
        print("Validation FAILED.")
        exit(1)
    else:
        print("Validation PASSED.")

if __name__ == '__main__':
    validate_projection_lineage()
