# MT-LAW-A: Fracture Propagation Rule (Patch 043)

## 1. Purpose
This document formalizes the rules governing the movement of **Fracture Fronts** through the continuation topology of **MT-LAW-A**. It defines the conditions under which a local topological split propagates into adjacent regional structures.

## 2. The Fracture Front ($\mathcal{F}_{front}$)
A **Fracture Front** is the leading edge of a topological fracture surface $\mathcal{F}$ where $Betti\text{-}0$ transition is actively occurring.

### 2.1 Local Propagation Condition
A fracture front propagates from process $\alpha$ to neighbor $\beta$ if the transport mismatch injected by $\alpha$'s collapse exceeds the neighbor's local resilience.
$$ |NavT(\alpha_{collapsed} \to \beta)| \ge S_C(\beta) $$

### 2.2 Cascading Fracture
If the propagation condition is satisfied for multiple neighbors sequentially, the system enters a **Cascading Fracture** state. This is the dynamic mechanism underlying the **Regional Avalanche** mode.

## 3. Fracture Dampening
Propagation is halted if:
1. **Topological Dampening:** The fracture front reaches a regional basin with sufficient ridge-height ($S_C$) to absorb the mismatch pulse.
2. **Budget Replenishment:** Local budget $B_A$ is restored at a rate faster than the front's expansion, re-stiffening the admissibility manifold.

## 4. Formal Rule: Continuity of Split
The MT-LAW-A framework requires that once a fracture front is initiated, its trajectory must be tracked until it either terminates at a dampen-boundary or consumes the restricted domain $U$. No "silent" fracture termination is allowed.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-043
- **Deliverable ID:** docs/math/mt_law_a_fracture_propagation_rule.md
- **Status:** PROPAGATION_RULE_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
