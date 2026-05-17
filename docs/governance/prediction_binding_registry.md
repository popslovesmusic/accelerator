# Prediction Binding Registry (MPF-DATA-MATH-002)

## 1. Purpose
Define the authoritative connections between restricted mathematical structures (families and operators) and observable analog signatures in external data. This registry prevents post-hoc narrative fitting by requiring pre-declared predictions and explicit falsification conditions.

## 2. Binding Structure
Each entry in the `prediction_binding_registry.json` must include:
- **math_family**: The relevant law family (e.g., `LF-001`).
- **operator_basis**: The irreducible operators generating the signature.
- **predicted_signature**: Qualitative or quantitative description of the expected behavior.
- **observable_proxy**: The measurable metric used to detect the signature.
- **null_model**: The baseline against which the signature is compared.
- **falsification_condition**: The specific result that would constitute a failure of the prediction.

## 3. Governance Rule
Analysis campaigns are prohibited from interpreting dataset support for a math structure without an active entry in this registry.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
