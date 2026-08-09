import sys
import json

def validate_agent_summary(summary_text):
    print("Validating agent summary for core alignment...")
    
    required_phrases = [
        "(ℰ≠0) ⇔_R δ(ℰ>0)",
        "inseparable",
        "recursive process"
    ]
    
    blocked_phrases = [
        "topology-first",
        "geometry-first",
        "simulation-first",
        "physics-first"
    ]

    issues_found = False
    
    for phrase in required_phrases:
        if phrase not in summary_text:
            print(f"ERROR: Summary is missing required phrase: '{phrase}'")
            issues_found = True
            
    for phrase in blocked_phrases:
        if phrase in summary_text:
            print(f"ERROR: Summary contains blocked phrase: '{phrase}'")
            issues_found = True
            
    if issues_found:
        print("Agent summary validation FAILED.")
        return False
    else:
        print("Agent summary validation PASSED.")
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        with open(filepath, 'r', encoding='utf-8') as f:
            summary = f.read()
            if not validate_agent_summary(summary):
                sys.exit(1)
    else:
        print("Usage: python validate_agent_summary_core_alignment.py <path_to_summary_file>")

