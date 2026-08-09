# MT-LAW-A: Restricted-Domain Theorem Tightening (Patch 021)

## 1. Purpose
This document refines the operational parameters of **MT-LAW-A (Bounded Continuation Persistence)** to ensure that the theorem statement relies strictly on quantities that have been empirically and symbolically verified during the TS4 Hardening Series (Patches 001-020).

## 2. Validated Quantities for Theorem Construction
The following quantities have passed L3 verification across multiple mechanism classes (PDE and Stochastic) and are cleared for use in the TS4 theorem draft:

- **$S_{achieved}$ (Stability-Achieved):** Measured as the active fraction of identity persistence. Validated to be non-zero and stable under $s$-forcing.
- **$P_{stab}$ (Stabilization-Pressure):** The mismatch or forcing scalar. Validated to be necessary for $S_{achieved} > 0$.
- **$S_C$ (Cost-to-Destabilize):** Verified as a hard boundary (e.g., $s \approx 0.36$ in the 1D PDE).
- **$V(M_U)$ (Validity Window):** Verified as finite; persistence expands/drifts over long iteration limits ($t \approx 5000$).
- **$B_A$ (Admissibility Budget):** Validated implicitly through the global saturation avalanche when thresholds are exceeded.

## 3. Discarded or Downgraded Concepts
The following concepts have failed verification or demonstrated leakage during testing, and MUST NOT be used in the TS4 theorem:
- **"Infinite" or "Global" Stability:** Falsified by temporal window detection and global saturation modes.
- **Universal Recovery:** Falsified by the Orientation Locking boundary test ($\kappa=0.0, \sigma=1.0$).
- **Scalar Tipping Points:** Replaced by the "Threshold Surface" ($\Omega_S$) model mapped in Patch 012.

## 4. Tightened Statement Constraints
The impending theorem draft (Patch 029) must state that $S_{achieved}$ is sustained *only* within the interior of the Threshold Surface $\Omega_S$, and only for iterations $t \in V(M_U)$. Furthermore, the transition out of $\Omega_S$ must be characterized by the specific geometric transitions mapped in Patch 014 (Abrupt, Hysteresis, Saturation).

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS4-021
- **Deliverable ID:** docs/math/mt_law_a_theorem_tightening.md
- **Status:** TIGHTENING_COMPLETE
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
