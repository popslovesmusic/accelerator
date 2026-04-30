# Plan for C4 Status Elevation (2026-04-29)

## Overview
This document outlines the strategic roadmap to elevate the Acellorator ecosystem to **C4 Status (Experimental Stability & Characterized Uncertainty)**.

## 1. Multi-Seed Stability (R1)
- **Status:** `multi_sim_runner.py` supports seed expansion.
- **Goal:** Update all claim-relevant experiment configs to use **>=5 seeds** as a baseline.
- **Action:** Create `configs/standard/c4_multi_seed_template.json`.

## 2. Multi-Model Verification (R2)
- **Status:** Supported by runner; several tool classes have Python/C++ counterparts.
- **Goal:** Standardize "cross-model" jobs in the runner for all Level 3 claims.
- **Action:** Implement a `cross_model_validator` utility in `multi_sim_runner.py` to compare outputs between model classes.

## 3. Falsification Enforcement (R3)
- **Status:** C++ ports for high-rigor tools have built-in falsification.
- **Goal:** Ensure every C4 candidate run includes a dedicated `falsification` job role.
- **Action:** Update `tool_manifest.json` to flag tools with automated falsification paths.

## 4. Numerical Convergence (R4)
- **Status:** Gaps identified. `convergence_report.json` files are currently empty.
- **Goal:** Implement automated parameter sweeps for grid/step refinement.
- **Action:** Create `scripts/run_convergence_sweep.py` targeting PDE/ODE engines.

## 5. Uncertainty Quantification (R5)
- **Status:** Missing from current runner output.
- **Goal:** Runner must calculate variance and confidence intervals across seeds.
- **Action:** Enhance `multi_sim_runner.py` post-run to produce `uncertainty_summary.json`.

## 6. Provenance Completeness (R6)
- **Status:** Mostly present in v2.3 reports.
- **Goal:** Every run must capture `source_commit` and `config_hash`.
- **Action:** Runner to fetch current git commit and hash input configs into `run_manifest.json`.

## 7. CPU/GPU Drift Checks (R7)
- **Status:** Confirmed for D-ASE and core high-rigor C++ ports.
- **Goal:** Standardize drift reporting for all SYCL tools.
- **Action:** Audit all `_cpp` engines for `precision_drift` metric emission.

## 8. Python/C++ Equivalence (R8)
- **Status:** Regression required before archiving Python.
- **Goal:** Generate `regression_report.json` for all 23 ports.
- **Action:** Create `scripts/run_regression_testing.py`.

## 9. v2.3 Schema Standardization (R9)
- **Status:** Established but requires exhaustive application.
- **Goal:** 100% compliance across 38 tools.
- **Action:** Add schema validation to the preflight check.

## 10. Integrated Governance Output (R10)
- **Status:** `claim_gate_input.json` and `certification_evidence_packet.json` implemented.
- **Goal:** Maintain and automate verification of these artifacts.
- **Action:** (Complete)

---
## Execution Phases

### Phase 1: Infrastructure Upgrade
- Enhance `multi_sim_runner.py` with uncertainty and provenance features.
- Implement `run_convergence_sweep.py` and `run_regression_testing.py`.

### Phase 2: Tool Certification
- Run regression tests for all Python/C++ pairs.
- Run convergence sweeps for all PDE/ODE tools.
- Update all `certification_manifest.json` files to C4 where applicable.

### Phase 3: Validation & Archival
- Update Scientific Rigor Report.
- Archive Python simulators with verified C++ counterparts.
