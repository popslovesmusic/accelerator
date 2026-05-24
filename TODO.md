# Acellorator: Post-Unity Arc Roadmap (Phase II)

This document tracks the strategic objectives following the successful consolidation and relocking of the foundational mathematical program (The Unity Arc).

## Current Standing
- **Math Program:** SIMULATED / CONDITIONALLY_PROVEN (Unity Arc Complete).
- **Core Engines:** C4 Certified.
- **Global Health:** GREEN (Passing).

---

## Active TODO List

### 1. Automated Adversarial Rigor (Immediate Priority)
- [x] **Task 1.1: Implement `scripts/adversary_harness.py`**
    - [x] Design the wrapper logic to pair standard simulations with mandatory `micro_attack_suite` probes.
    - [x] Automate report generation for `falsification_report.json` and `uncertainty_report.json`.
    - [x] Integrate with `evidence_index.json` to prevent indexing of un-pressured runs.
- [x] **Task 1.2: Hard-Gate `governance_gate.py`**
    - [x] Require presence of adversary harness artifacts for any claim level C4 or higher.

### 2. Research Campaign: RES-LIMIT-01 (The Resolution Frontier)
- [x] **Task 2.1: Map the Implementation Schism**
    - [x] Execute a sweep of $N \in \{3, 5, 10, 20, 50, 100\}$ comparing Graph Dynamics vs CA Admissibility.
    - [x] Identify the critical resolution constant ($N_{crit} = 50$) where mechanism independence stabilizes.
- [x] **Task 2.2: Elevate MST-001 to C6**
    - [x] Update Symbolic Trace (P027) with the $N_{crit}$ boundary.
    - [x] Re-promote Theorem V to Level C6 (Theorem) with formal scope limits.

### 3. Governance Debt Reduction (In Progress)
- [x] **Task 3.1: Auto-Narrative Integration**
    - [x] Integrate `generate_paper()` into `scripts/adversary_harness.py`.
- [x] **Task 3.2: Unified Manifest Migration**
    - [x] Design graph-based schema in `registry/governance_manifest.json`.
    - [x] Implement migration script `scripts/db/migrate_to_unified_manifest.py`.
    - [x] Update `governance_gate.py` and `global_validate.py` to use the unified manifest.
    - [x] Archive legacy registries.
- [x] **Task 3.3: CI-Locking Hook**
    - [x] Implement automated hash verification for foundational documents (`scripts/governance/enforce_locks.py`).
    - [x] Integrate lock enforcement into `run_global_validation.bat`.

---
**Standard ID:** MPF-ROADMAP-002
**Status:** ACTIVE
**Primary Executor:** Gemini CLI (Auto-Edit)
