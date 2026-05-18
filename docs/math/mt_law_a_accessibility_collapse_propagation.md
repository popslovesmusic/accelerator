# MT-LAW-A: Accessibility Collapse Propagation (Patch 046)

## 1. Purpose
This document formalizes the **Propagation of Accessibility Collapse** within the orientation field of **MT-LAW-A**. It models how the localized "pinching" or "shearing" of reachability manifolds spreads through regional budget depletion, formalizing the **Accessibility Collapse Wave**.

## 2. Accessibility Collapse Wave ($\mathcal{W}_A$)
The collapse wave is the propagating spatial boundary where the Reachability Manifold volume falls to zero ($Vol(\mathcal{A}_R) \to 0$).

### 2.1 Propagation Mechanism
The wave propagates through the consumption of regional budget. When a cluster of processes collapses, the resulting high-mismatch state requires massive regional damping. This "budget drain" starves adjacent processes of the resource required to maintain their own reachability volumes.
- **Wave Speed ($v_{wave}$):** Proportionate to the mismatch injection rate and inversely proportionate to the regional budget density.

### 2.2 Geometric Pinching
As the wave approaches process $\beta$, its manifold $\mathcal{A}_R(\beta)$ undergoes **Accelerated Pinching**.
- **Signature:** The number of admissible future geodesics falls rapidly, converging to a single locked orientation (Orientation Locking).

## 3. Topologically Non-Admissible Regions (TNAR)
The region "behind" the collapse wave is classified as a **Topologically Non-Admissible Region**.
- **State:** Orientation locking, zero reachability, and loss of identity continuity.
- **Reconstructibility:** TNARs coincide with the **Reconstruction Shadow** ($\mathcal{S}_R$), where information loss is absolute.

## 4. Constraint: Non-Global Propagation
The MT-LAW-A framework requires that all collapse wave claims define the **Containment Boundary** ($B_{cont}$), where regional budget replenishment or topological dampening halts the expansion. Universal accessibility collapse is a prohibited claim.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-046
- **Deliverable ID:** docs/math/mt_law_a_accessibility_collapse_propagation.md
- **Status:** WAVE_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
