# Recursive Stability Basin Classification (MPF-PF-015)

## 1. Purpose
This document establishes the **classification criteria** for local admissibility basins under recursive application of the Π_A projection operator and counterexample pressure. It differentiates between stable persistence and various modes of instability or exclusion, ensuring that proof candidates are only drawn from verified stable domains.

## 2. Basin Classes

### 2.1 RSB-STABLE: Stable Local Basin
- **Definition**: Repeated application of Π_A preserves the image $x \sim \Pi_A(x)$ across all test seeds and counterexample vectors within the local domain $D_L$.
- **Theorem Use**: May support restricted local proof steps.

### 2.2 RSB-METASTABLE: Metastable Local Basin
- **Definition**: Admissibility image is preserved for finite recursion depth $N$, but fails or enters instability beyond $N$ or under infinitesimal perturbation of the budget $B_A$ (LAW021).
- **Theorem Use**: Supports bounded evidence of persistence; cannot support proof closure.

### 2.3 RSB-OSCILLATORY: Oscillatory Basin
- **Definition**: The projection sequence $(\Pi_A)^n(x)$ enters a cycle between distinct images, none of which achieve idempotent stabilization.
- **Theorem Use**: Preserved as unresolved failure geometry (FG-A004).

### 2.4 RSB-SEVERED: Topology-Severed Basin
- **Definition**: The continuation structure $K$ disconnects under recursive application, making the boundary $\partial A$ inaccessible or the image $Im(\Pi_A)$ unreachable.
- **Theorem Use**: Formally classified as an excluded domain (ED-A002).

### 2.5 RSB-AMBIGUOUS: Identity-Ambiguous Basin
- **Definition**: The admissibility image persists, but the residue trace $R$ (LAW020) allows for multiple histories, breaking the uniqueness of the reconstructed process state.
- **Theorem Use**: Blocked from proof discharge (FG-A002).

## 3. Classification Process
1. **Load Campaign Logs**: Retrieve traces from the Pi_A Counterexample Injection Campaign (MPF-PF-013).
2. **Apply Rules**: Map each trace to one of the five basin classes based on budget status, boundary consistency, and failure geometry activation.
3. **Emit Summary**: Generate a machine-readable classification of the local domain.

## 4. Governance Footer
- **Theorem Status**: NOT_PROVEN.
- **Proof Status**: LTC_basin_classification_only.
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN.
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL.

---
[Back to Master Index](codex_master_index.md)
