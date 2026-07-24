# Execution Plan: Governance Hash Alignment

This plan outlines the steps required to restore the repository to a clean validation status.

## Steps

1. Run the governance integrity script with the `--initialize` flag to synchronize the baseline hash registry with the modified `GEMINI.md` and `AGENTS.md` assets:
   ```powershell
   python scripts/governance/enforce_governance_integrity.py --initialize
   ```
2. Re-snapshot the registries to update the database freshness marker and include the latest commits/changes:
   ```powershell
   python scripts/db/snapshot_registries.py
   ```
3. Run the global validation suite to ensure that all stages pass successfully:
   ```powershell
   python scripts/global_validate.py
   ```
4. Verify that the freshness status is green:
   ```powershell
   python scripts/query_governance.py freshness
   ```
5. Once all validations pass, perform a git commit to record the task-scoped governance alignment delta.
