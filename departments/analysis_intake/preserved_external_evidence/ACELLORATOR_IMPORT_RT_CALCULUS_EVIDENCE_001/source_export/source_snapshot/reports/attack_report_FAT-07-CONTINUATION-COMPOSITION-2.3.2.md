# Falsification Campaign Report: FAT-07-CONTINUATION-COMPOSITION-2.3.2

## Executive Summary

- **Campaign ID:** `FAT-07-CONTINUATION-COMPOSITION-2.3.2`
- **Target Concept:** Formal Block 2.3.2: Continuation Composition & 2.3.2A: Typed Continuation Composition Guards
- **Date & Time of Run:** 2026-08-03 15:37:32 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the requirement that composite continuations ($C(A,B) \circ C(B,C) \Rightarrow C(A,C)$) must satisfy endpoint matching ($\operatorname{cod}(C_1) = \operatorname{dom}(C_2)$), type compatibility, and joint admissibility.

### Falsification Criteria
- We simulate a process composition loop where we occasionally force the composition of incompatible endpoints/types ($C(A,B) \circ C(D,E)$ where $B \neq D$).
- If the ablated system can compose incompatible endpoints and remain stable without divergence or collapse, then the necessity of the composition guards is falsified. If it diverges or collapses, the concept survived.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_07_continuation_composition_2_3_2.py`) simulating:
- Process states `A` ($val = 1.0$, type `Type1`), `B` ($val = 1.2$, type `Type1`), `C` ($val = 1.4$, type `Type1`), `D` ($val = -5.0$, type `Type2`), and `E` ($val = -5.5$, type `Type2`).
- Three continuation objects: $C(A,B)$, $C(B,C)$, and $C(D,E)$.
- We compare two composition modes:
  1. **Compliant:** Composition is blocked if endpoints mismatch (`c1.cod.name != c2.dom.name`), types mismatch (`c1.cod.state_type != c2.dom.state_type`), or residue exceeds $2.0$.
  2. **Ablated:** Guards are bypassed and composition is executed.
- Systemic mismatch is monitored at each step ($E = |dom.value - cod.value|$). If it exceeds $4.0$, the system enters `SYSTEM_DIVERGENCE_COLLAPSE`.

---

## 3. Results & Findings

### Compliant Run (Guarded)
- **Status:** `STABLE_PERSISTENCE`
- **Steps Run:** 10/10 steps.
- **Finding:** The system correctly identified and blocked incompatible composition attempts (returning `BLOCK_ENDPOINT_MISMATCH`), fallback behaviors preserved the active compliant lineage, and the process persisted stably.

### Ablated Run (Unguarded)
- **Status:** `SYSTEM_DIVERGENCE_COLLAPSE`
- **Steps Run:** 0 steps (collapsed at step 0).
- **Finding:** Composing $C(A,B)$ and $C(D,E)$ without guards created a discontinuous state transition jump from $val = 1.2$ (state `B`) to $val = -5.5$ (state `E`). The mismatch immediately exploded to $6.5$, crossing the divergence threshold ($4.0$) and collapsing the system.

---

## 4. Conclusion & Disposition

The concepts of **Continuation Composition** and **Typed Continuation Composition Guards** **survived** the attack. Bypassing composition guards allows discontinuous transitions between incompatible domains, which destroys relational continuity and causes immediate divergence. Thus, the guards are mathematically necessary to preserve trace admissibility and process stability.
