import sys
import json

def check_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open('registry/governance/core_meaning_preservation_checklist.json', 'r', encoding='utf-8') as f:
        checklist = json.load(f)

    issues_found = False
    
    print(f"Running Meaning Preservation Gate on {filepath}...")
    
    # CHECK-CORE-001
    if checklist['checks'][0]['pass_condition'] == 'boolean' and checklist['checks'][0]['question'] and "(ℰ≠0) ⇔_R δ(ℰ>0)" not in content:
        print("FAIL (CHECK-CORE-001): Core expression is not stated explicitly.")
        issues_found = True
        
    # CHECK-CORE-002
    if checklist['checks'][1]['pass_condition'] == 'boolean' and "recursive aspect-binding" not in content and "inseparable aspect" not in content:
        print("FAIL (CHECK-CORE-002): Does not clarify the meaning of ⇔_R.")
        issues_found = True

    # CHECK-CORE-003
    if checklist['checks'][2]['pass_condition'] == 'boolean' and ("primitive substrate" in content or "pre-existing topology" in content):
        print("FAIL (CHECK-CORE-003): Describes geometry or topology as primitive.")
        issues_found = True
        
    # CHECK-CORE-004
    if checklist['checks'][3]['pass_condition'] == 'boolean' and "stabilized process projection" not in content and "derived projection" not in content:
        print("FAIL (CHECK-CORE-004): Does not describe derived structures as projections.")
        issues_found = True
        
    # CHECK-CORE-005
    with open('docs/reviewer_notes/core_misinterpretation_taxonomy.md', 'r', encoding='utf-8') as f:
        taxonomy = f.read() # Not elegant but works for this
    
    # This is a bit of a hack
    # In a real system you'd parse the taxonomy doc properly
    blocked_readings = [
        "topology-first", "equation-first", "physics-unification-first", "simulation-first", "dualism"
    ]
    for reading in blocked_readings:
        if reading in content:
            print(f"FAIL (CHECK-CORE-005): Contains blocked reading '{reading}'.")
            issues_found = True
            
    return not issues_found

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not check_document(filepath):
            print(f"Meaning Preservation Gate FAILED for {filepath}.")
            sys.exit(1)
        else:
            print(f"Meaning Preservation Gate PASSED for {filepath}.")
    else:
        print("Usage: python validate_core_meaning_preservation.py <path_to_document>")

