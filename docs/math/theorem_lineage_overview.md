# Theorem Lineage Overview

This document tracks the conceptual and formal lineage of local theorems within the Mono-Process Framework.

## Local Theorem Candidates

### MT-001: Projection Idempotence Under Stable Admissibility
- **Lineage**: Emerged from the requirement for stable admissibility windows in recursive process continuation.
- **Intuition**: Applying the admissibility projection multiple times should yield the same result if the window is stable.
- **Status**: Consolidated. Active in proof-elevation and counterexample campaigns.

### MT-002: Transport Identity on Null Path
- **Lineage**: Derived from the necessity of preserving process identity during zero-length transport operations (NavT).
- **Intuition**: Transporting a state across a distance of zero should return the original state unchanged.
- **Status**: Consolidated. Active in proof-elevation and counterexample campaigns.

### MT-003: Continuation Requires Non-Empty Admissible Image
- **Lineage**: Foundational requirement for process existence.
- **Intuition**: A process can only continue if there is at least one candidate transition that is both selected and admissible.
- **Status**: Consolidated. Active in proof-elevation and counterexample campaigns.

## Live Campaign Context
- The current governed execution order places `PROOF-ELEVATION-CAMPAIGN-001` and `MT-PROOF-ELEVATION-001` in `PHASE_1_FORMAL_FOLLOW_THROUGH` ahead of `MT-COUNTEREXAMPLE-001`.
- The formal follow-through sync for `PROOF-ELEVATION-CAMPAIGN-001` and `MT-PROOF-ELEVATION-001` reconciled the MT-001, MT-002, and MT-003 readiness reports to the live formal artifact state; no theorem-status promotion followed.
- These lineages remain descriptive and do not assert proof elevation or validation.

## Governance Note
These lineages are provided for human readability and conceptual mapping. They do not constitute formal proof elevation or physical validation.
