# Formal Core Expression Semantics

## 1. Purpose
This document defines the formal mathematical semantics of the core expression, **(ℰ≠0) ⇔_R δ(ℰ>0)**, ensuring it is not reduced to ordinary logical or algebraic equivalence.

## 2. Semantic Breakdown

### 2.1 Distinction: (ℰ≠0)
This term represents a **non-null element in the mismatch space**. It is not a variable to be solved for, but a condition of distinguishability that must be met for the process to have a driver.
- **Formal Reading:** The state of the local process projection is not an element of the null-mismatch kernel.

### 2.2 Continuation: δ(ℰ>0)
This term represents the **application of the continuation operator δ to a state of positive distinguishability**.
- **Formal Reading:** The operator δ selects a next state from the set of admissible continuations, where admissibility is determined by the residue-conditioned projection $\Pi_A$. The selection is biased toward states that minimize the source mismatch ℰ.

### 2.3 Recursive Aspect-Binding: ⇔_R
This is the core connective, representing **residue-conditioned, mutually-constituting co-arity**.
- **Formal Reading:** Let $D$ be the distinction aspect and $C$ be the continuation aspect. The expression $D \Leftrightarrow_R C$ asserts:
  1. **Co-necessity:** The existence of a non-null $D$ is a necessary condition for the application of $C$. The application of $C$ is the only means by which $D$ can be modified.
  2. **Residue Conditioning:** The specific mapping between any given $D$ and the resulting $C$ is conditioned by the residue state $R$, which is itself the accumulated trace of prior $C$ events.
  3. **Inseparability:** $D$ and $C$ are not independent entities that interact. They are co-defining, inseparable aspects (projections) of a single underlying process transformation event.

## 3. Rejection of Ordinary Equivalence
The relation is **not** an equality. The "left side" (a state of being distinguishable) and the "right side" (an action of continuing) do not belong to the same formal space and cannot be equated. The expression defines their lawful, recursive relationship as the fundamental engine of all derived structures.

## Status Footer
- **Patch ID:** MPF-CORE-GUARD-026
- **Status:** SEMANTICS_DEFINED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
