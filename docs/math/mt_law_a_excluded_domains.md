# MT-LAW-A: Bounded Continuation Persistence Excluded Domains

## Purpose
This document establishes the **Excluded Domain Taxonomy** for the **Bounded Continuation Persistence Lemma (MT-LAW-A)**. It provides a machine-traceable mapping of regions where the restricted-domain lemma candidate does not apply. These exclusions ensure that persistence claims are never misread as covering unresolved instabilities, divergent mechanisms, or counterexample-active zones.

## Excluded Domain Taxonomy

### 1. Budget Overflow Domain (ED-A001)
- **Exclusion Condition**: $C_A > B_{local}(\alpha)$.
- **Reason**: The operational cost of continuation exceeds the locally admissible budget.
- **Blocked Claim**: Unbounded budget persistence.
- **Required Signature**: `ERR_BUDGET_EXCEEDED`.

### 2. Topology Severance Domain (ED-A002)
- **Exclusion Condition**: $T_{access} \le \theta_{access}$ (Severance threshold).
- **Reason**: Regional coherence is lost due to orientation-array fragmentation.
- **Blocked Claim**: Non-local reachability under fragmentation.
- **Required Signature**: `ACCESS_SEVERED`.

### 3. Unbounded Reconstruction Divergence Domain (ED-A003)
- **Exclusion Condition**: $R_{divergence} > \epsilon_{crit}$.
- **Reason**: History recovery fidelity is too low to distinguish persistent structures from noise.
- **Blocked Claim**: Perfect history recovery or unique persistence under ambiguity.
- **Required Signature**: `HISTORY_AMBIGUITY`.

### 4. Identity Fragmentation Domain (ED-A004)
- **Exclusion Condition**: $I_{continuity}$ splits into non-equivalent branches.
- **Reason**: The continuity class fails to stabilize, and multi-branch ambiguity emerges.
- **Blocked Claim**: Absolute identity preservation without branch visibility.
- **Required Signature**: `BRANCH_AMBIGUITY`.

### 5. Oscillatory Non-Stabilization Domain (ED-A005)
- **Exclusion Condition**: Continuation remains active but fails bounded stabilization criteria.
- **Reason**: Active process recurrence without convergence to a basin or channel.
- **Blocked Claim**: Active continuation implies structural persistence.
- **Required Signature**: `CONVERGE_FAIL`.

### 6. Cross-Mechanism Divergence Domain (ED-A006)
- **Exclusion Condition**: Independent mechanism classes disagree beyond declared tolerance.
- **Reason**: Obsvational structural robustnes is not yet verified in this parameter region.
- **Blocked Claim**: Universal mechanism independence.
- **Required Signature**: `CROSS_MECH_DIVERGENCE`.

## Governance Constraints
- **Preserve Failure**: Excluded domains must remain explicitly mapped and visible.
- **No Early Discharge**: Exclusions represent active logical boundaries that must not be "smoothed over" to simplify proofs.
- **Strictly Local**: Claims are restricted to the complement of these excluded domains.

## Status Footer
- **Proof Status**: TS3_excluded_domain_mapping
- **Theorem Status**: NOT_PROVEN
- **Scope Status**: STRICTLY_LOCAL_RESTRICTED_DOMAIN
- **Physics Status**: NON_PHYSICAL_ANALOG_MODEL

---
[Back to Master Index](codex_master_index.md)
