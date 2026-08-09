# MT-LAW-A: Threshold Surface Formalization (Patch 022)

## 1. Purpose
This document converts the empirically observed destabilization regions (from Patch 012) into a governed mathematical structure: the **Cost-to-Destabilize Surface ($\Omega_S$)**.

## 2. Formalization of $\Omega_S$

Rather than treating the tipping point $S_C$ as a single scalar, the Cost-to-Destabilize is formalized as a bounded sub-manifold within the parameter space of the local restricted domain $U$.

Let $U$ be parameterized by a state vector $\vec{x}$, forcing pressure $P_{stab}$, and local coupling $\kappa$.

The **Admissible Interior** (the region where $S_{achieved} > 0$) is defined by:
$$ \Omega_S = \{ (P_{stab}, \kappa, B_A) \in U \mid P_{stab} < S_C(\kappa, B_A) \text{ and } P_{stab} > 0 \} $$

### 2.1 The Saturation Boundary ($\partial \Omega_{sat}$)
The upper boundary of $\Omega_S$ is the saturation limit, where forcing exceeds the local budget's damping capacity. Crossing this boundary triggers the **Global Saturation Avalanche** (TRANS-SATURATION-003).
$$ \partial \Omega_{sat} = \{ (P_{stab}, \kappa, B_A) \mid P_{stab} = S_C(\kappa, B_A) \} $$

### 2.2 The Extinction Boundary ($\partial \Omega_{ext}$)
The lower boundary occurs when forcing drops below the threshold required to maintain the channel against ambient residue decay.
$$ \partial \Omega_{ext} = \{ (P_{stab}, \kappa, B_A) \mid P_{stab} = 0 \} $$

## 3. Surface Curvature and Dimensionality
As demonstrated in Patch 018, the curvature of $\partial \Omega_{sat}$ is mechanism-dependent:
- In 1D PDE, the boundary is relatively flat with respect to $\kappa$ (zero curvature).
- In Stochastic models, the boundary is highly sensitive to noise $\sigma$.
Therefore, the general theorem must abstract the boundary geometry to $\partial \Omega_S$, avoiding mechanism-specific dimensional claims.

## 4. Status Footer
- **Patch ID:** MT-LAW-A-TS4-022
- **Deliverable ID:** docs/math/mt_law_a_threshold_surface_formalization.md
- **Status:** SURFACE_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
