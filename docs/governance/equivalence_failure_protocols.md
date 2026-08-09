# Failure-First Equivalence Protocols (MPF-ACELL-EQUIV-005)

## 1. Purpose
Mandate the preservation and indexing of failed implementation-equivalence runs as first-class evidence. These failures define the boundaries of implementation robustness and provide critical information for drift detection and rigor endorsement gating.

## 2. Failure Classes
The following failure types must be recorded and indexed:
- **metric_divergence**: Numerical difference exceeding defined tolerances.
- **tolerance_breach**: Specific seed/config combinations that fail.
- **phase_drift**: Divergence in emergent behavior classification.
- **seed_instability**: Numerical sensitivity across backends.
- **nondeterminism**: Lack of bit-identity across identical runs (where required).
- **optimization_mutation**: Semantic changes introduced by performance tuning.

## 3. Protocol
1. **Detect**: Implementation divergence detected during equivalence campaign.
2. **Archive**: Full output data, config, and binary hashes of the failed run archived in `outputs/audits/equivalence/failures/`.
3. **Index**: Record the failure in `registry/equivalence_failure_registry.json`.
4. **Govern**: Failure blocks rigor endorsement upgrade to C4 until a mitigation or tolerance update is formally approved.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
