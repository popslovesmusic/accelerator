# Recoverable Equivalence Evidence Packets (MPF-ACELL-EQUIV-004)

## 1. Purpose
Standardize the evidence emitted during implementation-equivalence testing. These packets provide the recoverable proof that a high-performance engine (e.g., C++) produces numerically equivalent results to its governed reference baseline (e.g., Python) within declared tolerances.

## 2. Packet Components
- **Hashes**: Cryptographic hashes of tool binaries (`tool_hash`), reference sources (`reference_hash`), and simulation configs (`config_hash`) to ensure strict provenance.
- **Metric Suite**: Comparison of key observables (e.g., `residue_mean`) between implementations, including absolute and relative differences.
- **Seed Set**: The specific random seeds used for the comparison to enable perfect reproduction of results.
- **Failure Cases**: Explicit logging of any seeds or metrics that breached tolerances, preserved as first-class structural information.
- **Equivalence Verdict**: A final machine-readable status (`PASS`, `FAIL`, or `PARTIAL`).

## 3. Storage Mandate
Emitted packets MUST be saved in the `outputs/audits/equivalence/` directory and indexed in the `tool_manifest.json` for all C4+ certified tools.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true

---
[Back to Governance Index](../README.md)
