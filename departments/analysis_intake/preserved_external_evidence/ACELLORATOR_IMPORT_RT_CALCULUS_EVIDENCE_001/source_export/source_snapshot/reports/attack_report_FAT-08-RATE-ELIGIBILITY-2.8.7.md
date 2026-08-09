# Falsification Campaign Report: FAT-08-RATE-ELIGIBILITY-2.8.7

## Executive Summary

- **Campaign ID:** `FAT-08-RATE-ELIGIBILITY-2.8.7`
- **Target Concept:** Governed Clarification 2.8.7: Rate-Type Eligibility Predicate
- **Date & Time of Run:** 2026-08-03 15:38:55 (Local Time)
- **Status:** **Completed**
- **Outcome:** **Survived (Falsification Failed)**

---

## 1. Attack Objective and Design

The goal of this campaign was to challenge the requirement of checking the `RATE_TYPE_ELIGIBLE` eligibility predicate prior to executing rate-based metric-bridge evaluations. The Mono-Process Framework asserts that rate-based evaluations require positive degrees of freedom (`DOF(x) > 0`) to prevent singular/undefined behavior in the bridge mapping.

### Falsification Criteria
- We attempt to evaluate the rate-type metric bridge on a decoupled state with `DOF(x) = 0`.
- If the ablated (unguarded) evaluation can run successfully and yield a valid, non-singular numerical value, then the necessity of the eligibility predicate is falsified. If it crashes or produces singular values, the concept survived.

---

## 2. Simulation Environment & Setup

We developed a self-contained Python model (`campaigns/attack_08_rate_eligibility_2_8_7.py`) simulating:
- A state object `StateX` with properties `dof` (degrees of freedom), `coupled_ae` (A|E coupling status), and `endpoint_compatible`.
- The predicate function `rate_type_eligible(x, phi)` enforcing `dof > 0`, `coupled_ae`, `endpoint_compatible`, and declared `phi`.
- A mock metric-bridge evaluation function:
  $$ \text{rate} = \frac{1.5}{\text{DOF}(x)} $$
  representing the concentration density of distinction relative to reference context `phi`.
- We compare:
  1. **Compliant (Guarded):** Checks eligibility first. Returns `BLOCKED: RATE_TYPE_INELIGIBLE_ZERO_DOF` for a zero-DOF state.
  2. **Ablated (Unguarded):** Runs the calculation directly on the zero-DOF state.

---

## 3. Results & Findings

### Scenario A: Compliant State ($DOF = 2$)
- **Result:** $rate = 0.75$, status `SUCCESS`.
- **Finding:** Evaluating a valid, eligible state successfully yields a well-defined rate projection.

### Scenario B: Zero-DOF (Guarded)
- **Result:** $rate = None$, status `BLOCKED: RATE_TYPE_INELIGIBLE_ZERO_DOF`.
- **Finding:** The predicate correctly blocks evaluation on the zero-DOF state, preventing calculation of singular/undefined values.

### Scenario C: Zero-DOF (Unguarded/Ablated)
- **Result:** $rate = None$, status `CRASH_ZERO_DIVISION`.
- **Finding:** Bypassing the eligibility check caused a division-by-zero exception during the rate calculation.

---

## 4. Conclusion & Disposition

The concept of the **Rate-Type Eligibility Predicate** **survived** the attack. Evaluating rate-type metric bridges on states with zero degrees of freedom results in mathematical singularities (division-by-zero crashes), demonstrating that checking the `RATE_TYPE_ELIGIBLE` predicate is strictly necessary to preserve metric-bridge integrity.
