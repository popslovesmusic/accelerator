# L036 — Ratchet Deformation of Admissibility

## Statement
Every operational selection event acts as a "ratchet" that leaves a trace (residue $R$), which deforms the future admissibility manifold of the process. Residue is not merely a record of the past, but an active deformation of the geometry of possible future continuations.

## Dependencies
- Definitions: `ratchet_event`, `residue` ($R$), `admissibility_manifold`
- Assumptions: Process is recursive and conditioned by its own history.
- Prior lemmas: L015 (Residue-Conditioned Closure v2)

## Proof (or Proof sketch)
1. A selection event $e_t$ occurs at time $t$ when $\Delta(x) \succcurlyeq \theta$.
2. This selection produces a residue $R_t = \Psi(R_{t-1}, e_t)$.
3. The admissibility window $A_{t+1}$ is a function of the updated residue: $A_{t+1} = f(R_t)$.
4. Therefore, every discrete event "ratchets" the system by narrowing or shifting the domain of allowed future updates.
5. This recursive deformation is the mechanism by which "laws" and stable structures emerge as persistent basins in the admissibility manifold.

## Status
draft

## Supersedes / Superseded-by
Refines: L015 (adds geometric deformation language)
