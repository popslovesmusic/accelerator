# Bridge Inventory Report

Report: `BRIDGE_INVENTORY_20260731_001`  
Claim ceiling: `C1_MODEL_RELATIVE`  
Repository commit: `f05311712357b55b6e9d6189bab55d443c07e885`  
Worktree: dirty; unrelated pre-existing changes were not modified.

## Scope and source precedence

This is a read-only inventory of bridge records across active mathematical registries, lexicon records, the lexicon gap queue, and preserved induction/intake queues. Active canonical registries take precedence over generated summaries and historical material. Queue entries are included, but they remain non-canonical unless their source records explicitly say otherwise.

## Active governed bridges

The mathematical open-bridge registry contains six records:

| ID | Bridge | Recorded status |
|---|---|---|
| `OPEN_BRIDGE_001` | Orientation-Closure Bridge (Topological Selection) | `SUPPORTED` |
| `OPEN_BRIDGE_001_v2` | Orientation-Closure Bridge (Induced Alignment) | `SUPPORTED` |
| `OPEN_BRIDGE_001_v3` | Orientation-Closure Bridge (Procedural Model) | `SUPPORTED` |
| `OPEN_BRIDGE_AE_OVERLAP_001` | Affect-Effect Quantitative Projection Bridge | `PROVISIONAL_FORMAL_DEFINITION` |
| `OPEN_BRIDGE_002` | Typed-Zero Provenance | `PROVISIONALLY_FORMALIZED_PENDING_VALIDATION` |
| `OPEN_BRIDGE_003` | Cross-Domain Continuation Trace | `PROVISIONALLY_FORMALIZED_PENDING_VALIDATION` |

`SUPPORTED` is the registry status; it is not an unrestricted external or physical claim. The affect-effect, typed-zero, and cross-domain records remain provisional or validation-pending as recorded.

## Bridge-related lexicon queue

Thirteen entries in `registry/lexicon_gap_queue.json` contain bridge-related source, alias, definition, or governance text:

`affect_effect_distinction_projection`, `rate_type_eligible`, `propagation_position`, `non_realizability_of_decoupled_endpoints`, `semantic_metric_bridge`, `bridge_operator`, `distinction_propagation`, `reference_relative_representation_map`, `reference_relative_projection_bridge`, `affect_effect_overlap_measure`, `compressed_affect_effect_squared_overlap`, `directional_relational_amplitude`, and `generic_topology_feature`.

The first five are recorded as `RESOLVED_TO_CANONICAL` but retain `PROVISIONAL` claim status. The remaining entries are `C1_DEFINED_PROVISIONAL` or equivalent provisional records with no promotion beyond their recorded governance status. Full machine-readable provenance, queue indexes, source references, and statuses are in the JSON report.

## Preserved induction queue

The report includes all current queue entries whose preserved intake metadata explicitly identifies a bridge:

1. `IQ_2026_07_30_046` — `RT_GR_BRIDGE_TRIANGLE_CLOSURE_RESIDUE_CAT_INDUCTION_20260730_001`: queued, not reviewed, `HOLD_C1`, non-canonical candidate; CAT label unresolved.
2. `IQ_2026_07_27_045` — `RT_GR_BOUNDED_SYMMETRY_EXTENSION_BRIDGE_INDUCTION_20260727_001`: intake record remains not reviewed, `HOLD_C1`, non-canonical candidate; no matching live governance-queue record was found.
3. `IQ_2026_07_14_010` — `RT_PROCESS_SEMANTIC_INDEX_001`: included because its queued lexicon family explicitly links `semantic_metric_bridge`; canonical binding remains pending.

These entries are preserved evidence of induction state, not active mathematical definitions.

## Dependencies, blockers, and limits

The bridge dependency registry states that downstream claims of an unresolved bridge cannot be promoted above the bridge’s current claim level. Pending work includes bridge proof/validation obligations, typed-zero recoupling validation, cross-domain continuation validation, executable projection semantics, and review of queued candidates.

This report does not establish universal validity, physical correspondence, proof closure, semantic equivalence between bridge terms, or executable completeness. It also does not promote or mutate any canonical registry.

## Recommended next action

Review the two `HOLD_C1` bridge inductions in Analysis Intake, then reconcile the 13 lexicon-gap entries to their canonical source artifacts while preserving their current claim ceilings. Keep that review separate from theorem promotion and external physical interpretation.

Machine-readable detail and source hashes: [bridge_inventory_20260731_001.json](/D:/projects/acellorator/departments/analysis/crawl_reports/bridge_inventory_20260731_001.json)
