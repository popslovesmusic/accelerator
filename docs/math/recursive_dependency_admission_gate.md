# Recursive Dependency Admission Gate (MPF-DEP-005)

## 1. Purpose
This document performs the **formal documentation** for the recursive dependency admission gate. Its primary goal is to determine whether any recursive dependency may enter theorem-facing, simulation-facing, or review-facing infrastructure after passing the Recursive Inheritance Firewall (MPF-DEP-004). It ensures that only validated and properly constrained dependencies propagate into the higher layers of the proof and simulation pipelines.

## 2. Admission Targets

### 2.1 Theorem-Facing Admission (RDAG-T001)
- **Requirement**: Only artifacts classified as `INHERITANCE-ALLOWED` or explicitly constrained `INHERITANCE-CONDITIONAL` may enter theorem-facing review.

### 2.2 Simulation-Facing Admission (RDAG-T002)
- **Requirement**: Simulation inputs must exclude quarantined, blocked, deceptive, or unresolved global-composition artifacts unless they are explicitly identified and used as adversarial stress-test cases.

### 2.3 Review-Facing Admission (RDAG-T003)
- **Requirement**: Review artifacts must preserve all open blockers, excluded domains, and established simulation-evidence limits. No admission may implies discharging a preserved failure.

### 2.4 Quarantine Enforcement (RDAG-T004)
- **Requirement**: Artifacts marked `INHERITANCE-BLOCKED` or `INHERITANCE-QUARANTINED` are strictly forbidden from entering proof-supporting derivation chains.

### 2.5 LAW034 Composition Guard (RDAG-T005)
- **Requirement**: No admitted dependency may imply or require global compositional closure from the continuation grammar (LAW034).

## 3. Admission Classes
- **ADMISSION-GRANTED**: Dependency may enter restricted-local review infrastructure.
- **ADMISSION-CONDITIONAL**: Dependency may enter only with explicit constraints and review-required status.
- **ADMISSION-STRESS-ONLY**: Dependency may be used only for adversarial simulation or failure-testing.
- **ADMISSION-DENIED**: Dependency may not enter theorem-facing or proof-supporting infrastructure.
- **ADMISSION-QUARANTINED**: Dependency retained only for historical or diagnostic reference.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

**MANDATE**: Every recursive dependency must pass the admission gate before being integrated into formal review or proof-facing derivation.

---
[Back to Master Index](codex_master_index.md)
