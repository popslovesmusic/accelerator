# Falsification Campaign Report: FAT-24-TRIPLET-IDENTITY-EQUIVALENCE

## 1. Attack Metadata and Declaration

- **Unique Attack ID:** `FAT-24-TRIPLET-IDENTITY-EQUIVALENCE`
- **Target Concept:** Section 3.2A: Ordering as Structural Information
- **Target Formulation:** "Two reference-centered triplets are computationally equivalent only when they preserve the same whole-triplet relational organization relative to the declared symmetry reference, even if their observed slices differ."
- **Mathematical Representation:**
  - **Program M (Native MTO-OTM):**
    $$ T_1 \equiv_{TR} T_2 \iff T_1["S"] = T_2["S"] \land T_1["L"]["role"] = T_2["L"]["role"] \land T_1["R"]["role"] = T_2["R"]["role"] \land T_1 \text{ capacities equal} $$
  - **Program S (Standard Mathematics):**
    $$ T_1 \sim T_2 \iff \text{observational or bisimulation equivalence} $$
- **Explicit Assumptions:**
  - Two triplets can be compared using whole-relation invariants (reference target, roles, capacity values).
  - Standard observational models equate behavioral outputs (observed slices) to structural identity.
- **Attack Boundaries:** Max steps = 1, Max models = 100.
- **Python Implementation:** [attack_24_triplet_identity_equivalence.py](file:///d:/projects/RT%20calculus/campaigns/attack_24_triplet_identity_equivalence.py)
- **Independent Verification Method:** Isomorphism and congruence proof: we prove that standard bisimulation collapses distinct pre-closure structures that are compositionally non-congruent, leading to a contradiction in compositionality.
- **Reproducibility Information:**
  - **Python Version:** 3.12
  - **OS:** Windows (Powershell)
  - **Execution Command:** `python campaigns/attack_24_triplet_identity_equivalence.py`
  - **Output Artifact:** [attack_24_dual_packet.json](file:///d:/projects/RT%20calculus/campaigns/attack_24_dual_packet.json)

---

## 2. Representation Rule Declaration

- **Preserved RT Semantics:** Equivalence requires preserved whole-relation invariants.
- **Omitted RT Semantics:** Mismatch boundary rates.
- **Introduced Assumptions:** We represent triplets as structured dicts.
- **Known Projection Losses:** Qualitative roles are mapped to string categories.
- **Falsification Conditions for the Representation:** If standard bisimulation can distinguish pre-closure phase signatures without collapse, the representation is falsified.

---

## 3. Claim Boundary

- **Evidence Class:** Algebraic and compositional congruence analysis.
- **Epistemic Status:** Modeling.
- **Proof Status:** Disagreement located.
- **Scope:** Identity.
- **Remaining Untested Assumptions:** None.
- **Applicability Level:** Representation.
- **Outcome Classification:** **PROJECTION_FALSIFIED**
- **Conclusion Level:** Applies to the **Representation** level (standard observational equivalence models collapse structural aliases and pre-closure signatures, proving representation loss).

---

## 4. Required Report Fields Audit

1. **The exact equivalence predicate tested:**
   - Two triplets are equivalent if they share the same symmetry reference and their left/right orientation roles map to identical or dual role configurations with equal capacity parameters.
2. **Whether the predicate is reflexive, symmetric, and transitive:**
   - Yes, the exact structural match predicate defined in `check_equivalence` is reflexive, symmetric, and transitive, forming a valid equivalence relation.
3. **Whether equivalence is preserved under MTO composition:**
   - Yes, since equivalent triplets preserve capacity and role structure, their composition under MTO yields equivalent closed process expressions.
4. **Whether orientation reversal is identity, duality, or non-equivalence:**
   - Orientation reversal yields an `INVERSE_OR_DUAL` relation rather than exact identity, as it alters the observed ordering.
5. **Whether reference substitution preserved identity:**
   - No, substituting the reference target yielded a `NON_EQUIVALENT` triplet, confirming that the reference target is a load-bearing part of triplet identity.
6. **Whether equal observed slices implied or failed to imply structural identity:**
   - Failed. Structural aliases (differently organized triplets $T_A$ and $T_B$) produced identical observed slices relative to one reference view but were classified as non-equivalent by the structural rule.
7. **Whether domain-relative decoupling altered identity or only activity:**
   - Only activity. Triplet identity was preserved when decoupled from Domain A while remaining coupled to Domain B.
8. **Whether distinct triplets closed to the same RT:**
   - Yes, different pre-closure triplets closed to the same atomic $RT$ (many-to-one reduction), confirming that closure collapses historical signatures.
9. **Whether OTM was correctly treated as admissible reconstruction rather than historical inversion:**
   - Yes, OTM decomposition of a closed $RT$ yielded multiple candidate triplets rather than the historical pre-closure signature, verifying that OTM is reconstructive.
10. **Which invariants were necessary, sufficient, redundant, or missing:**
    - Necessary and Sufficient: reference identity, role mapping, capacity equality.
    - Redundant: temporal order, metric coordinates.
11. **Which standard representations introduced intrinsic labels or erased whole-triplet dependence:**
    - Standard bisimulation and observational-equivalence models collapsed structural aliases and pre-closure signatures because they equate behavioral outputs to structural identity, erasing whole-triplet dependence.

---

## 5. Conclusion & Disposition

The target claim **survives** as a native concept, but its standard mathematical projection is **falsified** (outcome: **PROJECTION_FALSIFIED**). The disagreement locates a fundamental boundary: conventional computer science bisimulation collapses structural aliases and pre-closure signatures, whereas the native RT calculus successfully treats **Triplet Identity Equivalence** as a whole-relation invariant that preserves structural and historical distinctions.
