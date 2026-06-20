# S Arbitration Rule Audit Report

## 1. Scope
* **Target:** $S$ Arbitration Rule (S-stage) inside the continuation operator $\delta_a$.
* **Audited registries and artifacts:** `formal_object_registry.json`, `operator_registry.json`, `metric_registry.json`, `bridge_dependency_registry.json`, `mono_process_textbook_complete.md`, Appendix F.
* **Purpose:** Audit the unresolved S Arbitration Rule and determine whether $S$ is missing, partially defined, or already implicit in the admissibility/arbitration machinery.

## 2. Answers to Audit Questions

### Q1: Where is $S$ currently referenced in textbook, registries, and simulation tools?
* **Answer:** $S$ is referenced in:
  1. [mono_process_textbook_complete.md](file:///D:/projects/acellorator/docs/textbook/mono_process_textbook_complete.md) (Appendix F: High-Priority Gaps).
  2. [MPF_PATCH_R_DUAL_PHASE_FIXES_002.json](file:///D:/projects/acellorator/registry/governance/patches/MPF_PATCH_R_DUAL_PHASE_FIXES_002.json) (under `S_arbitration_rule`).
  3. [CRITICAL_PATH_RESOLUTION_PATCH_001.json](file:///D:/projects/acellorator/patches/CRITICAL_PATH_RESOLUTION_PATCH_001.json) (under `S_arbitration_rule`).
  4. In the simulation code, the pruning behavior is implicitly executed via the `admissibility_filter` and sequential validity checks.

### Q2: Is $S$ a pruning rule, scoring rule, selector stage, or sub-operator of $\delta_a$?
* **Answer:** $S$ functions as a **pruning/filtering stage and sub-operator** inside the $\delta_a$ composition. It acts to sequentially eliminate candidates that violate process constraints before they can be arbitrated (ranked and selected).

### Q3: Does $\text{Arb}_A$ depend on $S$, or does $S$ precede $\text{Arb}_A$?
* **Answer:** **$S$ precedes $\text{Arb}_A$.**
* **Details:** $\delta_a$ uses $S$ to prune the raw candidate set $Q_\alpha$ down to the set of admissible candidates. $\text{Arb}_A$ then selects from this pruned admissible set. Without the $S$-stage, $\text{Arb}_A$ would be forced to arbitrate over illegal candidates, risking core collapse.

### Q4: Can $\delta_a$ produce a candidate continuation set without $S$?
* **Answer:** **No.**
* **Details:** Without the $S$-stage, $\delta_a$ has no mechanism to filter candidate transitions, meaning it would pass all possible perturbations, leading to immediate violation of conservation laws and process collapse.

### Q5: Can $\text{Arb}_A$ select from candidates without $S$?
* **Answer:** **No.**
* **Details:** $\text{Arb}_A$ cannot operate on raw un-gated candidates without violating the core principle of admissibility. $S$ is the mathematical gatekeeper that supplies $\text{Arb}_A$ with its domain.

### Q6: Do existing campaigns already implement $S$ under another name?
* **Answer:** **Yes.**
* **Details:** In the simulation engines, $S$ is implemented operationally under names such as `admissibility_filter`, sequential validity checks (`check_distinction`, `check_residue`, `check_orientation`), or candidacy filtering.

### Q7: Which downstream bridge or app claims depend on $S$?
* **Answer:**
  - `OPEN_BRIDGE_001` (since it relies on selector-form routing).
  - `topological_selector_routing`.
  - `asymmetric_triadic_closure` ($\text{TC}_{\text{asym}}$).

## 3. Inferred inside Framework
* The $S$-stage enforces the sequential candidacy check order:
  1. Type Admissibility
  2. Nonzero Distinction check ($\mathcal{E} > 0$)
  3. Residue compatibility
  4. Topology preservation
  5. Orientation compatibility
  6. Arbitration ranking

## 4. What it does NOT prove
* This audit does not prove that natural systems prune possibilities in this exact sequential order; it only establishes that the Mono-Process computational engine requires this sequential filter structure for mathematical well-posedness.

## 5. Ruling
* **Ruling:** `PARTIALLY_DEFINED` (The rule is conceptually and candidate-ordered, but requires a canonical definition patch in Appendix F to align it with `DEFINITION_TARGET_IDENTIFIED`).
