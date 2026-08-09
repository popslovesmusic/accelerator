# Evidence Campaign Templates (MPF-EVID-CAMP-002)

## 1. Purpose
Create standardized campaign templates linking mathematical prediction structures to primary datasets, adversarial controls, and measurable proxies. These templates ensure that every evidence campaign is pre-structured for falsification rather than exploratory narrative fitting.

## 2. Template Structure
Each entry in the `evidence_campaign_template_registry.json` must include:
- **prediction_binding_id**: The pre-declared link to a math family and operator basis.
- **primary_dataset**: The main target for signature detection.
- **counterexample_dataset**: A structurally contrasting dataset where the signature should **NOT** appear.
- **null_model**: The baseline control (e.g., linear walk, uncoupled nodes).
- **falsification_vectors**: Mandatory adversarial checks (e.g., shuffle, ablation).

## 3. Governance Rule
Execution of a campaign is prohibited without a validated template that includes at least one adversarial control or counterexample dataset.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
