# Topology-Geometry Hardening Registry Sync Audit

## Scope
This audit maps the current `Topology_app -> Geometry_app` hardening work against the authoritative registry layer and identifies remaining synchronization gaps. It does not promote theorem status, bridge status, application status, or physics claims.

## Source Artifacts Used
- **Current evidence**: `docs/theory/foundational/5_03_26 unity/math/lemmas/L100_topology_geometry_hardening_gate.md`
- **Current evidence**: `docs/theory/foundational/5_03_26 unity/math/campaigns/GEO_PROJECTION_VALIDATION_001_design.md`
- **Current evidence**: `docs/math/open_questions_map.md`
- **Current evidence**: `docs/math/projection_induced_geometry_governance.md`
- **Current evidence**: `docs/textbook/mono_process_textbook_complete.md`
- **Current evidence**: `registry/formal_objects/formal_object_registry.json`
- **Current evidence**: `registry/math/proof_obligation_registry.json`
- **Current evidence**: `registry/math/theorem_status_registry.json`
- **Current evidence**: `registry/math/dependency_graph_registry.json`
- **Current evidence**: `registry/math/observable_projection_registry.json`
- **Current evidence**: `registry/evidence_campaign_template_registry.json`

## Directly Observed
1. `formal_object_registry.json` already contains `OBJ-OP-PI-GEO` and `OBJ-L099`.
2. `formal_object_registry.json` does not currently contain a formal object entry for `L100`, `GEO_LEMMA_001`, `GEO_PROJECTION_VALIDATION_001`, or `Topology_to_Geometry_Hardening`.
3. `evidence_campaign_template_registry.json` already contains a template entry for `GEO_PROJECTION_VALIDATION_001`.
4. `proof_obligation_registry.json` currently contains obligations for `MT-001`, `MT-002`, `MT-003`, `MT-ART-001`, `MT-O-CALC-001`, `MT-OTIMES-001`, and `MT-IFFS-001`, but no obligation for projection legality or topology-to-geometry hardening.
5. `theorem_status_registry.json` contains `OPEN_BRIDGE_001`, `TC_asym`, and `gravity_app`, but no explicit status record for `geometry_app`, `field_app`, `matter_app`, `L099`, `L100`, or `GEO_PROJECTION_VALIDATION_001`.
6. `observable_projection_registry.json` is still minimal and does not yet encode a governed `Topology_app -> Geometry_app` projection record for `Pi_geo`.
7. `dependency_graph_registry.json` does not currently include nodes or edges for `L099`, `L100`, `GEO_PROJECTION_VALIDATION_001`, `Topology_to_Geometry_Hardening`, `geometry_app`, `field_app`, or `matter_app` as explicit topology-geometry hardening dependencies.
8. Superseded status note: this audit originally recorded a disagreement between `dependency_graph_registry.json` and `theorem_status_registry.json` for `OPEN_BRIDGE_001`. That disagreement was reconciled on 2026-07-20 by `MPF_OPEN_BRIDGE_001_STATUS_RECONCILIATION_2026_07_20`: the theorem-status registry now records `OPEN_BRIDGE_001` as `SUPPORTED` with `C1_structural_supported` scope. Downstream application and theorem claims remain independently gated.
9. The living textbook is now aligned to the stricter reading:
   - `Topology_app -> Geometry_app` remains `PROJECTION_LEGALITY_REQUIRED`
   - `matter_app` and `field_app` are not automatically promoted
   - `Pi_geo` remains provisional pending legality retention and campaign evidence

## Inferred Inside Framework
The current highest-value synchronization task is not additional textbook prose. It is SSOT completion across the registry layer so that downstream status propagation is governed by machine-readable dependencies rather than narrative-only statements.

## External Resemblance
This resembles a documentation-registry drift problem in conventional research software projects, where the narrative layer has moved ahead of the authoritative metadata layer. This is an analogy only.

## What It Does Not Prove
- It does not prove `Pi_geo` is lawful.
- It does not prove `Topology_app -> Geometry_app` is solved.
- It does not authorize `field_app`, `matter_app`, `gravity_app`, or any physical interpretation.
- The original version of this audit did not resolve the `OPEN_BRIDGE_001` evidentiary status disagreement; the later reconciliation packet `docs/reports/open_bridge_001_status_reconciliation_2026_07_20.md` resolves that status surface as structural-only support.

## Failure Modes / Uncertainty
- If `formal_object_registry.json` is not the true controlling registry for new lemma/campaign objects, the proposed object insertions below may need rerouting.
- If `dependency_graph_registry.json` is stale relative to another hidden active graph, adding nodes there alone would not resolve the propagation gap.
- If the status mismatch for `OPEN_BRIDGE_001` is intentional residue rather than drift, forcing normalization could erase historical nuance.

## Required Registry Updates
1. `registry/formal_objects/formal_object_registry.json`
   - Add `OBJ-L100` for `L100 - Topology-Geometry Hardening Gate`
   - Add a formal object alias or binding for `GEO_LEMMA_001` pointing to `L100`
   - Add a campaign/simulation-binding object for `GEO_PROJECTION_VALIDATION_001`
   - Add an object for `Topology_to_Geometry_Hardening` if the project treats dependency gates as first-class governed objects

2. `registry/math/proof_obligation_registry.json`
   - Add a projection-legality obligation for `Pi_geo`
   - Bind the obligation to the invariant set already named in `L099` and `L100`: distinction, admissibility, orientation, closure

3. `registry/math/theorem_status_registry.json`
   - Add explicit status entries for `geometry_app`, `field_app`, and `matter_app` if they are intended to be governed application projections
   - Add a status record for `L100` and, if desired by registry design, for `GEO_PROJECTION_VALIDATION_001`
   - `OPEN_BRIDGE_001` active-status discrepancy resolved by `MPF_OPEN_BRIDGE_001_STATUS_RECONCILIATION_2026_07_20`

4. `registry/math/dependency_graph_registry.json`
   - Add node: `Topology_to_Geometry_Hardening`
   - Add node: `GEO_PROJECTION_VALIDATION_001`
   - Add node or edge bindings for `L099` and `L100`
   - Add REQUIRED edges from `geometry_app`, `field_app`, and `matter_app` to the hardening gate if that is the intended claim-cap behavior

5. `registry/math/observable_projection_registry.json`
   - Add a governed projection record for `Pi_geo : Topology_app -> Geometry_app`
   - Record retained information, loss accounting, and legality prerequisites

## Minimum Safe Resolution Order
1. Preserve the reconciled `OPEN_BRIDGE_001` status and do not propagate it automatically to downstream claims
2. Register `L100` and `GEO_PROJECTION_VALIDATION_001` as formal objects
3. Add the projection-legality proof obligation
4. Bind `geometry_app`, `field_app`, and `matter_app` to the hardening gate through the dependency graph
5. Expand the observable projection registry to include `Pi_geo`

## Governance Note
This audit is documentation-only. The required authoritative updates are outside the writable `docs/` scope used for this task and therefore remain pending implementation in the registry layer.
