# MT-LAW-A: Accessibility Geometry and Deformation (Patch 033)

## 1. Purpose
This document models the **Accessibility Geometry** of local continuation processes, specifically how the "reach" of admissible future states deforms under external perturbation and internal resource depletion (admissibility budget stress).

## 2. Reachability Manifold ($\mathcal{A}_R$)
For any process index $\alpha$, the **Reachability Manifold** is the set of all candidate states $\vec{x}'$ that satisfy local admissibility $\Pi_A$ given the current residue $R_t$.
$$ \mathcal{A}_R(\alpha) = \{ \vec{x}' \in X \mid \Pi_A(\vec{x}' \mid R_t) \ne \emptyset \} $$

## 3. Admissibility-Induced Deformation

The volume and shape of $\mathcal{A}_R$ are not static. They are subject to **Geometric Deformation** based on two primary factors:

### 3.1 Budget-Induced Contraction
As the local admissibility budget $B_A$ (LAW021) is consumed to maintain $P_{stab}$ or damp $P_\Delta$, the Reachability Manifold **contracts**.
- **Pinching Effect:** Continuation paths that were previously wide and robust become narrowed into restricted "corridors."
- **Collapse Limit:** When $B_A \to 0$, the manifold volume vanishes, leading to **Orientation Locking** (CE-A002).

### 3.2 Perturbation-Induced Shearing
Adversarial perturbations $|P_\Delta|$ (LAW022) exert a **Shearing Force** on the manifold, distorting the alignment of the orientation array.
- **Orientation Drift:** The manifold tilts, shifting the "optimal" continuation geodesic toward the basin ridge.
- **Fracture Risk:** High shear leads to topological tearing of the manifold (Fracture Surface $\mathcal{F}$).

## 4. Geometric Tensors of Accessibility
To formally measure these effects, we declare the following conceptual tensors:
- **Accessibility Metric ($g_{acc}$):** Encodes the local cost of continuation in any given orientation.
- **Budget Curvature Tensor ($\mathcal{K}_B$):** Measures the rate of manifold contraction with respect to budget depletion.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-033
- **Deliverable ID:** docs/math/mt_law_a_accessibility_geometry.md
- **Status:** ACCESSIBILITY_MODELED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
