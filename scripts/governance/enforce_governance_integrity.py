import json
import hashlib
from pathlib import Path
import glob
import sys
import argparse
from datetime import datetime

PROTECTED_PATTERNS = [
    "GEMINI.md",
    "AGENTS.md",
    "registry/compliance_charter_*.json",
    "registry/tools_rigor_endorsement_registry.json",
    "registry/claim_gate_registry.json",
    "registry/tool_manifest.json",
    "registry/tool_index.json",
    "docs/governance/*"
]

def calculate_hash(path):
    try:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()
    except Exception:
        return None

def get_protected_files(root):
    files = []
    for pattern in PROTECTED_PATTERNS:
        pattern_str = str(root / pattern).replace("\\", "/")
        for path_str in glob.glob(pattern_str):
            path = Path(path_str)
            if path.is_file():
                rel_path = path.relative_to(root)
                files.append(str(rel_path).replace("\\", "/"))
    return sorted(list(set(files)))

def check_integrity(root=Path(".")):
    hash_reg_path = root / "registry/governance_hash_registry.json"
    ledger_path = root / "registry/governance_change_ledger.json"
    
    if not hash_reg_path.exists():
        return {
            "status": "failed",
            "errors": [f"Governance hash registry missing at {hash_reg_path}. Run with --initialize to create."],
            "warnings": [],
            "verified_count": 0
        }
        
    try:
        with open(hash_reg_path, 'r', encoding='utf-8') as f:
            hash_reg = json.load(f)
    except Exception as e:
        return {
            "status": "failed",
            "errors": [f"Failed to parse governance hash registry: {e}"],
            "warnings": [],
            "verified_count": 0
        }
    
    ledger_entries = []
    if ledger_path.exists():
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                ledger_entries = json.load(f).get("entries", [])
        except Exception as e:
            return {
                "status": "failed",
                "errors": [f"Failed to parse governance change ledger: {e}"],
                "warnings": [],
                "verified_count": 0
            }
            
    protected_files = get_protected_files(root)
    errors = []
    warnings = []
    verified_files = {}
    
    baseline_hashes = hash_reg.get("hashes", {})
    
    for rel_path in protected_files:
        full_path = root / rel_path
        current_hash = calculate_hash(full_path)
        baseline_hash = baseline_hashes.get(rel_path)
        
        if baseline_hash is None:
            # Asset is new or missing in hash registry baseline
            approved = False
            for entry in ledger_entries:
                if rel_path in entry.get("affected_assets", []):
                    diff_report_path = root / entry.get("diff_report", "")
                    if entry.get("patch_id") and entry.get("approval_reference") and diff_report_path.exists():
                        approved = True
                        break
            if approved:
                warnings.append(f"Governance asset addition approved via change ledger: {rel_path}")
            else:
                errors.append(f"New governance asset unregistered in baseline hash registry and lacks approved change ledger entry: {rel_path}")
        elif current_hash != baseline_hash:
            # Asset is modified
            approved = False
            for entry in ledger_entries:
                if rel_path in entry.get("affected_assets", []):
                    diff_report_path = root / entry.get("diff_report", "")
                    if entry.get("patch_id") and entry.get("approval_reference") and diff_report_path.exists():
                        approved = True
                        break
            if approved:
                warnings.append(f"Governance asset modification approved via change ledger: {rel_path}")
            else:
                errors.append(f"Governance asset modified without authorized ledger entry or missing diff report: {rel_path}")
        else:
            verified_files[rel_path] = current_hash
            
    # Also check if any asset in baseline hashes has been deleted
    for rel_path in baseline_hashes.keys():
        full_path = root / rel_path
        if not full_path.exists():
            approved = False
            for entry in ledger_entries:
                if rel_path in entry.get("affected_assets", []):
                    diff_report_path = root / entry.get("diff_report", "")
                    if entry.get("patch_id") and entry.get("approval_reference") and diff_report_path.exists():
                        approved = True
                        break
            if approved:
                warnings.append(f"Governance asset deletion approved via change ledger: {rel_path}")
            else:
                errors.append(f"Governance asset deleted without authorized ledger entry or missing diff report: {rel_path}")
                
    status = "success" if not errors else "failed"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "verified_count": len(verified_files)
    }

def initialize_registry(root=Path(".")):
    protected_files = get_protected_files(root)
    hashes = {}
    for rel_path in protected_files:
        hashes[rel_path] = calculate_hash(root / rel_path)
        
    hash_reg_path = root / "registry/governance_hash_registry.json"
    data = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "patch_id": "GOVERNANCE_INTEGRITY_LOCK_001"
        },
        "hashes": hashes
    }
    
    hash_reg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(hash_reg_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Initialized governance hash registry with {len(hashes)} assets at {hash_reg_path}")

def main():
    parser = argparse.ArgumentParser(description="Governance Integrity lock validator")
    parser.add_argument("--initialize", action="store_true", help="Initialize hash registry from current asset states")
    parser.add_argument("--root", default=".", help="Root directory path")
    args = parser.parse_args()
    
    root = Path(args.root)
    
    if args.initialize:
        initialize_registry(root)
        sys.exit(0)
        
    res = check_integrity(root)
    if res["status"] == "failed":
        print("\n[CRITICAL ERROR] Governance Integrity Violation Detected!")
        for err in res["errors"]:
            print(f"  - {err}")
        print("\nAll modifications to governance assets require approval ledger entries and differential reports.")
        sys.exit(1)
        
    print(f"\n[SUCCESS] Governance integrity check passed. {res['verified_count']} assets verified.")
    for warn in res["warnings"]:
        print(f"  - [APPROVED BYPASS] {warn}")
    sys.exit(0)

if __name__ == "__main__":
    main()
