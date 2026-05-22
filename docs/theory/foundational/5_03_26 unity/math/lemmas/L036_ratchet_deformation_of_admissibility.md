# L036 — Ratchet Deformation of Admissibility (The Knot Insight)

## Statement
Every operational selection event acts as a "ratchet" that leaves a trace (residue $R$), which deforms the future admissibility manifold of the process. This mechanism demonstrates the **Knot Insight**: identity emerges from recursive orientational locking within a single process (the rope organized knot-wise), not from the addition of new substance.

## Dependencies
- Definitions: `ratchet_event`, `residue` ($R$), `admissibility_manifold`, `knot_stabilization`
- Assumptions: Process is recursive and conditioned by its own history; "thingness" emerges from relational organization alone.
- Prior lemmas: L015 (Residue-Conditioned Closure v2)

## Proof (or Proof sketch)
1. A selection event $e_t$ occurs at time $t$ when $\Delta(x) \succcurlyeq \theta$.
2. This selection produces a residue $R_t = \Psi(R_{t-1}, e_t)$, which acts as an orientational lock.
3. The admissibility window $A_{t+1}$ is a function of the updated residue: $A_{t+1} = f(R_t)$.
4. Like a knot in a rope, the selection does not add substance but constrains future admissible continuation pathways.
5. Therefore, every discrete event "ratchets" the system by narrowing or shifting the domain of allowed future updates.
6. This recursive deformation is the mechanism by which "laws" and stable structures (entities) emerge as persistent basins in the admissibility manifold.

## Status
draft

## Supersedes / Superseded-by
Refines: L015 (adds geometric deformation language and knot metaphor)
