# Governance Change Workflow

This guide details the procedure for modifying protected governance files (such as `AGENTS.md` and `GEMINI.md`) and resolving blocking integrity states in the repository.

---

## 1. Why Integrity Checks Exist
To ensure structural soundness and prevent unauthorized modifications to core principles (like the Calculus of Distinction rules or Department SSOTs), the repository employs a **two-phase integrity lock**:
- Core assets are monitored for SHA256 matches against [governance_hash_registry.json](file:///d:/projects/acellorator/registry/governance_hash_registry.json).
- Modifying a protected asset without updating its baseline hash triggers validation failures in `global_validate.py`.

---

## 2. Standard Modification Procedure
When you need to update a protected governance asset, follow this workflow:

### Step 1: Make your changes
Modify the protected files (e.g., adding rules to `AGENTS.md`).

### Step 2: Synchronize and Validate
Run the developer synchronization tool:
```powershell
python scripts/governance/sync_governance.py
```
This single command will:
1. Regenerate SHA256 hashes for modified protected files.
2. Refresh the SQLite database snapshot to keep indexing in a `"fresh"` state.
3. Execute the global validation suite to ensure no semantic errors were introduced.
4. Stage the updated hash registry `registry/governance_hash_registry.json` in Git.

### Step 3: Commit
After validation passes, record your changes:
```bash
git commit -m "docs(governance): update rules and re-baseline integrity hashes"
```

---

## 3. Resolving a Blocked Repository
If a commit fails due to the Git pre-commit hook blocking, or if automated validation shows failures under `governance_integrity_validation`, run:
```powershell
python scripts/governance/sync_governance.py
```
This automatically updates the baseline hashes and database metadata, restoring the repository to a passing state.
