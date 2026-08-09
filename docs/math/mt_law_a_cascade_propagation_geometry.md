# MT-LAW-A: Cascade Propagation Geometry (Patch 035)

## 1. Purpose
This document maps the geometric structure of **Cascade Propagation** in the Mono-Process Framework. It defines how a local destabilization event (crossing $S_C$) triggers sequential failures across adjacent or coupled continuation structures, formalizing the **Avalanche** transition mode.

## 2. The Propagation Field ($\Phi_C$)
Cascade propagation is modeled as the expansion of a **Destabilization Wave** through the local orientation array.

### 2.1 Coupling-Mediated Propagation
Destabilization propagates through the **Transport Operator** (NavT). When process $\alpha$ collapses, the sudden change in its state vector $\vec{x}_\alpha$ injects a high-mismatch "pulse" into its coupled neighbors $\beta \in CSI(\alpha)$.
- **Critical Condition:** If $|NavT(\alpha \to \beta)| > S_C(\beta)$, process $\beta$ also collapses.

### 2.2 Budget-Mediated Propagation
Avalanches can also propagate through shared budget resources. If multiple processes consume the local admissibility budget $B_A$ to damp a common perturbation, the exhaustion of $B_A$ triggers a simultaneous failure across the entire regional cluster.

## 3. Geometric Signatures of Cascade

### 3.1 Propagation Topology
The topology of a cascade is characterized by the **Graph of Sequential Crossings**.
- **Linear Cascades:** Sequential failure along a 1D corridor.
- **Radial Avalanches:** Spherical expansion from a central point of failure.

### 3.2 Dimensional Dampening
As observed in Patch 017, higher-dimensional topologies ($2D/3D$) exhibit **Geometric Dampening**, where the surface area of the propagation wave grows faster than the injected energy, often halting the cascade before it consumes the entire domain.

## 4. Formalization of Cascade Limits
The MT-LAW-A framework requires that all cascade claims specify the **Propagation Reach** ($R_{prop}$), defined as the topological distance at which the destabilization pulse falls below the local $S_C$ threshold of the neighbors.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-035
- **Deliverable ID:** docs/math/mt_law_a_cascade_propagation_geometry.md
- **Status:** PROPAGATION_MAPPED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
