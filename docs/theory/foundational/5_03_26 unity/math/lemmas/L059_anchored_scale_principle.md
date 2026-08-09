# L059 — Anchored Scale Principle

## Statement
Scale is not a primitive descriptor, geometric magnitude, or observer-independent metric within the Mono-Process Framework. Scale has procedural meaning only when measured relative to the locally stabilized orientation operator $-(i)$. The **Anchored Scale** $\sigma$ of a candidate continuation $y$ is defined as the relational distance between its mismatch $\varepsilon(y)$ and the local orientation direction $\omega$.

## Formal Representation
$$\sigma(y) = d(\varepsilon(y), \omega_\alpha)$$
where:
- $\omega_\alpha = -(i)_\alpha[\varepsilon_\alpha, R_\alpha]$ is the local orientation direction.
- $d(\cdot, \cdot)$ is the mismatch metric defined on the tangent structure of the process.

## Dependencies
- Definitions: `anchored_scale` ($\sigma$), `local_orientation` ($\omega$), `mismatch_metric` ($d$)
- Assumptions: No absolute geometric background or metric substrate exists.
- Prior lemmas: L058 (Orientation-Driven Ordering), L037 (Entity), L038 (Continuation Density).

## Proof sketch
1. In Strict Procedural Monism (SPM), all realized states are admissible images of lawful evolution.
2. Lawful evolution is shaped by the projection of the orientation operator $-(i)$ into the admissible tangent structure (L058).
3. If scale were primitive, it would require an absolute background independent of process. Since the NOT Axiom (2.1) and Admissibility (L057) restrict all states to process-local relations, primitive scale is inadmissible.
4. Scale must therefore be derived from the available relational primitives: deviation ($\varepsilon$) and orientation ($\omega$).
5. Measuring scale as the persistent alignment or departure of continuation relative to the orientation basin provides a local, procedural, and orientation-referenced metric.
6. A "large" scale structure corresponds to a continuation whose alignment with the orientation basin persists broadly across many updates ($\prec$).

## Status
simulated

## Proof Type
simulation_supported

## Evidence
- [Campaign Report](results/2026-05-23_run03_Procedural_Gravity_Scale_Campaign/data/campaign_report.json)
- Persistence Ratio: 0.974 (50 seeds, cross-model)

## Supersedes / Superseded-by
- **Supersedes:** None (New core principle).
- **Notes:** Grounded in the SPM TECH NOTE "Anchored Scale, Orientation-Constrained Evolution, and Gravity".
