# MT-LAW-A: Stability Quantity Definition (S_C and Disambiguation)

## 1. Purpose
This document formalizes the disambiguation of "stability" into three distinct quantities required for the TS4 hardening of **MT-LAW-A (Bounded Continuation Persistence)**. Historically, "stability" has been used loosely to refer to both the *state* of persistence and the *resilience* of that state. This patch separates these into operational metrics to enable precise boundary testing.

## 2. Disambiguated Quantities

### 2.1 Stability-Achieved ($S_{achieved}$)
**Role:** Observable State.
**Definition:** The current magnitude or fraction of a continuation channel that remains admissible and coherent over time.
- **Metric:** `active_fraction`, `persistence_duration`.
- **Description:** Measures "Is it stable now?" but does not predict future resilience.
- **Reference Law:** LAW012 (Lawlike Persistence Channel).

### 2.2 Stabilization-Pressure ($P_{stab}$)
**Role:** Maintenance Condition / Driver.
**Definition:** The active forcing magnitude (epsilon-injection) or selection pressure (LAW014) applied to the update rule to sustain the channel.
- **Metric:** `epsilon_mean`, `selection_pressure_intensity`.
- **Description:** Measures "What is holding it open?"
- **Reference Law:** LAW014 (Channel Competition and Selection).

### 2.3 Cost-to-Destabilize ($S_C$)
**Role:** Resilience Threshold / Capacity.
**Definition:** The minimum perturbation magnitude or admissible budget cost required to force a stable channel into fracture, collapse, or transition.
- **Metric:** `s_crit`, `fracture_threshold`.
- **Description:** Measures "What will it take to break it?"
- **Reference Law:** LAW021 (Budget), LAW022 (Perturbation Resilience).

## 3. Formal Definition of $S_C$ (Cost-to-Destabilize)

The Cost-to-Destabilize $S_C$ for a given channel $\alpha$ is defined as the infimum of adversarial perturbation magnitudes that result in a transition to an inadmissible state:

$$S_C(\alpha) = \inf \{ |P_{adv}| : \Pi_A(\Delta x + P_{adv}) = \emptyset \text{ or } \text{residue collapse occurs} \}$$

### 3.1 Relationship to Admissibility Budget ($B_A$)
Under **LAW021 (Finite Admissibility Budget)**, $S_C$ is constrained by the available local budget. A channel consumes budget to damp perturbations ($P_{adv}$); once the budget $B_A$ is exhausted, the cost to destabilize falls to zero, and any nonzero perturbation will trigger a transition (LAW027).

### 3.2 Resilience and LAW022
Resilience is the operational capacity of the process to maintain $S_{achieved} \approx 1$ as $|P_{adv}|$ approaches $S_C$. Unlike global permanence, $S_C$ is a local, bounded, and potentially depletable property of a continuation regime.

## 4. Interaction Dynamics

The persistence of a structure can be modeled as a balance between these quantities:

1. **Maintenance:** $P_{stab}$ drives the continuation.
2. **Current State:** $S_{achieved}$ represents the success of that drive.
3. **Threshold:** $S_C$ represents the margin of safety against external noise or internal drift.

**Failure Boundary:** Persistence fails when the cumulative perturbation load (integrated over time or magnitude) exceeds the local Cost-to-Destabilize $S_C$.

## 5. Implementation Guidance for MT-LAW-A-TS4
- All TS4-candidate simulations MUST report $S_C$ through a controlled perturbation sweep (FV-2).
- Claims of "stability" MUST specify whether they refer to $S_{achieved}$, $P_{stab}$, or $S_C$.
- The term "stability" without qualification is deprecated for TS4+ proof work.

---
## Metadata
- **Patch ID:** MT-LAW-A-TS4-002
- **Deliverable ID:** docs/math/mt_law_a_stability_quantity_definition.md
- **Status:** INITIAL_DRAFT
- **Binding:** [PCD_STABILITY_QUANTITY_REGISTRY](../registry/math/stability_quantity_registry.json)
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
