# Falsification Campaign Report: FAT-11-FLOOR-CONSTRAINT-DS

## Executive Summary

- **Campaign ID:** `FAT-11-FLOOR-CONSTRAINT-DS`
- **Target Concept:** Formal Block 3.4.1: The Floor Constraint
- **Date & Time of Run:** 2026-08-03 15:56:34 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Falsified**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the fundamental necessity of the floor constraint ($D \ge \epsilon > 0$) using **Dynamical Systems Theory**. The framework claims that the floor constraint is essential to prevent division-by-zero singularities when the state converges to the target.

### Falsification Vector
We compare:
1. **RT Floor Formulation:** Uses a division-by-distance update rule with a hard discontinuous floor constraint ($D = \max(|S|, \epsilon)$).
2. **Standard Continuous Gradient Descent:** Formulates the update using standard dynamical systems gradient descent where updates scale with the distance, eliminating the singularity at zero.
- If standard gradient descent converges smoothly to the attractor without any floor constraint or singularity, the necessity of the floor constraint is falsified.

---

## 2. Simulation Results

- **Standard Continuous Gradient Descent:** Converged smoothly and asymptotically to $0.0$ (final values: $[0.0078, 0.0071, 0.0064, 0.0057, 0.0052]$) without requiring any epsilon floor or encountering coordinate singularities.
- **RT Floor Formulation:** Encountered high-frequency chattering and boundary oscillations near the attractor ($9$ sign changes in the final $10$ steps).

---

## 3. Conclusion & Disposition

The concept of the **Floor Constraint** is **falsified**. Standard dynamical systems theory shows that the coordinate singularity at $S_{\text{target}}$ is an artifact of the framework's division-by-distance coordinate projection choice. A standard continuous gradient formulation avoids the singularity entirely and converges smoothly without any floor constraint.
