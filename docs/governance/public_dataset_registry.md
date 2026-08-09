# Public Dataset Registry (MPF-DATA-MATH-003)

## 1. Purpose
Catalog and govern the admissible public and synthetic datasets used in evidence campaigns. This registry ensures strict provenance tracking, license compliance, and clear scoping of analysis boundaries for every data source.

## 2. Dataset Metadata
Each entry in the `public_dataset_registry.json` must include:
- **provenance_status**: Verification level of the data source (`VERIFIED`, `UNVERIFIED`, `RESIDUE`).
- **dataset_domain**: The restricted domain of the data (e.g., `synthetic_analog`, `astrophysical_proxy`).
- **allowed_analysis_scope**: Constraints on how the data may be used (e.g., `STRICTLY_LOCAL`).
- **associated_prediction_bindings**: Explicit links to the `prediction_binding_registry.json`.

## 3. Governance Rule
Datasets without 'VERIFIED' status are restricted to exploratory (C1-C2) evidence levels.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
