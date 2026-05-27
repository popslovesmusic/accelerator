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

### 4. Phase II Master Campaign: Cross-Layer Stability (INITIALIZED)
- [x] **Task 4.1: Campaign Initialization**
    - [x] Campaign definition created in `campaigns/BOOK_CAMPAIGN_PHASE_01_MASTER.json`.
    - [x] Result directory established: `results/2026-05-27_run01_BOOK_CAMPAIGN_PHASE_01_MASTER/`.
    - [x] Lexicon terms induced (Adaptive Routing, Recursive Identity, etc.).
    - [x] Tool readiness verified (StructuralBox, SignalScope, TDA, Kuramoto).
- [x] **Task 4.2: Execute Module CLS_001 (Recursive Stability Validation)**
    - [x] Run `signal_scope_phase_continuation_engine` simulations.
    - [x] Perform cross-verification with `structural_box_sim_cpp`.
    - [x] Perform Lexicon Out-Check and Claim Gate.
- [x] **Task 4.3: Execute Module CLS_002 (Geometry and Ratchet Continuity)**
    - [x] Run hysteresis ramps in `structural_box_sim_cpp`.
    - [x] Test geometry deformation and residue lag vectors.
- [ ] **Task 4.4: Execute Module CLS_003 (Collapse and Reformation Basin Validation)**

### 5. Procedural PDE Engine (2D/3D Campaign Spec V0.1)
- [x] **Task 5.1: Create 2D C++ baseline engine**
    - [x] Scaffold core C++ headers (`grid.hpp`, `fields.hpp`, `update_rules.hpp`, `metrics.hpp`, `io.hpp`).
    - [x] Implement 2D step logic (`engine_2d.cpp`, `main.cpp`).
    - [x] Create JSON config and Python orchestrator (`pde_2d_baseline.json`, `run_campaign.py`).
    - [x] Run 32 seeds and emit `multi_seed_summary.json` with required metrics.
- [x] **Task 5.2: Falsification Vector Validation (2D)**
    - [x] Implement and test FV_001 through FV_008 on the 2D engine.
- [x] **Task 5.3: Phase 2 - 3D Port**
    - [x] Implement `engine_3d.cpp` and update `main.cpp`.
    - [x] Run 3D baseline (16 seeds) and compare invariants against 2D.





---
**Standard ID:** MPF-ROADMAP-002
**Status:** ACTIVE
**Primary Executor:** Gemini CLI (Auto-Edit)
