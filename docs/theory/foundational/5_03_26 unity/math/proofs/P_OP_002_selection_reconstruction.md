# Proof Artifact: Selection Reconstruction Bounds Lemma

**Proof ID:** P_OP_002
**Lemma ID:** MT-OP-002
**Target:** Selection Reconstruction Bounds Lemma
**Classification:** LOCAL_LEMMA
**Status:** FORMAL_PROCEDURAL_ONLY

## 1. Lemma Statement
The underlying selection parameter (or aggregate causal input) $T_\alpha$ cannot be uniquely reconstructed from the observed continuation $X'_\alpha$ if the dimension of the null space of the projection operator $\Pi_{A_\alpha}$ is greater than zero ($dim(Ker(\Pi_{A_\alpha})) > 0$).

## 2. Formal Skeleton
* **Let** $X'_\alpha = X_\alpha + \Pi_{A_\alpha}(T_\alpha)$ be the observed continuation state.
* **Assume** the admissibility projection $\Pi_{A_\alpha}$ has a non-trivial null space, i.e., $\exists N \neq 0$ such that $\Pi_{A_\alpha}(N) = 0$.
* **Then** the preimage mapping under $\Pi_{A_\alpha}$ is not injective.
* **And** $T'_\alpha := T_\alpha + N$ produces an identical observed continuation $X'_\alpha$.

## 3. Structural Preservation Steps

**Step 001: Express continuation mapping.**
The observed continuation update is given by:
$$ \Delta X_\alpha = \Pi_{A_\alpha}(T_\alpha) $$

**Step 002: Introduce non-trivial null space element.**
Since the null space of the projection operator is non-trivial, let $N \in Ker(\Pi_{A_\alpha})$ be a non-zero vector. By definition of the null space:
$$ \Pi_{A_\alpha}(N) = 0 $$

**Step 003: Evaluate perturbed causal input.**
Let $T'_\alpha = T_\alpha + N$ be a perturbed causal input. Evaluating the continuation update under this input:
$$ \Delta X'_\alpha = \Pi_{A_\alpha}(T'_\alpha) = \Pi_{A_\alpha}(T_\alpha + N) $$

**Step 004: Apply linearity of projection mapping.**
Since the projection is linear over the local admissibility window:
$$ \Delta X'_\alpha = \Pi_{A_\alpha}(T_\alpha) + \Pi_{A_\alpha}(N) = \Pi_{A_\alpha}(T_\alpha) + 0 = \Delta X_\alpha $$

**Step 005: Conclude non-invertibility.**
The perturbed input $T'_\alpha$ yields the exact same observed continuation update as the original input $T_\alpha$. Thus, $T_\alpha$ cannot be uniquely reconstructed from $\Delta X_\alpha$, proving the non-invertibility of the projection mapping.

## 4. Required Failure Analysis
* **FAIL_RECON_001 (Circular reconstruction assumptions):** Assuming a unique preimage exists when the null space is non-trivial.
* **FAIL_RECON_002 (Null space violation):** Performing inverse operations that fail to account for the kernel of $\Pi_A$.
* **FAIL_RECON_003 (Information collapse):** Perturbing the system outside the admissibility window such that the projection erases all input signatures.

## 5. Conclusion
This lemma establishes the mathematical bounds of selection reconstruction, proving that the causal history is not uniquely recoverable from observed state continuations. The proof is restricted to FORMAL_PROCEDURAL_ONLY.
