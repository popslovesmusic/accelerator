# Falsification Campaign Report: FAT-02-TRACE-PRIORITY-1.2.6

## Executive Summary

- **Campaign ID:** `FAT-02-TRACE-PRIORITY-1.2.6`
- **Target Concept:** Formal Principle 1.2.6: Trace Priority Over Projection: $P(H_1) = P(H_2) \not\implies H_1 = H_2$
- **Date & Time of Run:** 2026-08-03 15:27:55 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the principle of **Trace Priority Over Projection**, which asserts that process identity is defined by its trace history ($H$) rather than its surface observable projections ($P$). 

### Falsification Criteria
- Can we construct a projection mapping $P$ that is strictly injective (meaning $P(H_1) = P(H_2) \implies H_1 = H_2$) in a realistic RT operational regime? 
- If such a mapping exists, then the history $H$ is completely redundant since process identity can be determined uniquely from final-state projections. This would falsify the trace-prior claim.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_02_trace_priority_1_2_6.py`) evaluating two scenarios:
1. **Test Case 1: Simple Linear Accumulation System**
   - History $H = [s_0, s_1]$.
   - Residue accumulates state values: $R_1 = s_0 + s_1$.
   - Projection is $P(H) = (s_1, R_1)$.
2. **Test Case 2: RT Nonlinear Admissibility System**
   - History $H = [s_0, s_1, s_2]$.
   - Residue accumulates state updates only when changes exceed a threshold $\epsilon = 0.5$:
     $R_t = R_{t-1} + |s_t - s_{t-1}|$ if $|s_t - s_{t-1}| > \epsilon$ else $R_{t-1}$.
   - Projection is $P(H) = (s_2, R_2)$.

---

## 3. Results & Findings

### Test Case 1: Simple Linear Accumulation
- **Histories:** $H_1 = [1.0, 2.0]$ and $H_2 = [1.5, 2.0]$
- **Projections:** $P(H_1) = (2.0, 3.0)$ and $P(H_2) = (2.0, 3.5)$
- **Reconstruction:** We successfully reconstructed $s_0 = R_1 - s_1$. For $H_1$, $s_0 = 3.0 - 2.0 = 1.0$. For $H_2$, $s_0 = 3.5 - 2.0 = 1.5$.
- **Finding:** Under a simple linear memory regime, final projections are injective, making history reconstructible from the projection. This represents a localized counterexample.

### Test Case 2: RT Nonlinear Admissibility System
- **Histories:** $H_1 = [1.0, 1.3, 2.0]$ and $H_2 = [1.2, 1.3, 2.0]$
- **Projections:**
  - $H_1$: Step 1 diff = $0.3 < 0.5$ (ignored); Step 2 diff = $0.7 > 0.5$ (added). $P(H_1) = (2.0, 0.7)$.
  - $H_2$: Step 1 diff = $0.1 < 0.5$ (ignored); Step 2 diff = $0.7 > 0.5$ (added). $P(H_2) = (2.0, 0.7)$.
- **Finding:** A projection collision was successfully demonstrated. Both histories resulted in identical final observables and residues $P(H_1) = P(H_2) = (2.0, 0.7)$, yet the historical paths were distinct ($[1.0, 1.3, 2.0] \neq [1.2, 1.3, 2.0]$).

---

## 4. Conclusion & Disposition

The principle of **Trace Priority Over Projection** **survived** the attack. Although highly simplified linear architectures can allow historical reconstruction, any realistic RT regime with non-linear admissibility gating is non-injective. Multiple distinct process histories can produce identical macroscopic projections, meaning truth and process identity are indeed trace-prior.
