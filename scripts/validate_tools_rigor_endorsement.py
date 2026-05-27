import json
import sys
import os

def main():
    registry_path = 'registry/tools_rigor_endorsement_registry.json'
    
    if not os.path.exists(registry_path):
        print(f"ERROR: Missing {registry_path}")
        sys.exit(1)
        
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    records = data.get('records', [])
    
    if len(records) != 59:
        print(f"ERROR: Expected exactly 59 registered tools. Found {len(records)}.")
        sys.exit(1)
        
    level_map = {'C0': 0, 'C1': 1, 'C2': 2, 'C3': 3, 'C4': 4, 'C5': 5, 'C6': 6}
    
    errors = []
    for tool in records:
        tid = tool.get('tool_id')
        lvl = tool.get('current_rigor_endorsement_level', 'C0')
        lock = tool.get('lock_state')
        evidence = tool.get('test_result_files', [])
        falsi = tool.get('falsification_vectors_tested', [])
        
        if level_map.get(lvl, 0) < 4:
            errors.append(f"Tool {tid} has endorsement level {lvl} (< C4).")
            
        if lock != 'locked':
            errors.append(f"Tool {tid} is not locked (current state: {lock}).")
            
        if not evidence:
            errors.append(f"Tool {tid} is missing test_result_files.")
        else:
            for ev_file in evidence:
                if os.path.exists(ev_file):
                    with open(ev_file, 'r', encoding='utf-8') as ef:
                        content = ev_file + ef.read()
                        if 'certification' in content.lower():
                            errors.append(f"Tool {tid} evidence {ev_file} uses deprecated 'certification' language.")
            
        if not falsi:
            errors.append(f"Tool {tid} is missing falsification_vectors_tested.")
            
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
        
    print("VALIDATION PASSED: All 59 tools meet the C4 rigor endorsement lock requirements.")

if __name__ == '__main__':
    main()
