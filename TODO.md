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
- [x] **Task 4.3.1: Lexicon Gap Resolution (MNT-LEX-001)**
    - [x] Promoted 'Singularity/Rebound' cluster to L2 (evidence: SINGULARITY-REBOUND-001).
    - [x] Evaluated 'Phase Dynamics' cluster; downgraded to L1/Descriptive (evidence: LFCR_004).
    - [x] Deferred Zeta/Center clusters pending primitive mapping.
    - [x] Unified registry sync passed.
- [x] **Task 4.4: Execute Module CLS_003 (Collapse and Reformation Basin Validation)**
    - [x] Measurement channels and pass/fail criteria verified across `structural_box` and `graph_dynamics`.
    - [x] Zeta mapping probes (`Pi_zeta`, `Center_Control_Functional`) promoted to L2 status.
    - [x] Elevated `L5_RIGOR_FORKED_ATTACK` to supported C5 status.
- [x] **Task 4.5: Basin Signature Formalization (CLS_004)**
    - [x] Implemented `scripts/cls_004_basin_analyzer.py` for $\Sigma$ extraction.
    - [x] Verified 100% rotation stability under perturbation.
    - [x] Identified quadrant occupancy volatility as a resolution artifact.
- [x] **Task 4.6: Relational Basin Signature Validation (CLS_004R)**
    - [x] Implemented `scripts/cls_004R_relational_analyzer.py` for $\Sigma_R$ extraction.
    - [x] Verified 100% stability for Rotation ($\chi$) and Window ($W_a$) invariants.
    - [x] Confirmed $\Sigma_R$ functions as a **Class Marker** (85% collision rate across distinct trajectories).
    - [x] Reclassified quadrant volatility as **Boundary-Front Interaction**.
- [x] **Task 4.6.1: CLS_004R Follow-up Induction**
    - [x] Register **Sigma_R** as provisional relational signature object. (Completed: relational_signature_registry.json)
    - [x] Add **Wa**, **rho_D**, **chi**, **R_{-(i)}**, and **boundary_front** to lexicon gap queue. (Completed: lexicon_gap_queue.json)
    - [x] Add **CLS_004R** results to claim registry with status L2. (Completed: claim_registry.json)
    - [x] Audit **OPEN_BRIDGE_001** to determine whether prior falsification tested isolated variables rather than whole RT expressions. (Completed: AUDIT_OPEN_BRIDGE_001_WHOLE_EXPRESSION_PRIMACY)

- [x] **Task 4.7: Macroscopic Projection and Behavioral Prediction**
    - [x] Map $\Sigma_R$ to predicted response basins in `structural_box_sim_cpp`.
    - [x] Verify that $W_a$ membership predicts perturbation survival.

---
## Phase IV: Whole-Expression RT Validation (aRT)

- [x] **Task 6.0: Whole-Expression RT Perturbation Campaign** (`MPF_SIM_ART_001`)
    - [x] Develop Python simulation engine (`sim_art_001.py`) to test aRT deformations vs component ablation.
    - [x] Implement control models M0_full_aRT, M1_simple_ablation, M2_substituted_orientation, M3_substituted_residue, M4_random_shuffle, M5_trace_preserving.
    - [x] Execute multi-seed campaign ($N=64$, 20 seeds, 1000 iterations).
    - [x] Generate summary reports and falsification audit.

    - [x] Develop Python (`numpy` based) simulation engine (`sim_array_graph_001.py`).
    - [x] Implement $U_\Omega$ update loop tracking distinction matrix $\chi_D$, orientation, residue, and admissibility.
    - [x] Implement control models (M0-M6) representing various ablation regimes (random arbitration, no residue, no orientation, no floor, etc.).
    - [x] Execute minimum viable exploratory run ($N=64$, 20 seeds, 1000 iterations).
    - [x] Generate summary reports, plots, and falsification audit.
- [x] **Task 4.8: Execute PD_CG Root-Trace Falsification (PD_CG_V1)**
    - [x] Performed `ATTACK_001_ROOT_DRIFT` (Verified derivation of $<\neq>_r$ in PD_CG_NOTE_001).
    - [x] Executed `ATTACK_002` to `ATTACK_005` (Confirmed 100% $W_a$ stability vs 0% boundary stability).
    - [x] Formalized **Relational Hierarchy** (Core Invariants C5 vs Interaction Observables C2).
- [x] **Task 4.9: Re-Audit OPEN_BRIDGE_001 (Orientation-Closure)**
    - [x] Inducted `PD_CG_V2_PROCEDURAL_ORIENTATING_REAUDIT.json`.
    - [x] Performed sequence-level orientating analysis (Confirmed ablation impact 97%).
    - [x] Verified procedural mediation of boundary-front stabilization.
    - [x] Re-promoted OPEN_BRIDGE_001 to RECOVERY_PENDING (Living SSOT updated).




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

### 7. Induction Integration Follow-ups (PROVISIONAL - 2026-06-17)
- [x] **Task 7.0: Initial Integration of MPF_IND_2026_06_17_CORE_REDUCTION**
    - [x] Archive induction payload in `outputs/reports/`.
    - [x] Register 3 provisional claims in `claim_registry.json`.
    - [x] Update Chapter 1.2A and 1.7 of `mono_process_textbook_complete.md`.
    - [x] Induct core terms (RT, Generative Exclusion, Evaluation Process, Sign) into gap queue.
- [x] **Task 7.1: Resolve RT Formation Gap (GAP_RT_FORMAL_CRITERION)**
    - [x] Define the precise admissibility condition ($ \mathcal{A} $) under which a precursor distinction becomes an RT.
- [x] **Task 7.2: Formalize RT Core Equivalence (GAP_RT_CORE_EQUIVALENCE)**
    - [x] Investigate and prove whether $ RT := [D \neq 0 \langle * \rangle_x D = 0] $ is formally equivalent to the canonical core or structurally analogous.
- [ ] **Task 7.3: Define Sign Semantics (GAP_SIGN_SEMANTICS)**
    - [ ] Formalize the notation for additive-signature vs. exclusion-signature and map to generative process pathways.
- [ ] **Task 7.4: Map Evaluation Architecture (GAP_EVALUATION_ARCHITECTURE)**
    - [ ] Formally define the relationship between the framework's governance process and the underlying admissibility/evaluation process.

### 8. Repository Maintenance & Governance Debt
- [/] **Task 8.1: Lexicon Gap Resolution (MNT-LEX-002)**
    - [x] Initial Phase: Resolved 28 priority gaps (Core, Basin, Mathematical objects) and cleaned up noise artifacts.
    - [ ] Ongoing: Resolve the remaining 17 `GAP_OPEN` entries in `registry/lexicon_gap_queue.json` and keep `registry/lexicon_validation_registry.json` aligned with the core validation set.
- [ ] **Task 8.2: Results Hygiene - Legacy Cleanup (MNT-RES-001)**
    - [ ] Standardize the naming of legacy result folders to match the required `YYYY-MM-DD_runNN_name` schema.
- [ ] **Task 8.3: Living SSOT Formalization (MNT-SSOT-001)**
    - [ ] Address 'Syntax Closure' and 'Semantic Closure' requirements in the textbook as identified in `docs/textbook/textbook_formal_system_gap_assessment.md`.
    - [ ] Specify formal object classes and well-formedness rules for the core calculus.

---
**Standard ID:** MPF-ROADMAP-002
**Status:** ACTIVE
**Primary Executor:** Gemini CLI (Auto-Edit)
