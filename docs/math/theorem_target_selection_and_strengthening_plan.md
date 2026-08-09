# Theorem Target Selection and Strengthening Plan (META-006)

## Executive Summary
Following the consolidation of LAW-001 through LAW-034 (META-005), this plan selects the highest-priority candidates for formal theorem strengthening. The objective is to move from "candidate law" descriptions to "formally supported" lemmas by addressing specific proof blockers, defining rigorous metrics, and satisfying counterexample obligations.

## 1. High-Priority Theorem Targets

### MT-LAW-A: Bounded Continuation Persistence Lemma
- **Priority**: Highest
- **Core Statement**: A continuation structure (basin or channel) can persist only while admissibility projection remains defined, transport flux remains finite, and local admissibility cost remains within budget tolerance.
- **Dependencies**: LAW-001 (delta), LAW-002 (Pi_A), LAW-004 (finite flux), LAW-011 (basins), LAW-021 (budgets).
- **Proof Blockers**: 
  - Need explicit persistence metric ($\eta_B$ refinement).
  - Need formalization of admissibility-cost ($Cost_A$).
  - Need explicit assumptions for finite-flux bounds.
  - Need formal tolerance definitions.

### MT-LAW-B: Projectional Geometry Dependency Lemma
- **Priority**: High
- **Core Statement**: Apparent geometry projects from stabilized accessibility topology and orientation-array structure; primitive metric geometry cannot be reintroduced.
- **Dependencies**: LAW-006 (distinction), LAW-008 (accessibility), LAW-010 (apparent geometry).
- **Proof Blockers**:
  - Need explicit definition of accessibility topology ($Top_A$).
  - Need formal conditions for the projection map ($Proj_{geom}$).
  - Need nonprimitive-geometry exclusion criterion.

### MT-LAW-C: Reconstruction Non-Uniqueness Lemma
- **Priority**: High
- **Core Statement**: Multiple distinct continuation histories may reconstruct into equivalent observable structures under bounded observability and recursive loss.
- **Dependencies**: LAW-016 (asymmetry), LAW-017 (compression), LAW-023 (observability).
- **Proof Blockers**:
  - Need equivalence relation over reconstructed states ($\sim_{obs}$ refinement).
  - Need rigorous compression-loss metric ($Loss(C_P, n)$).
  - Need criteria for ambiguity regions.

### MT-LAW-D: Finite Budget Competition Lemma
- **Priority**: Medium
- **Core Statement**: Shared finite admissibility budgets necessitate arbitration outcomes including suppression, starvation, and co-stabilization.
- **Dependencies**: LAW-014 (competition), LAW-021 (budgets), LAW-024 (ecology), LAW-029 (arbitration).
- **Proof Blockers**:
  - Need shared-budget definition for interacting basins.
  - Need formal competition relation ($Compete(B_i, B_j)$).
  - Need taxonomy of arbitration outcomes.

## 2. Strengthening Roadmap

### Phase 1: Definition Tightening
Before proofs can be attempted, the following metrics must be formalized:
- **Persistence Metric**: Quantitative stability of basins.
- **Admissibility-Cost Metric**: Resource consumption rules.
- **Budget Tolerance**: Limits of regional sustainability.
- **Reconstruction Equivalence**: Criteria for observational indistinguishability.

### Phase 2: Counterexample Obligations
Identify conditions under which the lemmas would fail to identify fundamental framework limits:
- Persistence failure under undefined projection or infinite flux.
- Observational equivalence of divergent prehistories.
- Violation of topology-first principles by primitive geometric shortcuts.

### Phase 3: Simulation Targets
Rigorous simulation data from C++ engines must support the conceptual lemmas:
- **Budget Saturation**: Observing collapse as resources are exhausted.
- **Flux Growth Destabilization**: Measuring the breakdown of basins under unbounded transport.
- **History Compression**: Demonstrating the loss of discriminating structural features.

## 3. Governance Constraints
- **Pause Expansion**: No new "laws" (e.g., LAW-035) until these targets are strengthened.
- **No Promotion**: All targets remain "candidate lemmas" until proof blockers are resolved and reviewed.
- **No Physics Overclaim**: Lemmas remain properties of the Mono-Process Framework topology and budget rules.

---
[Back to Master Index](codex_master_index.md)
