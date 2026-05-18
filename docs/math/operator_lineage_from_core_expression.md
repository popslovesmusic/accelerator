# Operator Lineage from Core Expression

## 1. Purpose
This document formally traces the lineage of the primary operators of the Mono-Process Framework back to the canonical root expression: **(ℰ≠0) ⇔_R δ(ℰ>0)**. This ensures they are understood as derived aspects of the core process, not independent primitives.

## 2. Operator Derivations

### 2.1 Continuation Operator (δ)
- **Lineage:** `continuation_aspect`
- **Derivation:** The δ operator is the explicit formalization of the continuation aspect of the core expression, δ(ℰ>0). It represents the selection of an admissible next state that reduces the source distinction (mismatch).

### 2.2 Admissibility Projection Operator (Π_A)
- **Lineage:** `residue_binding_aspect`
- **Derivation:** The admissibility window $A$ is defined by the persistence of residue $R$. The Π_A operator, which filters for admissible states, is therefore a direct projection of the residue-conditioning (⇔_R) that governs what continuations are possible.

### 2.3 Residue Transport Operator (NavT)
- **Lineage:** `continuation_aspect`
- **Derivation:** NavT models the propagation of the consequences of a continuation event. It is the mechanism by which the selection of a next state at locus $\alpha$ influences the state at locus $\beta$.

### 2.4 Reconstruction Operator (Ξ)
- **Lineage:** `residue_binding_aspect`
- **Derivation:** The Ξ operator attempts to invert the process history by reading the residue field $R$. Its existence and limitations are a direct consequence of the information-preserving (or information-losing) nature of the residue-conditioned binding (⇔_R).

### 2.5 Arbitration Operator (Arb_A)
- **Lineage:** `continuation_aspect`
- **Derivation:** Arb_A is a higher-order form of the core continuation operator δ. It resolves conflicts between multiple potential continuation paths when δ(ℰ>0) is multi-valued, ensuring a single process outcome under budget constraints.

### 2.6 Topology Evolution Operator (T_E)
- **Lineage:** `stabilized_projection`
- **Derivation:** T_E maps the entire stabilized topological structure from one state to the next. It is an operator that acts on projections of the whole process, not a primitive transformation.

## Status Footer
- **Patch ID:** MPF-CORE-TRACE-012
- **Status:** LINEAGE_MAPPED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
