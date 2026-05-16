# Aspect-Relation Trace Schema (MPF-PALG-007)

## 1. Purpose
This document defines a recoverable schema for recording how any analyzed aspect (such as exclusion, continuation, or polarity) remains bound to its indivisible source relation. By enforcing mandatory traceability, the framework prevents analytical decomposition from being mistaken for ontological separation or primitive status.

## 2. Core Rule: Aspect Traceability
Every isolated aspect must retain a recoverable trace to the indivisible source relation from which it was analytically projected.
- **Short Form**: $\boxed{ aspect(x) \to trace\_to(Whole_R) }$

## 3. Trace Schema Definition
A valid aspect trace must include the following fields:
- **trace_id**: Unique identifier for the trace record.
- **source_relation**: The indivisible process relation (e.g., $(E \neq 0) \iff_R \delta(E > 0)$) from which the aspect originates.
- **aspect_label**: The symbolic representation of the aspect being analyzed (e.g., $-1$ or $\Pi_E$).
- **analysis_mode**: Explicitly restricted to `projection_only`, `local_analysis`, or `analogy_only`.
- **non_separability_acknowledged**: A mandatory boolean flag confirming that the analyst recognizes the aspect is not independently fundamental.
- **primitive_status**: Fixed to `false`. Traced aspects cannot be promoted to primitives.
- **claim_level**: Fixed to `ANALOG_MODEL_ONLY`.

## 4. Invalid Trace Conditions
A trace is invalidated if any of the following occur:
- The aspect has no recorded source relation.
- The aspect is promoted to primitive status.
- Non-separability is not explicitly acknowledged.
- Feature loss (e.g., loss of simultaneity) is not recorded.
- The projection is treated as proof of the underlying relation.

## 5. Usage Rules

### 5.1 Allowed Uses
- Tracking aspect-level analysis without violating indivisibility.
- Recording what is retained and lost when a whole relation is projected.
- Preventing symbolic convenience from being mistaken for ontological reality.

### 5.2 Forbidden Uses
- Using a traced aspect as an independent primitive or "building block."
- Treating traceability as proof of the relation.
- Dropping the source relation link once projection is complete.
- Claiming physical interpretations directly from aspect traces.

## 6. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Schema Status**: CANDIDATE_TRACE_SCHEMA.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)


---
**source_relation**: (E≠0) ⇔R δ(E>0)
**non_separability_acknowledged**: non-separability acknowledged
