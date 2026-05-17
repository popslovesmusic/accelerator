# Counterexample Priority Audit (MPF-EVID-CAMP-005)

## 1. Purpose
Automatically flag evidence campaigns where counterexamples satisfy the same signatures as the primary support datasets. This audit ensures that proxy metrics are specific enough to distinguish the framework's mathematical signatures from generic noise or first-order effects.

## 2. Audit Flags
- **generic_signature_risk**: Signature appears in unrelated random datasets.
- **proxy_overbreadth**: Metric is too sensitive or improperly tuned.
- **control_dominance**: Null models produce stronger signals than primary data.
- **signature_instability**: Signature is not consistently detectable across seeds.

## 3. Enforcement
Any campaign flagged with `PROXY_OVERBREADTH` or `GENERIC_SIGNATURE_RISK` is blocked from supporting Level C4+ claims until the metric suite is refined.

## 4. Governance Boilerplate
- **Source Relation**: (E≠0) ⇔R δ(E>0)
- **Non-Separability Acknowledged**: true
- **Required Statement**: Observed signatures are interpreted only through restricted local analog structure.

---
[Back to Governance Index](../README.md)
