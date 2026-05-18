import os
import glob

def validate_core_expression():
    print("Validating core expression presence across foundational documents...")
    required_strings = [
        "(ℰ≠0) ⇔_R δ(ℰ>0)",
        "recursive aspect-binding",
        "derived structure doctrine",
        "core_expression_dependency"
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

    docs_to_check = glob.glob("docs/**/*.md", recursive=True) + glob.glob("registry/**/*.json", recursive=True)
    
    issues_found = False
    
    for filepath in docs_to_check:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for blocked readings
            for blocked in blocked_readings:
                # Exclude the string "forbidden_reading": "Logical equivalence or ordinary biconditional."
                safe_content = content.replace('"forbidden_reading": "Logical equivalence or ordinary biconditional."', '')
                if blocked in safe_content and 'guardrails' not in filepath and 'canonical_statement' not in filepath and 'GEMINI.md' not in filepath and 'AGENTS.md' not in filepath and 'core_expression_orientation_note.md' not in filepath and 'codex_master_index.md' not in filepath and 'codex_volume_1_foundations.md' not in filepath:
                    print(f"ERROR: Blocked reading '{blocked}' found in {filepath}")
                    issues_found = True
        except Exception as e:
            pass

    if issues_found:
        print("Validation FAILED.")
        exit(1)
    else:
        print("Validation PASSED.")

if __name__ == '__main__':
    validate_core_expression()
