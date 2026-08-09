import argparse
import sys
import os

ALLOWED_PATHS = [
    "scripts/db/",
    "scripts/audit_current_state.py",
    "scripts/save_report.py",
    "scripts/orientation_status_check.py",
    "scripts/agent_scope_check.py",
    "scripts/build_claim_packet.py",
    "registry/db/",
    "outputs/audits/",
    "outputs/reports/",
    "outputs/maintenance/",
    "AGENTS.md"
]

FORBIDDEN_PATHS = [
    "registry/lexicon_canonical.json",
    "registry/lexicon_alias_map.json",
    "registry/lexicon_gap_queue.json",
    "registry/lexicon_validation_registry.json",
    "registry/claim_registry.json",
    "registry/compliance_charter_v2_3.json",
    "tools/",
    "docs/",
    "configs/canonical/"
]

def is_path_allowed(path):
    path = path.replace('\\', '/')
    
    # Check forbidden first
    for forbidden in FORBIDDEN_PATHS:
        if path.startswith(forbidden):
            return False, f"Path '{path}' is explicitly forbidden (SSOT or core logic)."
    
    # Check allowed
    for allowed in ALLOWED_PATHS:
        if path.startswith(allowed):
            return True, None
    
    # Special case for AGENTS.md (direct match)
    if path == "AGENTS.md":
        return True, None
        
    return False, f"Path '{path}' is not in the allowed list for this patch."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if an agent edit is within allowed scope.")
    parser.add_argument("paths", nargs="+", help="Paths to check.")
    args = parser.parse_args()
    
    all_ok = True
    for p in args.paths:
        ok, msg = is_path_allowed(p)
        if not ok:
            print(f"BLOCK: {msg}")
            all_ok = False
        else:
            print(f"ALLOW: {p}")
            
    if not all_ok:
        sys.exit(1)
    else:
        print("SCOPE CHECK: PASS")
