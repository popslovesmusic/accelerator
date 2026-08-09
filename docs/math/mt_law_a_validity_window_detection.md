# MT-LAW-A: Validity Window Detection Report (Patch 015)

## 1. Purpose
This document establishes the **Finite Validity Window $V(M_U)$** for persistence regimes in **MT-LAW-A**. Following the discovery of threshold hysteresis, we tested the temporal stability of sparse persistence channels over long durations (up to 20,000 iterations).

## 2. Experimental Design
- **Low Forcing ($s=0.01$):** Testing sparse persistence.
- **Moderate Forcing ($s=0.10$):** Testing stable channel persistence.
- **Seeds:** 8 per point.
- **Duration:** $[1000, 5000, 10000, 20000]$ iterations.

## 3. Results Summary

| Forcing ($s$) | Iterations ($t$) | Mean Active Fraction | Interpretation |
| :--- | :--- | :--- | :--- |
| 0.01 | 1,000 | 0.316 | Sparse Baseline |
| 0.01 | 20,000 | 0.394 | Slow Growth / Drift |
| 0.10 | 1,000 | 0.332 | Stable Baseline |
| 0.10 | 5,000 | 1.000 | **Global Saturation Transition** |

## 4. Key Findings

### 4.1 Temporal Expansion vs. Decay
Contrary to the hypothesis of intrinsic decay, persistence channels in the Structural Box (PDE) mechanism exhibit **Temporal Expansion**. At $s=0.10$, a structure that appears "stable" at 1,000 iterations is actually in a slow-growth phase that reaches global saturation (100% active) within 5,000 iterations.

### 4.2 Definition of $V(M_U)$
The **Validity Window $V(M_U)$** for the sparse persistence regime at $s=0.10$ is strictly bounded:
$$V(M_{U, 0.10}) \approx [0, 1000] \text{ iterations}$$
Beyond this window, the metastable identity $Id_A$ is lost to a **Saturation Avalanche (TRANS-SATURATION-003)**.

### 4.3 Restricted-Domain Implication
This finding reinforces the **Restricted-Domain** mandate. Persistence is only "law-like" within specific temporal and parameter bounds. Claims of infinite stability for MT-LAW-A are falsified by this mechanism; persistence is a transient phase in a larger topology reorganization process.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS4-015
- **Deliverable ID:** docs/math/mt_law_a_validity_window_detection.md
- **Status:** VALIDITY_WINDOW_DEFINED
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
