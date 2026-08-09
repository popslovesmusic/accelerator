import sys
from pathlib import Path

# Add project root to sys.path
root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import json
import hashlib

def calculate_hash(path):
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception as e:
        return None

def enforce_locks():
    root = Path(".")
    lock_path = root / "registry/math_core_hashes.json"
    
    if not lock_path.exists():
        print("[SKIP] Math core lock missing. Run scripts/governance/authorize_lock_update.py to initialize.")
        return True

    print("[GOVERNANCE] Enforcing Foundational Core Locks...")
    
    with open(lock_path, 'r', encoding='utf-8') as f:
        lock_data = json.load(f)
    
    lock_files = lock_data.get("files", {})
    violations = []

    for rel_path, locked_hash in lock_files.items():
        full_path = root / rel_path
        if not full_path.exists():
            violations.append(f"MISSING: {rel_path}")
            continue
        
        current_hash = calculate_hash(full_path)
        if current_hash != locked_hash:
            violations.append(f"MODIFIED: {rel_path}")

    if violations:
        print("\n[CRITICAL ERROR] Core Lock Violation Detected!")
        print("The following foundational documents have been modified without authorization:")
        for v in violations:
            print(f"  - {v}")
        print("\n[ACTION REQUIRED] Revert these changes or run 'python scripts/governance/authorize_lock_update.py' to authorize.")
        return False

    print("[SUCCESS] Foundational core integrity verified.")
    
    # Run Governance Integrity Locks
    print("[GOVERNANCE] Enforcing Governance Integrity Locks...")
    from scripts.governance.enforce_governance_integrity import check_integrity
    gov_res = check_integrity(root)
    if gov_res["status"] != "success":
        print("\n[CRITICAL ERROR] Governance Integrity Violation Detected!")
        for err in gov_res["errors"]:
            print(f"  - {err}")
        print("\n[ACTION REQUIRED] Modifications to governance assets require approval ledger entries and differential reports.")
        return False
        
    print(f"[SUCCESS] Governance integrity verified. {gov_res['verified_count']} assets verified.")
    return True

if __name__ == "__main__":
    if not enforce_locks():
        sys.exit(1)
