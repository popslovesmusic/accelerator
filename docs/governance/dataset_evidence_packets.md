# Dataset Evidence Packets (MPF-DATA-MATH-006)

## 1. Purpose
Standardize the format and content of evidence emitted during dataset-analysis campaigns. These packets ensure that all empirical support for mathematical signatures is recoverable, auditable, and explicitly bounded by the framework's claim-humility rules.

## 2. Packet Components
- **dataset_id / prediction_binding_id**: Explicit links to the governed registries.
- **proxy_metrics**: The numerical results of the pre-declared Measurable Proxies.
- **falsification_results**: Mandatory report of pass/fail status for null models and controls.
- **support_verdict**: The machine-readable interpretation of the evidence (`STRONG`, `PARTIAL`, `NULL`, `FALSIFIED`).
- **claim_scope**: Hardcoded restriction to `STRICTLY_LOCAL_RESTRICTED_ANALOG`.

## 3. Storage Mandate
Every emitted packet MUST be archived in `outputs/audits/evidence_campaigns/` and include a valid cryptographic hash of the input dataset to ensure provenance.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
