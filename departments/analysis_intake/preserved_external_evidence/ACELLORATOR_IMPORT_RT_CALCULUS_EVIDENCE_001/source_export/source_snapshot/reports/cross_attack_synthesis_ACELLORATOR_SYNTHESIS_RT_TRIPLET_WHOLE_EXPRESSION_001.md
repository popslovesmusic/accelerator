# Cross-Attack Synthesis Report: ACELLORATOR_SYNTHESIS_RT_TRIPLET_WHOLE_EXPRESSION_001

## 1. Synthesis Metadata and Declaration

- **Unique Synthesis ID:** `ACELLORATOR_SYNTHESIS_RT_TRIPLET_WHOLE_EXPRESSION_001`
- **Source Bundle:** `RT_CALCULUS_ATTACK_EVIDENCE_20260804`
- **Source Attacks:**
  - [FAT-23-REFERENCE-CENTERED-ORDERED-RELATION](file:///d:/projects/RT%20calculus/reports/attack_report_FAT-23-REFERENCE-CENTERED-ORDERED-RELATION.md)
  - [FAT-24-TRIPLET-IDENTITY-EQUIVALENCE](file:///d:/projects/RT%20calculus/reports/attack_report_FAT-24-TRIPLET-IDENTITY-EQUIVALENCE.md)
  - [FAT-25-INVARIANT-MINIMALITY](file:///d:/projects/RT%20calculus/reports/attack_report_FAT-25-INVARIANT-MINIMALITY.md)
  - [FAT-26-INVARIANT-DEPENDENCY-GRAPH](file:///d:/projects/RT%20calculus/reports/attack_report_FAT-26-INVARIANT-DEPENDENCY-GRAPH.md)
- **Active Claim Classification Level:** `C2_INTERNAL_STRUCTURAL_SYNTHESIS`
- **Epistemic Status:** `PROVISIONAL`
- **Proof Status:** `NOT_PROVED`
- **Promotion Status:** `HOLD`
- **Disposition:** `PROVISIONAL_SYNTHESIS_READY_FOR_REVIEW`

---

## 2. Synthesis Claim

Under the tested native formulation, the reference-centered triplet is the current minimum whole-expression computational relation. Its symmetry reference, orientation roles, and distinction capacity are independently nameable under OTM decomposition but are not independently realizable within the tested computational domain.

---

## 3. Supporting Findings and Evidence

- **FAT-23:** Reference ablation, orientation ablation, and binary reduction each destroy the tested whole-triplet semantics.
- **FAT-24:** Observed-slice equality and closure equality do not establish pre-closure triplet identity.
- **FAT-25:** Symmetry reference, orientation roles, and distinction capacity form the current candidate identity basis under the tested perturbations.
- **FAT-26:** The candidate basis elements are OTM-exposed aspects of a mutually conditioned whole-expression relation rather than independent native primitives.

---

## 4. Limitations and Boundaries

1. Program M and Program S remain separate implementations within the same research program, not independent external verification.
2. The uniqueness of the claimed whole-expression primitive has not been established beyond the tested constructions.
3. The completeness and multiplicity of OTM decompositions remain untested.
4. The standard-mathematics comparisons remain representation-bounded.
5. Historical execution provenance and replay coverage remain incomplete.

---

## 5. Generated Attack Obligations

| Obligation ID | Title | Question | Status |
| :--- | :--- | :--- | :--- |
| **OBL-RT-OTM-001** | OTM completeness | Does OTM generate all lawful decompositions or only a reference-conditioned admissible subset? | **REGISTERED** |
| **OBL-RT-OTM-002** | OTM multiplicity | Can one closed RT admit multiple non-equivalent lawful decomposition families while preserving identity capacity? | **REGISTERED** |
| **OBL-RT-OTM-003** | OTM reachability | Are some lawful decompositions unreachable under the current OTM procedure? | **REGISTERED** |
| **OBL-RT-MTO-001** | MTO closure equivalence | What exact relation determines when different pre-closure organizations collapse to the same atomic RT? | **REGISTERED** |
| **OBL-RT-TRIPLET-001** | Whole-expression uniqueness | Can a simpler native relation reproduce all tested triplet behavior without hidden reintroduction of reference, orientation, or distinction capacity? | **REGISTERED** |

---

## 6. Recommended Next Attack

- **Attack ID:** `FAT-27-OTM-COMPLETENESS-MULTIPLICITY`
- **Rationale:** FAT-26 places OTM at the exact boundary between the closed whole-expression primitive and its exposed aspects. The next unresolved question is whether OTM exposes one admissible decomposition, all lawful decompositions, or only a bounded reachable subset.
