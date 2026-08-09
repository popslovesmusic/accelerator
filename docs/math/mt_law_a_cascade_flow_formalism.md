# MT-LAW-A: Cascade Flow Formalism (Patch 045)

## 1. Purpose
This document formalizes the **Cascade Flow** ($\Phi_{cas}$) as a governed dynamic process within **MT-LAW-A**. It represents sequential destabilization as a directed flow over coupled local regions, enabling the predictive modeling of large-scale avalanches.

## 2. Cascade Flow ($\Phi_{cas}$)
Cascade flow is the time-ordered sequence of threshold crossings in a coupled orientation graph.

### 2.1 The Propagation Geodesic
The flow follows the **Propagation Geodesic**, which is the path of minimum local Cost-to-Destabilize ($S_C$) through the regional structure.
- **Rule:** Destabilization flows toward regions where budget headroom $(B_A - Cost_A)$ is lowest.

### 2.2 Continuity Equation
The conservation of mismatch across a cascade is described by the **Continuity Equation for Cascade Flow**:
$$ \frac{\partial \Phi_{cas}}{\partial t} + \nabla \cdot (\Phi_{cas} \otimes NavT) = \text{Source} - \text{Dampening} $$
- **Source:** Local basin collapse (mismatch injection).
- **Dampening:** Topological friction and budget-mediated damping (LAW022).

## 3. Propagation Regimes

### 3.1 Sub-Critical Flow
Dampening exceeds Source. The cascade is **Local** and terminates rapidly within the source neighborhood.

### 3.2 Super-Critical Flow
Source exceeds Dampening. The cascade expands into a **Global Avalanche**, consuming all available budget until the entire local domain saturates.

## 4. Formal Metric: Cascade Velocity ($v_{cas}$)
The rate of expansion of the fracture front through the orientation array.
$$ v_{cas} \propto \frac{|NavT| - S_C}{B_A} $$

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-045
- **Deliverable ID:** docs/math/mt_law_a_cascade_flow_formalism.md
- **Status:** FLOW_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
