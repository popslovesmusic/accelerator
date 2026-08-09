# MT-LAW-A: Threshold Geometry Mapping (Patch 012)

## 1. Purpose
This document establishes the formal geometric representation of the **Cost-to-Destabilize ($S_C$)** threshold for **MT-LAW-A (Bounded Continuation Persistence)**. Following the FV-2 verification, this patch maps the persistence boundary as a multi-parameter surface in Forcing-Coupling ($s$-$\kappa$) space.

## 2. Parameter Space Topology

We mapped the response of the **Structural Box (PDE)** mechanism across a 2D grid:
- **Forcing ($s$):** $[0.01, 0.40]$ (Stabilization Pressure).
- **Coupling ($\kappa$):** $[0.10, 1.00]$ (Coupling Reach).

### 2.1 Observed Persistence Surface ($S_{achieved}$)
The mapping revealed that within the tested regime, structural persistence is primarily driven by the forcing magnitude ($s$), with high resilience across the coupling ($\kappa$) range:

| Forcing ($s$) | Mean Active Fraction | Interpretation |
| :--- | :--- | :--- |
| 0.01 | 0.316 | Sparse Persistence |
| 0.10 | 0.355 | Stable Channel |
| 0.20 | 0.433 | Expanded Continuity |
| 0.40 | 1.000 | Global Saturation (Budget Limit) |

### 2.2 Boundary Geometry
The $S_C$ boundary in this mechanism class behaves as a **First-Order Saturation Surface**. 
- **Sharp Transition:** At $s \approx 0.40$, the local admissibility basin undergoes a global transition to total saturation (100% active).
- **Coupling Invariance:** For $\kappa > 0.1$, the coupling strength does not significantly shift the $s$-driven threshold, suggesting that the "Locking" boundary (CE-A002) is not reached in this parameter volume.

## 3. Mathematical Formalization of the Surface

The stability surface $\Omega_S$ is defined as the subset of parameter space where $S_{achieved} \in (0, 1)$:

$$\Omega_S = \{ (s, \kappa) : 0 < \text{ActiveFraction}(s, \kappa) < 1.0 \}$$

- **Lower Boundary:** $s < 0.01$ (Transition to extinction).
- **Upper Boundary:** $s \ge 0.40$ (Transition to saturation/avalance).

## 4. Stability Boundary Points (Estimated)
Based on the mapping, the "Restricted Domain" for MT-LAW-A persistence is bounded by:
- **Max Forcing:** $S_C^{max} \approx 0.40$.
- **Min Forcing:** $S_C^{min} \approx 0.00$ (Persistence vanishes without $P_{stab}$).

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS4-012
- **Deliverable ID:** docs/math/mt_law_a_threshold_geometry_mapping.md
- **Status:** INITIAL_MAPPING_COMPLETE
- **Math Registry:** [PCD_STABILITY_QUANTITY_REGISTRY](../registry/math/stability_quantity_registry.json)
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
