# Tool Certification Registry (MPF-ACELL-EQUIV-006)

## 1. Purpose
Define and track the machine-readable certification state for all tools in the ecosystem. This registry ensures that tool capability is formally governed and that high-performance engines are not permitted to support scientific claims beyond their proven equivalence level.

## 2. Certification States
- **UNVERIFIED**: No validation evidence exists.
- **REFERENCE_BASELINE_ONLY**: Python reference tool with no performance equivalent.
- **EQUIVALENCE_PENDING**: Implementation exists but check is incomplete.
- **EQUIVALENCE_VERIFIED**: Implementation matches reference baseline.
- **CERTIFIED_C1**: Basic execution and output recovery verified.
- **CERTIFIED_C2**: Core scientific validity and mapping verified.
- **CERTIFIED_C3**: Cross-model validation and falsification verified.
- **CERTIFIED_C4**: High-rigor stable state with full equivalence and UQ.
- **CERTIFICATION_REVOKED**: Tool failed audit and is blocked.

## 3. Governance Rule
All research claims at Level C4 or higher MUST use tools with `CERTIFIED_C4` status in this registry.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
