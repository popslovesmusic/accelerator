#!/usr/bin/env python
import os
import sys
import subprocess
import argparse

EXECUTION_BUDGET_SECONDS = 300

def run_command(args):
    print(f"Running: {' '.join(args)}")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=EXECUTION_BUDGET_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"FAIL: execution budget exceeded for {' '.join(args)}")
        print(f"Execution budget: {EXECUTION_BUDGET_SECONDS} seconds")
        return False, f"FAIL: execution budget exceeded: {exc}"
    if result.returncode != 0:
        print(f"FAIL: command returned exit code {result.returncode}: {' '.join(args)}")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        return False, result.stdout + "\n" + result.stderr
    return True, result.stdout

def main():
    parser = argparse.ArgumentParser(
        description="Run governance synchronization. Terminal outcome is PASS or FAIL only."
    )
    parser.parse_args()
    print("=== Starting Governance Integrity Synchronization ===")
    
    # Step 1: Re-baseline hashes
    success, output = run_command([sys.executable, "scripts/governance/enforce_governance_integrity.py", "--initialize"])
    if not success:
        print("PROCESS_OUTCOME=FAIL")
        sys.exit(1)
    print("Hashes successfully re-baselined.")
    
    # Step 2: Refresh database snapshot
    success, output = run_command([sys.executable, "scripts/db/snapshot_registries.py"])
    if not success:
        print("PROCESS_OUTCOME=FAIL")
        sys.exit(1)
    print("Database snapshot refreshed.")
    
    # Step 3: Run global validation
    success, output = run_command([sys.executable, "scripts/global_validate.py"])
    if not success:
        print("PROCESS_OUTCOME=FAIL")
        sys.exit(1)
    print("Global validation passed successfully.")
    
    # Step 4: Automatically stage registry files in Git
    success, output = run_command(["git", "add", "registry/governance_hash_registry.json"])
    if not success:
        print("PROCESS_OUTCOME=FAIL")
        sys.exit(1)
    print("Staged registry/governance_hash_registry.json in Git.")
    
    print("\nPROCESS_OUTCOME=PASS")
    print("Governance synchronized and validated successfully. You can now commit your changes.")

if __name__ == "__main__":
    main()
