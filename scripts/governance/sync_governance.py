#!/usr/bin/env python
import os
import sys
import subprocess

def run_command(args):
    print(f"Running: {' '.join(args)}")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(args)}")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        return False, result.stdout + "\n" + result.stderr
    return True, result.stdout

def main():
    print("=== Starting Governance Integrity Synchronization ===")
    
    # Step 1: Re-baseline hashes
    success, output = run_command([sys.executable, "scripts/governance/enforce_governance_integrity.py", "--initialize"])
    if not success:
        print("Failed to re-baseline hashes.")
        sys.exit(1)
    print("Hashes successfully re-baselined.")
    
    # Step 2: Refresh database snapshot
    success, output = run_command([sys.executable, "scripts/db/snapshot_registries.py"])
    if not success:
        print("Failed to refresh database snapshot.")
        sys.exit(1)
    print("Database snapshot refreshed.")
    
    # Step 3: Run global validation
    success, output = run_command([sys.executable, "scripts/global_validate.py"])
    if not success:
        print("Global validation failed.")
        sys.exit(1)
    print("Global validation passed successfully.")
    
    # Step 4: Automatically stage registry files in Git
    success, output = run_command(["git", "add", "registry/governance_hash_registry.json"])
    if not success:
        print("Failed to stage registry changes in Git.")
        sys.exit(1)
    print("Staged registry/governance_hash_registry.json in Git.")
    
    print("\nGovernance synchronized and validated successfully! You can now commit your changes.")

if __name__ == "__main__":
    main()
