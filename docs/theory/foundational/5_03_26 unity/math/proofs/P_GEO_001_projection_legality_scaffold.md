# Proof Artifact: Pi_geo Projection Legality Scaffold

**Proof ID:** P_GEO_001
**Lemma ID:** GEO_LEMMA_001
**Target:** Projection Legality Lemma
**Classification:** LOCAL_LEMMA
**Status:** FORMAL_PROCEDURAL_ONLY

## 1. Lemma Statement
For any admissible topology input `T`, a candidate projection
$$
\Pi_{\mathrm{geo}} : \mathrm{Topology\_app} \to \mathrm{Geometry\_app}
$$
is lawful for provisional downstream handling only if distinction class, admissibility status, orientation traceability, and closure traceability remain preserved or recoverably retained under the declared projection map.

## 2. Scope Boundary
This artifact does **not** prove physical realism, metric completeness, spacetime derivation, or downstream application promotion. It states only the bounded legality conditions required for a governed topology-to-geometry projection inside the Mono-Process Framework.

## 3. Formal Skeleton
* **Let** `T` be a lawful `Topology_app` structure with non-empty admissible continuation.
* **Let** `Pi_geo(T) = G` be a declared `Geometry_app` projection candidate.
* **Assume** `L099` defines the legality invariants for `Pi_geo`.
* **Assume** `L100` blocks promotion unless those invariants are retained and paired with a recoverable validation path.
* **Assume** `OPEN_BRIDGE_001` is supported only as a structural/topological selector and therefore cannot certify downstream interpretation from projection alone.
* **Then** `Pi_geo` is lawful only when the declared invariant set remains preserved or traceably recoverable in `G`.

## 4. Structural Preservation Steps

**Step 001: Fix the projection layer.**
`Pi_geo` is a projection from `Topology_app` into `Geometry_app`, not a primitive ontology switch. By `L045`, both sides remain projections of the same recursive process rather than independent first principles.

**Step 002: Preserve distinction class.**
If two admissible topology structures `A` and `B` satisfy `D_topology(A|B) > 0`, then legality requires the projection to avoid total distinction collapse:
$$
D_{\mathrm{geometry}}(\Pi_{\mathrm{geo}}(A)|\Pi_{\mathrm{geo}}(B)) > 0.
$$
Otherwise the map erases governed structural differences and cannot count as a lawful continuation.

**Step 003: Preserve admissibility status.**
If `P_adm(T) = 1`, then legality requires:
$$
P_{\mathrm{adm}}(\Pi_{\mathrm{geo}}(T)) = 1.
$$
If the projection generates illegal geometry from admissible topology, the map violates the admissibility corridor rather than expressing it.

**Step 004: Preserve orientation traceability.**
If `Class_orient(T)` is declared on the topology side, then a lawful projection must retain or recoverably encode the corresponding orientation class on the geometry side. A map that smooths away orientation selectors without a governed recovery path fails the legality gate.

**Step 005: Preserve closure traceability.**
If `Closure(T)` is declared, then legality requires closure identity to survive projection unless a separate governed operator explicitly accounts for the transformation. Unexplained closure destruction is therefore a blocking failure.

**Step 006: Apply the hardening gate.**
`L100` converts these preservation conditions into a promotion barrier. Even if a geometric image is visually expressive or analytically convenient, no downstream `field_app`, `matter_app`, or bridge interpretation is admissible unless the preservation steps above remain satisfied.

**Step 007: Bind empirical checking without overclaiming proof.**
`GEO_PROJECTION_VALIDATION_001` is the attached campaign for measuring loss rates and recoverability. The campaign can support or weaken confidence in a candidate `Pi_geo`, but campaign attachment does not by itself complete proof discharge.

## 5. Required Failure Analysis
* **FAIL_GEO_001 (distinction collapse):** Distinct admissible topology classes become geometrically indistinguishable.
* **FAIL_GEO_002 (admissibility violation):** An admissible topology input projects into illegal geometry.
* **FAIL_GEO_003 (orientation loss):** Orientation class becomes unrecoverable under the declared projection.
* **FAIL_GEO_004 (closure loss):** Closure identity is destroyed without a separate governed explanatory operator.
* **FAIL_GEO_005 (projection-to-physics escalation):** Geometric expressiveness is treated as physical interpretation or bridge promotion without satisfying the legality gate.

## 6. Discharge Conditions
`PO-GEO-001` can advance beyond `open` only when all of the following are satisfied:
1. `Pi_geo` is explicitly bound in the observable projection registry.
2. The invariant set is declared identically across `L099`, `L100`, and the obligation registry.
3. A bounded argument shows each failure mode is blocked by the legality conditions rather than hidden by language.
4. `GEO_PROJECTION_VALIDATION_001` remains attached as the empirical check for measured retention.

## 7. Conclusion
This scaffold establishes the local proof shape for `GEO_LEMMA_001`: topology-to-geometry projection is lawful only when governed invariants survive the map in a traceable way. The result remains restricted to `FORMAL_PROCEDURAL_ONLY` and does not promote physical or bridge-level claims.
