# L094 — Coarse-Graining Legality Bounds (The $\tau$ Criterion)

## Statement
The application of the coarse-graining operator $\Leftrightarrow_{xb}$ is only mathematically valid (**Legal**) when the micro-update density satisfies the **Homogenization Condition** relative to the scale threshold $\tau$. Coarse-graining is illegal if the variance of the procedural mismatch is high at the scale of the projection kernel $\mathcal{K}$:

$$ \text{Validity}(\Leftrightarrow_{xb}) \iff \frac{\text{Var}(\sum \delta_a)}{\text{Mean}(\sum \delta_a)} < \epsilon_{\tau} \quad \text{for } N > \tau $$

1. **Illegal Regime:** Below $\tau$, the system is dominated by discrete fluctuations; macro-projections are unstable or "fractured."
2. **Legal Regime:** Above $\tau$, the aggregate density stabilizes, allowing the projection of a continuous manifold (geometry_app).

## Dependencies
- Lemma L080 (Cross-Basin Projection)
- Lemma L092 (Projection Kernels)

## Proof Sketch
1. Projection is an averaging operation over a neighborhood (L092).
2. For an average to represent a stable "property" (like curvature), the sample size must be sufficient to suppress local noise.
3. The scale threshold $\tau$ defines this minimum sample size.
4. If coarse-graining is attempted prematurely ($N < \tau$), the resulting geometry_app will fail stability checks and cross-mechanism agreement tests.
5. This defines the boundary between the "Quantum-analog" ($N < \tau$) and "GR-analog" ($N > \tau$) regimes.

## Status
- **Status:** provisional
- **Proof Type:** heuristic
- **Endorsement:** Level C4 targeted

## Metadata
- **Codex Grounding:** LAW-005, LAW-031
- **Charter:** v2.3 — Claim Classification: Theoretical
- **Authority:** Mono-Process Framework Core Math Program. ∎
