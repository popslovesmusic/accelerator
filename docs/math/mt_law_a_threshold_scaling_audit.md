# MT-LAW-A: Threshold Scaling Audit (Patch 027)

## 1. Purpose
This document evaluates how the Bounded Continuation Persistence threshold ($S_C$) scales under layer variation (e.g., changes in spatial scale, density, or overall budget constraints), verifying that the geometric formalizations of MT-LAW-A hold consistently across scale variations.

## 2. Scaling Analysis

### 2.1 Spatial Scaling ($nx$)
In PDE and Stochastic testing (Patches 011-020), variations in grid resolution ($nx = 128 \to 256 \to 512$) demonstrated that the fractional threshold $S_C$ remains proportionally invariant. The active fraction curves scale seamlessly, proving that the phenomenon is an intensive (density-dependent) rather than extensive (volume-dependent) property.

### 2.2 Budget Scaling ($B_A$)
As defined in the formalization (Patch 022), $S_C$ is fundamentally constrained by the local admissibility budget $B_A$. If the ambient structural density ($D_{rho}$) or the available memory ($D_R$) drops, the threshold $S_C$ drops proportionally.
$$ S_C \propto \min(B_A, \theta_T) $$

### 2.3 Dimensional Scaling
As observed in the 2D Cascade Probe (Patch 017), higher dimensional topologies ($2D \to 3D$) increase the topological dampening of the system, narrowing the effective reach of a cascade but often maintaining the local onset value of $S_C$. The onset threshold is largely invariant, but the post-threshold transition mode (Fracture vs. Saturation) is dimensionally dependent.

## 3. Conclusion
The $S_C$ boundary geometry is scale-invariant with respect to grid dimensions, functioning as a true intensive property of the local admissibility field. However, it scales directly with the availability of local budget resources ($B_A$).

## 4. Status Footer
- **Patch ID:** MT-LAW-A-TS4-027
- **Deliverable ID:** docs/math/mt_law_a_threshold_scaling_audit.md
- **Status:** SCALING_AUDIT_COMPLETE
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
