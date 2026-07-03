# Master Work Index Bootstrap Audit

Status: PASS_WITH_MAPPING_GAPS

- Total indexed items: 76
- Source files scanned: 25
- Zero-item sources: 8
- Needs mapping: 1
- Source registry status changed: False

## Seed Coverage
- governance/live/induction_queue.json: represented
- registry/lexicon_gap_queue.json: represented
- registry/lexicon/lexicon_gap_queue.json: represented
- registry/human_arbitration_queue.json: represented
- registry/math/process_algebra_expansion_review_queue.json: represented

## Campaign Coverage
- registry/math/proof_elevation_campaign_registry.json: represented
- registry/math/mt_proof_elevation_campaign_registry.json: represented
- registry/math/mt_counterexample_campaign_registry.json: represented
- registry/p0_engine_c4_elevation_campaign.json: represented
- registry/governance/living_falsification_campaign_registry.json: represented
- campaigns/BOOK_CAMPAIGN_PHASE_01_MASTER.json: represented
- campaigns/MST001_RESOLUTION_FRONTIER_CAMPAIGN_V1.json: represented
- campaigns/PD_CG_ROOT_TRACE_FALSIFICATION_CAMPAIGN_V1.json: represented

## Not Normalized
- MST001_RESOLUTION_FRONTIER_CAMPAIGN_V1 [campaigns/MST001_RESOLUTION_FRONTIER_CAMPAIGN_V1.json]: needs_mapping -> missing status

## Zero-Item Sources
- governance/live/work_reduction_framework.json
- governance/live/debt_discharge_command.json
- governance/live/program_debt_discharge_command.json
- registry/lexicon/lexicon_gap_queue.json
- registry/human_arbitration_queue.json
- registry/governance/patches/DEBT_VALIDATOR_IMPORT_PATH_001.json
- registry/governance/patches/MPF_FORMAL_DEBT_RECONCILIATION_PASS_001.json
- registry/governance/patches/MPF_PROOF_DEBT_PRIORITIZATION_001.json

## Scope
The bootstrap creates a live master index as a projection of governed work items. Source registries remain authoritative and unchanged.

## Notes
- `governance/live/master_work_index.json` was regenerated from the live queues, campaigns, debt registries, and induction registry.
- Support-only files were scanned but not indexed as work items.
- `governance/live/work_reduction_framework.json` continues to serve as the routing framework for the projection.
