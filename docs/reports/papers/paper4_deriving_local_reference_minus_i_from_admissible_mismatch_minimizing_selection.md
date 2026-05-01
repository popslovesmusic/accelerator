# Deriving Local Reference -(i) from Admissible Mismatch-Minimizing Selection

## Signature Block

This work derives the local reference mechanism `-(i)` that Paper 3 assumes. The goal is not to introduce a new primitive object, but to define `-(i)` as an admissible *selection operator* forced by mismatch under nonzero continuation (`ℰ ≠ 0`). The manuscript is theory-first, but it includes a minimal operational probe using the existing weighted-graph prototype to demonstrate that `-(i)`-style selection/transport observables produce corridor, transition, and decoupling separation in code.

## Abstract

Paper 3 framed a relational geometry based on `ℰ ≠ 0`, defining geodesics as least-mismatch paths and curvature as the operational rate of failure of Geodesic Reference Alignment (GRA). That framework relies on a local reference `-(i)` but does not derive it. This paper supplies the missing derivation.

Paper 4 derives the local reference mechanism assumed in Paper 3 by defining `-(i)` as a locally selected admissible reference induced by mismatch-minimizing operator choice under nonzero continuation.

Starting from `ℰ ≠ 0 → continuation → mismatch`, we argue that coherent admissible continuation requires a local rule ordering admissible updates. We define an operator family `O = (L, Q)` where `L` is an admissibility operator and `Q` is an orientation operator, with admissibility preceding orientation. We then select minimizing operators `O*` by relational mismatch cost and define `-(i)` as the induced local reference (not the operator itself). In degenerate cases the minimizing set is non-unique, so `-(i)` is naturally set-valued, providing a disciplined account of local families of near-equivalent references.

We then show how transport residual `δ_T`, alignment divergence `Δ_align`, least-mismatch geodesics, and the curvature law `κ = d/ds Δ_align + λ δ_T` follow operationally once `-(i)` is defined. Finally, we cite a minimal governed weighted-graph prototype already present in the repository whose outputs separate corridor, shelf-transition, and decoupling regimes using exactly these observables.

## 1. Introduction and Gap Statement

Paper 3 introduced a relational geometry derived from `ℰ ≠ 0` and defined interaction structure through least-mismatch geodesics, reference co-transport, and GRA. In that framing, a local reference `-(i)` appears as a necessary ingredient, but it is treated as assumed.

This paper closes the main structural gap left by Paper 3. The earlier manuscript required a local reference `-(i)` in order to define co-transport, alignment, and operational curvature, but it did not yet derive that reference from the primitive framework. The present paper supplies that derivation by defining `-(i)` as the local reference induced by admissible mismatch-minimizing operator selection.

The intended deliverable is a disciplined, minimal definition. `-(i)` is not a coordinate axis, not a vector field, and not a globally fixed reference. It is a selection operator over admissible continuations that depends only on local mismatch and the local admissible operator set.

## 2. Primitive Constraint and Minimal Consequences

The primitive constraint is:

`ℰ ≠ 0`

Interpreted here as exclusion of terminal null resolution, this forces continuation. Continuation forces difference: if a system persists, it cannot be globally identical across all loci, times, or update legs without collapsing distinguishability. Therefore mismatch is unavoidable.

We denote the local mismatch state as `ε(x,t)` (or `ε(s)` along a path parameter `s`). The paper does not require a specific PDE or ODE for `ε`; it requires only that mismatch exists and evolves under admissible continuation rules.

The key step is then: once mismatch exists, the system must have a rule that determines which admissible continuation is preferred when multiple admissible updates are possible. That “preference” is not optional structure; it is the minimum required to make continuation under mismatch coherent.

## 3. Operator Family and Admissibility Skeleton

This paper reuses the minimal operator vocabulary already present in the notes:

- Admissibility operators: `L ∈ {+, -}`.
- Orientation operators: `Q ∈ {++, +-, -+, --}`.
- Combined admissible orientation operator: `O = (L, Q)`.

Two constraints are treated as part of the admissibility skeleton:

1. **Precedence**: admissibility (`L`) precedes orientation (`Q`).
2. **Compatibility**: the “two-leg” structure requires opposite-leg sign compatibility (stated axiomatically here; a closed algebra can be supplied later).

Define `𝒪_adm(x,t)` as the admissible operator set available at `(x,t)` after applying these constraints. The details of how `𝒪_adm` varies (globally fixed vs. locally restricted) can be treated as an implementation choice, but the manuscript requires that such a set exists.

## 4. Definition of `-(i)` via Admissible Selection

Let `μ_rel(·)` be a relational mismatch cost functional. The paper remains agnostic about its full form; it must only provide an ordering over candidate outcomes.

The framework requires a local rule that orders admissible continuations under mismatch. We define this rule in two stages. First, an admissible operator is selected by minimizing relational mismatch cost over the local admissible operator family. Second, the induced continuation reference is identified as `-(i)`. In this way, `-(i)` is derived as a local reference mechanism rather than introduced as a primitive object.

**Core definition (two-stage, but minimal)**:

`O*(x,t) ∈ argmin_{O ∈ 𝒪_adm(x,t)} μ_rel( O · ε(x,t) )`

Then define the local reference `-(i)` as the reference induced by the selected admissible operator acting on the local mismatch state:

`-(i)(x,t) := Ref( O*(x,t) · ε(x,t) )`

Here `O · ε` denotes the action of an admissible operator on the mismatch state in the minimal operational sense: it produces the candidate continuation outcome whose mismatch cost is evaluated by `μ_rel`. `Ref(·)` is an explicit reminder that `-(i)` is a *reference value* derived from the selected continuation, not the operator itself. `O*` denotes the minimizing admissible operator choice, while `-(i)` denotes the local reference induced by that choice; the two should not be identified.

### 4.1 Set-valuedness under degeneracy

If multiple admissible operators achieve the same minimal cost, then `argmin` returns a set of minimizers. Therefore `O*` is set-valued in degenerate cases, and consequently the induced reference can also be set-valued:

`-(i)(x,t) ∈ { Ref(O · ε(x,t)) : O ∈ argmin_{O ∈ 𝒪_adm(x,t)} μ_rel(O · ε(x,t)) }`

This is a feature, not a failure. It provides a disciplined way to represent local “families” of near-equivalent orientations (for example, near low-mismatch regimes) without introducing new primitives. Set-valuedness is not a technical exception but a structural feature of the framework: near-equivalent admissible continuations may induce a local family of references rather than a unique reference.

## 5. Properties Required Downstream

The framework only needs a small number of properties for `-(i)` to be usable in Paper 3’s geometry and interaction stack.

### 5.1 Locality

`-(i)(x,t)` depends only on local mismatch and the admissible operator set at `(x,t)`. No global coordinate frame is required.

### 5.2 Stability under smooth continuation (with boundary events)

If `ε(x,t)` evolves smoothly and the minimizer is isolated, `-(i)(x,t)` should change in a bounded way. Discontinuities are allowed at degeneracy boundaries where minimizers swap or bifurcate. This stability-with-events framing is sufficient to motivate transport: reference transport is meaningful precisely in regions where the selection is stable.

## 6. Transport and Transport Residual

To connect to Paper 3, define transport along a path parameter `s`. Let `T_{L/Q}` denote the admissible update rule induced by the local operator state `L/Q`. Then a minimal transport statement is:

`-(i)(s + ds) = T_{L/Q}( -(i)(s) )`

Since `-(i)` is defined by selection, transport can fail in two ways: the predicted continuation is not realized by the next selection, or degeneracy causes a minimizer switch. Both are operationally detectable by a transport residual:

`δ_T(s) = | actual(s+ds) - expected(s+ds) |`

where `expected(s+ds) = T_{L/Q}(actual(s))`. In practice, `actual` is the newly selected reference at the next step and `expected` is the reference predicted by transporting the prior reference under the admissible update rule.

This is the key quantity used later in the operational curvature law. Paper 4’s contribution is that `δ_T` is no longer an introduced measurement convenience; it is a forced diagnostic of selection instability.

Transport is meaningful only where local selection is sufficiently stable; transport residual therefore measures instability of the reference-selection mechanism itself, not merely path irregularity.

## 7. From `-(i)` to Geodesics

Once mismatch cost and admissible selection exist, least-mismatch paths are the natural candidates for geodesics. In Paper 3 language, geodesics minimize accumulated relational mismatch, not Euclidean distance.

Paper 4 reframes that: geodesics are the paths along which `-(i)` selection and transport remain coherent. Operationally, along a geodesic corridor, one expects both low accumulated mismatch and low transport residual `δ_T`.

Paper 3 introduced least-mismatch geodesics as operational paths. Paper 4 refines that picture by showing that such paths are precisely the corridors along which local reference selection and transport remain coherent.

## 8. Multi-`-(i)` Interaction and Alignment

For two basins or references `A` and `B` transported along a common path, define alignment divergence:

`Δ_align(s) = | -(i)_A(s) - -(i)_B(s) |`

Bounded `Δ_align` corresponds to compatibility (corridor formation); increasing `Δ_align` corresponds to strain (transition shelves); and divergence corresponds to decoupling.

This is the interaction layer that Paper 3 named GRA. Paper 4 makes explicit that it rests on the existence of `-(i)` as a selection operator and the stability of its transport.

## 9. Curvature Emerges from Selection and Transport Failure

Paper 3 introduced an operational curvature law:

`κ(s) = d/ds Δ_align(s) + λ δ_T(s)`

Paper 4’s upgrade is the dependency: `κ` is not an additional primitive. It emerges as the rate of breakdown of multi-reference alignment together with local selection/transport instability.

This positions curvature as a derived quantity measuring loss of relational consistency under admissible continuation, rather than a geometric input.

Under this reading, curvature is not an input geometry but a derived observable of reference-selection and transport breakdown.

## 10. Minimal Operational Probe (Existing Governed Prototype)

This manuscript includes a minimal operational probe using the existing weighted-graph prototype already present in the repository:

- Driver: `sim/scripts/run_paper2_relational_geodesic_prototype.py`
- Config: `sim/configs/paper2_relational_geodesic_prototype_v1.json`
- Canonical run artifacts: `artifacts/runs/paper2_relational_geodesic_prototype_v1_1/`
- Figure: `docs/manuscript/paper3/fig1_relational_geodesic_regimes.png`

The prototype is synthetic by design. Its purpose is to demonstrate that the definitions in Sections 4–9 can be implemented and that their observables separate corridor, transition, and decoupling in the intended order.

### 10.1 Prototype results table (from `scenario_summary.csv`)

| scenario_id | observed_regime | geodesic_cost | Δ_align_max | δ_T_mean | κ_mean | κ_max | hotspots | decoupling_events |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| corridor | corridor | 77.0926 | 0.0593 | 0.00756 | 0.0117 | 0.0380 | 0 | 0 |
| shelf_transition | shelf_transition | 93.7056 | 0.1506 | 0.0135 | 0.0297 | 0.0888 | 0 | 0 |
| decoupling | decoupling | 111.0217 | 0.2899 | 0.0211 | 0.0460 | 0.1483 | 4 | 6 |

These numbers do not validate the theory as physics. They do establish that the selection/transport/alignment observables are coherent enough to produce regime separation in code, which is the minimal requirement for downstream formal tightening and broader simulation work.

### 10.2 Full-field `O*` / `-(i)` computation (grid-wide)

Path-wise metrics are useful, but Paper 4’s central object is local: `-(i)(x,t)` is defined by an `argmin` at each locus. The repository therefore includes an explicit grid-wide selection probe:

- Driver: `sim/scripts/run_paper3_i_field_probe.py`
- Config: `sim/configs/paper3_i_field_probe_v1.json`
- Canonical run artifacts: `artifacts/runs/paper3_i_field_probe_v1_2/`
- Figure: `docs/manuscript/paper3/fig2_i_field_quiver.png`

This probe computes a proxy for `O*(x)` by evaluating a simple local cost over the discrete operator family `(L,Q)` and selecting the minimizer at every grid cell. The induced `-(i)` is represented as the selected direction angle (`i_angle_rad`) and visualized as a quiver field over the mismatch heatmap. This does not settle the final form of `μ_rel` or `O · ε`, but it demonstrates that the core definitional move (local argmin selection) can be computed as a field and inspected directly.

The same run also exports an explicit **degeneracy map**: the local count of near-tied minimizers (operators whose costs lie within a tolerance of the minimum). This is the operational handle for the claim that `-(i)` can be set-valued under degeneracy. The manuscript figure is `docs/manuscript/paper3/fig3_degeneracy_map.png`, and the per-cell values are written to `i_field.csv` as `degeneracy_count` and `mu_gap_to_second`.

The resulting fields show that `-(i)`-selection is not merely definable pointwise but organizes into coherent spatial structure whose deformation tracks the corridor-to-transition-to-decoupling ordering.

## 11. Limitations

- The operator family is specified as a minimal admissibility skeleton, not a complete algebra.
- `μ_rel` and `O · ε` are defined operationally; a stronger mathematical formalization remains future work.
- The stability property is argued as a requirement and an empirical expectation, not proven as a general theorem here.
- The included validation probe is synthetic and small; it demonstrates operational coherence, not physical truth.

## 12. Conclusion

Paper 4 supplies the missing derivation of the local reference `-(i)` assumed by Paper 3. Under `ℰ ≠ 0`, mismatch is unavoidable, and coherent admissible continuation requires a local selection rule. Defining `-(i)` as an admissible orientation-selection operator provides that rule while preserving locality and allowing set-valued behavior under degeneracy. Once `-(i)` exists, transport residuals, alignment divergence, geodesic corridors, and operational curvature follow as derived observables rather than introduced primitives.

The next step is not to widen the conceptual vocabulary, but to harden the operator semantics and preserve the same observable layer (`δ_T`, `Δ_align`, `κ`) as the framework is extended into richer lattice and PDE settings.
