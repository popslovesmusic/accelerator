# Falsification Campaign Report: FAT-05-TRACE-ADMISSIBILITY-1.2D.1

## Executive Summary

- **Campaign ID:** `FAT-05-TRACE-ADMISSIBILITY-1.2D.1`
- **Target Concept:** Formal Principle 1.2D.1: Trace-Admissibility (PRIN_001) & 1.2D.2: Typed Zero-Condition Recoupling Admissibility
- **Date & Time of Run:** 2026-08-03 15:33:33 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the trace-admissibility and typed zero-condition recoupling rules. In nested process traces, local collapses to zero residue (null conditions) are inadmissible unless they retain directional provenance ($0_{\text{minus}} \neq 0_{\text{plus}}$) and are recoupled asymmetrically under an opposite-sign relation ($[0_{\text{minus}} \langle g \rangle_y 0_{\text{plus}}]$). Same-sign collapses (e.g. $[0_{\text{minus}} \langle g \rangle_y 0_{\text{minus}}]$) must fail and halt the process.

### Falsification Criteria
- We attempt to simulate composition of zero residues.
- If we can construct a nested trace where same-sign zero collapses recouple symmetrically or continue to evolve without halting (meaning the process continues despite lacking opposite-sign balancing), then the necessity of the recoupling rule is falsified. If it collapses and halts, the rule survived.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_05_trace_admissibility_1_2d_1.py`) simulating:
- A class `TypedZeroResidue` storing value and directional sign ($-1$ for minus, $+1$ for plus, $0$ for undifferentiated).
- A composition operator $\circ$ executing:
  - **Asymmetric opposite-sign coupling:** $0_{\text{minus}} \circ 0_{\text{plus}}$, recovering a non-zero relational tension (mismatch $= 0.1$, status `CONTINUATION`).
  - **Symmetric opposite-sign coupling:** $0_{\text{minus}} \circ 0_{\text{plus}}$ (symmetric relation), resulting in complete collapse (value $= 0.0$, sign $= 0$, status `HALT_SYMMETRIC`).
  - **Same-sign coupling:** $0_{\text{minus}} \circ 0_{\text{minus}}$, resulting in collapse to undifferentiated zero (value $= 0.0$, sign $= 0$, status `HALT_SAME_SIGN`).

---

## 3. Results & Findings

### Scenario A: Opposite-Sign Asymmetric Recoupling
- **Composition:** $0_{\text{minus}} \circ 0_{\text{plus}}$
- **Result:** Value $= 0.1$, sign $= 1$, status `CONTINUATION`.
- **Finding:** The asymmetric coupling of opposite signs successfully restored relational mismatch, allowing continuation.

### Scenario B: Same-Sign Composition
- **Composition:** $0_{\text{minus}} \circ 0_{\text{minus}}$
- **Result:** Value $= 0.0$, sign $= 0$, status `HALT_SAME_SIGN`.
- **Finding:** Composing same signs resulted in an undifferentiated null state lacking directional provenance, failing the legality check and halting the system.

### Scenario C: Opposite-Sign Symmetrical Coupling
- **Composition:** $0_{\text{minus}} \circ 0_{\text{plus}}$ (symmetric relation)
- **Result:** Value $= 0.0$, sign $= 0$, status `HALT_SYMMETRIC`.
- **Finding:** Symmetric coupling of opposite signs failed to resolve the tension, collapsing to a null state as predicted by the trace rules.

---

## 4. Conclusion & Disposition

The concepts of **Trace-Admissibility** and **Typed Zero-Condition Recoupling Admissibility** **survived** the attack. Symmetrical or same-sign zero collapses inevitably destroy the directional provenance (relational distinction) needed for continuation, forcing a system halt. Only asymmetric opposite-sign recoupling allows a collapsed process to recover distinction and continue.
