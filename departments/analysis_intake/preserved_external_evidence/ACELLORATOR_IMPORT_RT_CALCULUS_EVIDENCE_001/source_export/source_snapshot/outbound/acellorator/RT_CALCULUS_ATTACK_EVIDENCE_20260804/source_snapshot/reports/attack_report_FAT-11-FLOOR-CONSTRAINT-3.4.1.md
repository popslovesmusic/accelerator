# Falsification Campaign Report: FAT-11-FLOOR-CONSTRAINT-3.4.1

## Executive Summary

- **Campaign ID:** `FAT-11-FLOOR-CONSTRAINT-3.4.1`
- **Target Concept:** Formal Block 3.4.1: The Floor Constraint (Epsilon Floor)
- **Date & Time of Run:** 2026-08-03 15:44:12 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the necessity of the floor constraint $D(S_1|S_2) \geq \epsilon$ where $\epsilon > 0$. The Mono-Process Framework asserts that an absolute zero distinction ($D = 0$) causes orientation vector calculations to experience mathematical singularities (such as division by zero) and degenerate states.

### Falsification Criteria
- We attempt to run the process simulation with $\epsilon = 0.0$ (ablated floor).
- We test two scenarios:
  1. **Test 1:** Converging toward a target state.
  2. **Test 2:** Starting at the target state (identity stability).
- If both scenarios complete successfully without crashes or NaN values, then the necessity of the floor constraint is falsified. If either scenario crashes or halts due to division by zero, the concept survived.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_11_floor_constraint_3_4_1.py`) simulating:
- A state value $S_t$ and target state $S_{\text{target}} = 5.0$.
- The distinction relation:
  $$ D(S_a \mid S_b) = \max(|S_a - S_b|, \epsilon) $$
- The orientation vector calculation:
  $$ O_t = \frac{S_t - S_{\text{target}}}{D(S_t \mid S_{\text{target}})} $$
- The update rule:
  $$ S_{t+1} = S_t - 0.1 \cdot O_t \cdot |S_t - S_{\text{target}}| $$
- We compare compliant ($\epsilon = 0.01$) vs. ablated ($\epsilon = 0.0$) runs.

---

## 3. Results & Findings

### Test 1: Converging toward target (Starting from $S_0 = 0.0$)
- **Compliant:** `SUCCESSFUL_STABILIZATION` (converged asymptotically without reaching target exactly).
- **Ablated:** `SUCCESSFUL_STABILIZATION` (converged asymptotically without reaching target exactly).
- **Finding:** Under asymptotic convergence, the state never matches the target exactly in finite steps, avoiding a $0/0$ division.

### Test 2: Starting at target (Identity stability, starting from $S_0 = 5.0$)
- **Compliant:** `SUCCESSFUL_STABILIZATION` (stabilized at $5.0$).
- **Ablated:** `ZERO_DISTINCTION_CRASH` (crashed on Step 0).
- **Finding:** Starting at the target state triggers total identity ($D = 0.0$). Under the ablated model, the orientation vector evaluation fails immediately due to a division-by-zero crash. The compliant model (with $\epsilon = 0.01$) safely evaluates the orientation as $0.0$, keeping the state stable.

---

## 4. Conclusion & Disposition

The concept of the **Floor Constraint (Epsilon Floor)** **survived** the attack. Without a positive floor constraint, when states achieve identity, the orientation vector becomes mathematically singular (division by zero), causing system collapse. This confirms that the floor constraint is strictly necessary to prevent orientation degeneracy.
