# Topology Behavioral Distinctions (MPF-TOPO-DIST-001)

## 1. Purpose
This document establishes the categorical distinctions between core topology behaviors within the Mono-Process Framework. To maintain mathematical and governance precision, it is mandatory to prevent the "structural collapse" of these distinct categories. Each distinction defines what a behavior IS and what it IS NOT, identifying the risks of confusing them.

## 2. Mandatory Distinctions

### 2.1 transition vs. reconfiguration
- **transition**: Changes topology state classification. For example, moving from a `local_region_expansion` state to a `local_region_contraction` state.
- **reconfiguration**: Rearranges internal relations within a fixed state classification. For example, `local_neighbor_rebinding` without changing the region's expansion/contraction status.
- **Key Difference**: Transition changes the *class*; reconfiguration rearranges the *content* of the class.

### 2.2 corridor vs. path
- **corridor**: A persistent, constrained admissibility structure. It defines the traversable "landscape" within a local domain.
- **path**: A specific traversal instance. It is the sequence of states or the active trajectory an agent or process takes through a corridor.
- **Key Difference**: Corridor is the *landscape*; path is the *journey*.

### 2.3 orientation vs. transport
- **orientation**: A local relational field that constrains admissibility directionality. It determines which continuations are preferred or "aligned."
- **transport**: Describes movement behavior. It is the active process of shifting state through defined paths.
- **Key Difference**: Orientation is the *constraint field*; transport is the *active dynamics*.

### 2.4 failure vs. invalidity
- **failure**: Bounded structural degradation. It occurs when topology relationships break down locally due to instability (e.g., `containment_shell_fracture`).
- **invalidity**: A violation of governance constraints. It occurs when an operation attempts to bypass mandates (e.g., a `global_topology_inference` attempt).
- **Key Difference**: Failure is a *structural event*; invalidity is a *governance breach*.

## 3. Mandatory Governance Status
All behavioral classifications must be explicitly marked with:
- **NOT_PROVEN**: Status is unverified.
- **STRICTLY_LOCAL**: Applies only to finite domains.
- **NON_PHYSICAL_ANALOG_MODEL**: No physical reality is implied.

---
[Back to Master Index](codex_master_index.md)
