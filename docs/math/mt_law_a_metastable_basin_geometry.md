# MT-LAW-A: Metastable Basin Geometry Framework (Patch 032)

## 1. Purpose
This document formalizes the geometric structure of **Metastable Basins** in the Mono-Process Framework, providing a rigorous spatial model for the Bounded Continuation Persistence lemma. It defines the features of the admissibility landscape that govern structural stability and regime transitions.

## 2. The Admissibility Landscape ($\mathcal{L}_A$)
The persistence of a continuation channel is modeled as a trajectory within an **Admissibility Landscape**, where "height" corresponds to the local mismatch ($\epsilon$) or the distance to the nearest exclusion boundary.

### 2.1 Metastable Basin ($B_M$)
A **Metastable Basin** is a connected region of the landscape where $S_{achieved} \approx 1$ and the local gradient of mismatch $(\nabla \epsilon)$ points toward a stable fixed-point or cycle.
- **Persistence Zone:** The interior of the basin where perturbations are damped (LAW022).

### 2.2 Transition Ridge ($\mathcal{R}_T$)
The ridge is the boundary separating two adjacent basins ($B_M, B_V$). It represents the local maximum of continuation cost.
- ** ridge height:** Operationally equivalent to the Cost-to-Destabilize $S_C$.
- **Crossing Rule:** A transition occurs if and only if the perturbation energy exceeds the ridge height.

### 2.3 Metastable Corridor ($\mathcal{C}_M$)
A **Metastable Corridor** is a narrow "valley" in the landscape that connects two stable states, allowing for admissible transition without basin collapse.
- **Topology:** A path $P \subset U$ where $S_{achieved} > 0$ for all points along the path.

## 3. Basin Geometry Metrics

### 3.1 Basin Curvature ($\kappa_B$)
Measures the sharpness of the transition ridge.
- **Sharp Ridges:** Correlate with first-order abrupt transitions (Patch 024).
- **Soft Ridges:** Correlate with smooth degradation or continuous drift.

### 3.2 Basin Depth ($D_B$)
The magnitude of the admissibility barrier.
- **Deep Basins:** High resilience ($S_R$), high $S_C$.
- **Shallow Basins:** Low resilience, vulnerable to noise.

## 4. Formal Topology Binding
Persistence in MT-LAW-A requires that the local orientation array {-(i)} remains "trapped" within the connected component of the current metastable basin $B_M$. Fracture occurs when the component topology changes (Betti-0 expansion).

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-032
- **Deliverable ID:** docs/math/mt_law_a_metastable_basin_geometry.md
- **Status:** GEOMETRY_FRAMEWORK_ESTABLISHED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
