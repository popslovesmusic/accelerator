# Proof Artifact: O_calculus Partial Composition Lemma

**Proof ID:** P_O_CALC_001
**Lemma ID:** MT-O-CALC-001
**Target:** O_calculus Partial Composition Lemma
**Classification:** LOCAL_LEMMA
**Status:** FORMAL_PROCEDURAL_ONLY

## 1. Lemma Statement
Orientation transformations compose lawfully iff they preserve typed admissible continuation and closure class.

## 2. Formal Skeleton
* **Let** $O_a, O_b \in \mathcal{O}$ be typed orientation transformations over a lawful operand $X \in RT \cup aRT$.
* **Assume** $O_a(X)$ is defined and preserves distinction, admissibility, and closure class for $X$.
* **Assume** $O_b$ accepts the output orientation class of $O_a(X)$ as an admissible input class over the same typed operand.
* **Assume** the chained action does not trigger any declared failure condition `FAIL_O_001` through `FAIL_O_006`.
* **Then** $O_b \circ O_a$ is a lawful partial composition in $O_{calculus}$.
* **Conversely,** if typed admissible continuation or closure-class preservation fails, the composition is not lawful in the calculus.

## 3. Structural Preservation Steps

**Step 001: Expand the typing rule for orientation transformations.**
A lawful element of $\mathcal{O}$ is not a free-standing motion primitive. It is a typed admissible retuning over a declared operand $X$ such that distinction support, admissibility, and closure class remain defined.

**Step 002: Expand partial composition.**
The expression $O_b \circ O_a$ is partial by construction. It is defined only when the output orientation class of $O_a$ is an admissible input class for $O_b$ over the declared typed operand.

**Step 003: Show typed admissible continuation is necessary.**
If $O_a(X)$ does not preserve typed admissible continuation, then the chained state lacks a lawful continuation target for $O_b$. This triggers `FAIL_O_004` or `FAIL_O_005`, so the composition is undefined.

**Step 004: Show closure-class preservation is necessary.**
If $O_a(X)$ destroys or changes closure support outside the declared admissible class, then $O_b$ no longer acts on the same lawful closure regime. This triggers `FAIL_O_003` or `FAIL_O_006`, so the composition is undefined.

**Step 005: Show distinction preservation remains a firewall.**
Even if operand typing is declared, the composition cannot proceed when distinction collapses below the operative floor $\epsilon$. This is exactly `FAIL_O_002`, blocking any lawful chaining.

**Step 006: Show the positive direction.**
When $O_a(X)$ preserves typed admissible continuation, distinction support, and closure class, and when $O_b$ is typed for that resulting orientation class, the chained action remains inside the declared admissible orientation space. No failure condition is triggered, so $O_b \circ O_a$ is lawful as a partial composition.

**Step 007: Show the converse direction.**
Assume $O_b \circ O_a$ is lawful. Then by the definition of lawful membership in $\mathcal{O}$ and by the partiality rule, the intermediate state produced by $O_a$ must still be typed, admissible, and closure-supported for $O_b$ to act on it. Therefore lawful composition implies preservation of typed admissible continuation and closure class.

## 4. Required Failure Analysis
* **FAIL_O_001 (orientation degeneracy):** No determinate admissible orientation class can be selected, so composition cannot be typed.
* **FAIL_O_002 (distinction collapse):** The operative distinction floor is violated; chaining is blocked.
* **FAIL_O_003 (closure support fails):** The intermediate state loses lawful closure support, so the next map has no admissible target.
* **FAIL_O_004 (operand typing fails):** At least one action is untyped over the declared operand; the composition is undefined.
* **FAIL_O_005 (admissible continuation set empty):** No lawful successor orientation remains; the chain terminates.
* **FAIL_O_006 (incompatible orientation classes):** The codomain class of $O_a$ is not an admissible domain for $O_b$.

## 5. Conclusion
This artifact establishes the minimum local rule for lawful partial composition in $O_{calculus}$. It confines the result to typed admissible chaining over RT/aRT operands and blocks any reading of orientation composition as a free, globally closed algebra. The claim remains restricted to FORMAL_PROCEDURAL_ONLY.
